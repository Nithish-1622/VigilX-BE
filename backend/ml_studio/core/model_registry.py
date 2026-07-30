from __future__ import annotations

import json
import logging
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from ml_studio.config import ml_settings
from ml_studio.schemas.job import JobStatus, TrainingJob, TrainingConfig
from ml_studio.schemas.model import ModelStatus, RegisteredModel

logger = logging.getLogger(__name__)

# Thread lock to prevent concurrent registry corruption
_lock = threading.Lock()


# ─────────────────────────────────────────────────────────────────────────────
# Low-level file helpers
# ─────────────────────────────────────────────────────────────────────────────

def _read(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning("Registry file %s corrupted, returning empty: %s", path, exc)
    return {}


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Model Registry
# ─────────────────────────────────────────────────────────────────────────────

class ModelRegistry:
    """
    JSON-backed registry for fine-tuned models.
    Thread-safe — uses a module-level lock.
    File: registry/models.json
    """

    def __init__(self) -> None:
        self._path = Path(ml_settings.models_registry_file)

    def _load(self) -> dict[str, dict]:
        return _read(self._path)

    def _save(self, data: dict[str, dict]) -> None:
        _write(self._path, data)

    def create(self, model: RegisteredModel) -> RegisteredModel:
        with _lock:
            data = self._load()
            # Calculate domain version
            tenant_id = getattr(model, "tenant_id", "default") or "default"
            domain = (model.domain or "general").capitalize()
            existing_versions = [
                v.get("version", 1)
                for v in data.values()
                if (str(v.get("tenant_id", "default")) or "default") == tenant_id
                and str(v.get("domain", "")).lower() == domain.lower()
            ]
            next_version = (max(existing_versions) + 1) if existing_versions else 1
            model.version = next_version
            if not model.version_label:
                model.version_label = f"{domain}-v{next_version}"

            # Link predecessor if active exists for domain
            for entry in data.values():
                if (
                    entry.get("is_active")
                    and (str(entry.get("tenant_id", "default")) or "default") == tenant_id
                    and str(entry.get("domain", "")).lower() == domain.lower()
                ):
                    model.predecessor_model_id = entry.get("model_id")
                    break

            data[model.model_id] = model.model_dump(mode="json")
            self._save(data)
        return model

    def get(self, model_id: str, tenant_id: str | None = None) -> Optional[RegisteredModel]:
        data = self._load()
        entry = data.get(model_id)
        if entry is None:
            return None
        if tenant_id is not None:
            entry_tenant = (str(entry.get("tenant_id", "default")) or "default").strip() or "default"
            if entry_tenant != (tenant_id or "default"):
                return None
        return RegisteredModel(**entry)

    def list_all(self, tenant_id: str | None = None) -> list[RegisteredModel]:
        data = self._load()
        models: list[RegisteredModel] = []
        for entry in data.values():
            try:
                if tenant_id is not None:
                    entry_tenant = (str(entry.get("tenant_id", "default")) or "default").strip() or "default"
                    if entry_tenant != (tenant_id or "default"):
                        continue
                models.append(RegisteredModel(**entry))
            except Exception as exc:
                logger.warning("Malformed model registry entry: %s", exc)
        return sorted(models, key=lambda m: m.created_at, reverse=True)

    def get_active(self, tenant_id: str | None = None) -> Optional[RegisteredModel]:
        """Return the currently active model, or None."""
        for m in self.list_all(tenant_id=tenant_id):
            if m.is_active:
                return m
        return None

    def update(self, model_id: str, tenant_id: str | None = None, **fields) -> Optional[RegisteredModel]:
        with _lock:
            data = self._load()
            if model_id not in data:
                return None
            if tenant_id is not None:
                entry_tenant = (str(data[model_id].get("tenant_id", "default")) or "default").strip() or "default"
                if entry_tenant != (tenant_id or "default"):
                    return None
            data[model_id].update({k: (v.value if hasattr(v, "value") else v) for k, v in fields.items()})
            self._save(data)
            return RegisteredModel(**data[model_id])

    def deactivate_all(self, tenant_id: str | None = None) -> None:
        """Mark every model as inactive."""
        with _lock:
            data = self._load()
            for entry in data.values():
                if tenant_id is not None:
                    entry_tenant = (str(entry.get("tenant_id", "default")) or "default").strip() or "default"
                    if entry_tenant != (tenant_id or "default"):
                        continue
                entry["is_active"] = False
                entry["status"] = ModelStatus.READY.value
                entry["lifecycle_stage"] = "approved"
            self._save(data)

    def activate(self, model_id: str, tenant_id: str | None = None) -> Optional[RegisteredModel]:
        """Deactivate all models, then mark model_id as active and production."""
        activated_job_id: str | None = None
        deprecated_job_ids: list[str] = []
        with _lock:
            data = self._load()
            if model_id not in data:
                return None
            if tenant_id is not None:
                entry_tenant = (str(data[model_id].get("tenant_id", "default")) or "default").strip() or "default"
                if entry_tenant != (tenant_id or "default"):
                    return None
            activated_job_id = data[model_id].get("job_id")
            for mid, entry in data.items():
                if tenant_id is not None:
                    mid_tenant = (str(entry.get("tenant_id", "default")) or "default").strip() or "default"
                    if mid_tenant != (tenant_id or "default"):
                        continue
                if mid == model_id:
                    entry["is_active"] = True
                    entry["status"] = ModelStatus.ACTIVE.value
                    entry["lifecycle_stage"] = "production"
                    entry["activated_at"] = datetime.utcnow().isoformat()
                elif entry.get("status") == ModelStatus.ACTIVE.value:
                    entry["is_active"] = False
                    entry["status"] = ModelStatus.READY.value
                    entry["lifecycle_stage"] = "deprecated"
                    entry["deprecated_at"] = datetime.utcnow().isoformat()
                    dep_job_id = entry.get("job_id")
                    if dep_job_id:
                        deprecated_job_ids.append(dep_job_id)
            self._save(data)
            activated_model = RegisteredModel(**data[model_id])

        job_reg = JobRegistry()
        if activated_job_id:
            job_reg.update(activated_job_id, tenant_id=tenant_id, status=JobStatus.ACTIVE)
        for dep_job_id in deprecated_job_ids:
            old_job = job_reg.get(dep_job_id, tenant_id=tenant_id)
            if old_job and old_job.status == JobStatus.ACTIVE:
                job_reg.update(dep_job_id, tenant_id=tenant_id, status=JobStatus.COMPLETED)

        return activated_model

    def rollback(self, model_id: str, tenant_id: str | None = None) -> tuple[Optional[RegisteredModel], Optional[RegisteredModel]]:
        """
        Rollback from current model to its predecessor.
        Returns (current_model, restored_predecessor_model).
        """
        curr = self.get(model_id, tenant_id=tenant_id)
        if not curr or not curr.predecessor_model_id:
            return curr, None

        pred = self.get(curr.predecessor_model_id, tenant_id=tenant_id)
        if not pred:
            return curr, None

        # Activate predecessor
        restored = self.activate(pred.model_id, tenant_id=tenant_id)
        return curr, restored

    def deprecate(self, model_id: str, tenant_id: str | None = None) -> Optional[RegisteredModel]:
        """Mark model as DEPRECATED."""
        model = self.get(model_id, tenant_id=tenant_id)
        updated = self.update(
            model_id,
            tenant_id=tenant_id,
            lifecycle_stage="deprecated",
            is_active=False,
            deprecated_at=datetime.utcnow().isoformat(),
        )
        if model and model.job_id:
            job_reg = JobRegistry()
            job = job_reg.get(model.job_id, tenant_id=tenant_id)
            if job and job.status == JobStatus.ACTIVE:
                job_reg.update(model.job_id, tenant_id=tenant_id, status=JobStatus.COMPLETED)
        return updated

    def delete(self, model_id: str, tenant_id: str | None = None) -> bool:
        with _lock:
            data = self._load()
            if model_id not in data:
                return False
            if tenant_id is not None:
                entry_tenant = (str(data[model_id].get("tenant_id", "default")) or "default").strip() or "default"
                if entry_tenant != (tenant_id or "default"):
                    return False
            del data[model_id]
            self._save(data)
        return True
        return True


# ─────────────────────────────────────────────────────────────────────────────
# Job Registry
# ─────────────────────────────────────────────────────────────────────────────

class JobRegistry:
    """
    JSON-backed registry for training jobs.
    Thread-safe — uses a module-level lock.
    File: registry/jobs.json
    """

    def __init__(self) -> None:
        self._path = Path(ml_settings.jobs_registry_file)

    def _load(self) -> dict[str, dict]:
        return _read(self._path)

    def _save(self, data: dict[str, dict]) -> None:
        _write(self._path, data)

    def create(self, config: TrainingConfig, job_name: str, tenant_id: str = "default") -> TrainingJob:
        job = TrainingJob(
            job_id=str(uuid.uuid4()),
            tenant_id=tenant_id or "default",
            job_name=job_name,
            status=JobStatus.QUEUED,
            config=config,
            total_steps=config.max_steps,
            created_at=datetime.utcnow(),
        )
        with _lock:
            data = self._load()
            data[job.job_id] = job.model_dump(mode="json")
            self._save(data)
        return job

    def get(self, job_id: str, tenant_id: str | None = None) -> Optional[TrainingJob]:
        data = self._load()
        entry = data.get(job_id)
        if entry is None:
            return None
        if tenant_id is not None:
            entry_tenant = (str(entry.get("tenant_id", "default")) or "default").strip() or "default"
            if entry_tenant != (tenant_id or "default"):
                return None
        return TrainingJob(**entry)

    def list_all(self, tenant_id: str | None = None) -> list[TrainingJob]:
        data = self._load()
        jobs: list[TrainingJob] = []
        for entry in data.values():
            try:
                if tenant_id is not None:
                    entry_tenant = (str(entry.get("tenant_id", "default")) or "default").strip() or "default"
                    if entry_tenant != (tenant_id or "default"):
                        continue
                jobs.append(TrainingJob(**entry))
            except Exception as exc:
                logger.warning("Malformed job registry entry: %s", exc)
        return sorted(jobs, key=lambda j: j.created_at, reverse=True)

    def update(self, job_id: str, tenant_id: str | None = None, **fields) -> Optional[TrainingJob]:
        with _lock:
            data = self._load()
            if job_id not in data:
                return None
            if tenant_id is not None:
                entry_tenant = (str(data[job_id].get("tenant_id", "default")) or "default").strip() or "default"
                if entry_tenant != (tenant_id or "default"):
                    return None
            data[job_id].update({k: (v.value if hasattr(v, "value") else v) for k, v in fields.items()})
            self._save(data)
            return TrainingJob(**data[job_id])

    def append_log(self, job_id: str, line: str, max_lines: int = 50, tenant_id: str | None = None) -> None:
        """Thread-safe append to the job's log_tail ring buffer."""
        with _lock:
            data = self._load()
            if job_id not in data:
                return
            if tenant_id is not None:
                entry_tenant = (str(data[job_id].get("tenant_id", "default")) or "default").strip() or "default"
                if entry_tenant != (tenant_id or "default"):
                    return
            log = data[job_id].get("log_tail", [])
            log.append(line)
            data[job_id]["log_tail"] = log[-max_lines:]
            self._save(data)

    def update_progress(self, job_id: str, step: int, total: int, loss: Optional[float] = None, tenant_id: str | None = None) -> None:
        """Convenience: update step progress + optional loss."""
        pct = round((step / total) * 100.0, 1) if total > 0 else 0.0
        kwargs: dict = {"current_step": step, "total_steps": total, "progress": pct}
        if loss is not None:
            kwargs["loss"] = round(loss, 5)
        self.update(job_id, tenant_id=tenant_id, **kwargs)

    def delete(self, job_id: str, tenant_id: str | None = None) -> bool:
        with _lock:
            data = self._load()
            if job_id not in data:
                return False
            if tenant_id is not None:
                entry_tenant = (str(data[job_id].get("tenant_id", "default")) or "default").strip() or "default"
                if entry_tenant != (tenant_id or "default"):
                    return False
            del data[job_id]
            self._save(data)
        return True
