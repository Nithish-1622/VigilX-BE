from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

_AUDIT_LOG_ENV = "ML_STUDIO_AUDIT_LOG"
_DEFAULT_AUDIT_LOG = "ml_studio_audit.jsonl"


class AuditLogger:
    """
    Immutable append-only JSON audit logger for ML Studio operations.
    Each event is written as a single JSONL line with timestamp, actor, and metadata.
    """

    def __init__(self, log_file: str | None = None) -> None:
        self._log_file = Path(
            os.environ.get(_AUDIT_LOG_ENV, log_file or _DEFAULT_AUDIT_LOG)
        )
        self._log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        event_type: str,
        actor: str = "system",
        tenant_id: str = "default",
        details: dict | None = None,
    ) -> None:
        """
        Write an immutable audit event to the JSONL audit log.

        Args:
            event_type: Short event identifier (e.g. "dataset_upload", "model_activated").
            actor: The system component or user responsible for the event.
            details: Additional metadata relevant to the event.
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "actor": actor,
            "tenant_id": tenant_id,
            "details": details or {},
        }
        try:
            with open(self._log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, default=str) + "\n")
        except OSError as exc:
            logger.warning("Audit log write failed: %s", exc)

    def read_recent(self, n: int = 100) -> list[dict]:
        """Return the last N audit entries from the log file."""
        if not self._log_file.exists():
            return []
        try:
            lines = self._log_file.read_text(encoding="utf-8").strip().splitlines()
            recent = lines[-n:] if len(lines) > n else lines
            return [json.loads(line) for line in recent if line.strip()]
        except Exception as exc:
            logger.warning("Audit log read failed: %s", exc)
            return []

    # ── Convenience helpers ─────────────────────────────────────────────────────

    def dataset_uploaded(self, dataset_id: str, filename: str, row_count: int) -> None:
        self.log("dataset_upload", details={
            "dataset_id": dataset_id,
            "filename": filename,
            "row_count": row_count,
        })

    def training_started(self, job_id: str, dataset_id: str, strategy: str, tenant_id: str = "default") -> None:
        self.log("training_started", tenant_id=tenant_id, details={
            "job_id": job_id,
            "dataset_id": dataset_id,
            "strategy": strategy,
        })

    def model_activated(self, model_id: str, model_name: str, tenant_id: str = "default") -> None:
        self.log("model_activated", tenant_id=tenant_id, details={
            "model_id": model_id,
            "model_name": model_name,
        })

    def dataset_deleted(self, dataset_id: str, filename: str, tenant_id: str = "default") -> None:
        self.log("dataset_deleted", tenant_id=tenant_id, details={
            "dataset_id": dataset_id,
            "filename": filename,
        })

    def model_deleted(self, model_id: str, model_name: str, tenant_id: str = "default") -> None:
        self.log("model_deleted", tenant_id=tenant_id, details={
            "model_id": model_id,
            "model_name": model_name,
        })
