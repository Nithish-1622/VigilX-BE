from __future__ import annotations

import csv
import io
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Generator

from ml_studio.config import ml_settings
from ml_studio.schemas.dataset import (
    DatasetPreviewRow,
    DatasetRecord,
    DatasetUploadResponse,
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_registry_file() -> Path:
    return Path(ml_settings.registry_dir) / "datasets.json"


def _load_registry() -> dict[str, dict]:
    reg_file = _get_registry_file()
    if reg_file.exists():
        try:
            return json.loads(reg_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_registry(data: dict[str, dict]) -> None:
    reg_file = _get_registry_file()
    reg_file.parent.mkdir(parents=True, exist_ok=True)
    reg_file.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")



# ─────────────────────────────────────────────────────────────────────────────
# Parsing helpers
# ─────────────────────────────────────────────────────────────────────────────

def _parse_jsonl(content: bytes) -> list[dict]:
    """Parse a JSONL byte buffer into a list of dicts."""
    rows: list[dict] = []
    for i, line in enumerate(content.decode("utf-8", errors="replace").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"JSONL parse error on line {i}: {exc}") from exc
        rows.append(obj)
    return rows


def _parse_csv(content: bytes) -> list[dict]:
    """Parse a CSV byte buffer into a list of dicts."""
    text = content.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    return [row for row in reader]


def _validate_rows(rows: list[dict]) -> list[str]:
    """
    Validate that every row has 'prompt' and 'completion' keys.
    Returns a list of warning messages (empty if all good).
    """
    warnings: list[str] = []
    missing_prompt = 0
    missing_completion = 0
    empty_rows = 0

    for row in rows:
        p = str(row.get("prompt", "")).strip()
        c = str(row.get("completion", "")).strip()
        if not p:
            missing_prompt += 1
        if not c:
            missing_completion += 1
        if not p and not c:
            empty_rows += 1

    if missing_prompt:
        warnings.append(f"{missing_prompt} row(s) missing or empty 'prompt' field — will be skipped during training.")
    if missing_completion:
        warnings.append(f"{missing_completion} row(s) missing or empty 'completion' field — will be skipped during training.")
    if empty_rows:
        warnings.append(f"{empty_rows} completely empty row(s) detected.")
    return warnings


def _iter_valid_rows(rows: list[dict]) -> Generator[dict, None, None]:
    """Yield only rows that have non-empty prompt and completion."""
    for row in rows:
        if str(row.get("prompt", "")).strip() and str(row.get("completion", "")).strip():
            yield row


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

class DatasetManager:
    """
    Handles upload, validation, storage, listing, and deletion of training datasets.

    Expected dataset format (both JSONL and CSV):
        {"prompt": "Summarise FIR-2025-042...", "completion": "The accused..."}

    The manager writes raw files to disk under:
        registry/datasets/<dataset_id>.<ext>

    A lightweight JSON registry (registry/datasets.json) stores metadata.
    """

    def __init__(self) -> None:
        Path(ml_settings.dataset_store_path).mkdir(parents=True, exist_ok=True)

    # ── Upload ────────────────────────────────────────────────────────────────

    def ingest(
        self,
        filename: str,
        content: bytes,
        tenant_id: str = "default",
    ) -> DatasetUploadResponse:
        """
        Validate, store, and register an uploaded dataset file.

        Args:
            filename: Original filename provided by the client.
            content:  Raw file bytes.

        Returns:
            DatasetUploadResponse with metadata and a preview.

        Raises:
            ValueError: If the file is too large, unsupported format, or unparsable.
        """
        # ── Size guard ──────────────────────────────────────────────────────
        if len(content) > ml_settings.max_dataset_size_bytes:
            max_mb = ml_settings.max_dataset_size_bytes // (1024 * 1024)
            raise ValueError(f"Dataset file exceeds maximum allowed size of {max_mb} MB.")

        # ── Format detection ────────────────────────────────────────────────
        ext = Path(filename).suffix.lower()
        if ext not in ml_settings.allowed_dataset_extensions:
            raise ValueError(
                f"Unsupported file format '{ext}'. Allowed: "
                + ", ".join(ml_settings.allowed_dataset_extensions)
            )

        fmt = ext.lstrip(".")  # "jsonl" or "csv"

        # ── Parse ───────────────────────────────────────────────────────────
        if fmt == "jsonl":
            raw_rows = _parse_jsonl(content)
        else:
            raw_rows = _parse_csv(content)

        if not raw_rows:
            raise ValueError("Dataset file is empty — no rows found.")

        warnings = _validate_rows(raw_rows)
        valid_rows = list(_iter_valid_rows(raw_rows))

        if not valid_rows:
            raise ValueError(
                "No valid rows found. Every row must have non-empty 'prompt' and 'completion' fields."
            )

        # ── Persist ──────────────────────────────────────────────────────────
        dataset_id = str(uuid.uuid4())
        safe_filename = f"{dataset_id}{ext}"
        dest_path = Path(ml_settings.dataset_store_path) / safe_filename
        dest_path.write_bytes(content)
        logger.info("Dataset %s stored at %s (%d bytes)", dataset_id, dest_path, len(content))

        # ── Registry entry ───────────────────────────────────────────────────
        now = datetime.utcnow()
        record = DatasetRecord(
            dataset_id=dataset_id,
            tenant_id=tenant_id or "default",
            filename=filename,
            format=fmt,
            row_count=len(valid_rows),
            file_size_bytes=len(content),
            uploaded_at=now,
            file_path=str(dest_path),
        )
        registry = _load_registry()
        registry[dataset_id] = record.model_dump(mode="json")
        _save_registry(registry)

        # ── Preview (first 3 valid rows) ─────────────────────────────────────
        preview = [
            DatasetPreviewRow(
                prompt=str(r["prompt"])[:200],
                completion=str(r["completion"])[:200],
            )
            for r in valid_rows[:3]
        ]

        return DatasetUploadResponse(
            dataset_id=dataset_id,
            tenant_id=record.tenant_id,
            filename=filename,
            format=fmt,
            row_count=len(valid_rows),
            file_size_bytes=len(content),
            uploaded_at=now,
            preview=preview,
            warnings=warnings,
        )

    # ── List ──────────────────────────────────────────────────────────────────

    def list_datasets(self, tenant_id: str = "default") -> list[DatasetRecord]:
        """Return all registered datasets."""
        registry = _load_registry()
        records: list[DatasetRecord] = []
        for entry in registry.values():
            try:
                record = DatasetRecord(**entry)
                record_tenant = getattr(record, "tenant_id", "default") or "default"
                if record_tenant == (tenant_id or "default"):
                    records.append(record)
            except Exception as exc:
                logger.warning("Malformed dataset registry entry: %s", exc)
        return sorted(records, key=lambda r: r.uploaded_at, reverse=True)

    # ── Get one ───────────────────────────────────────────────────────────────

    def get_dataset(self, dataset_id: str, tenant_id: str = "default") -> DatasetRecord | None:
        """Return a single dataset record, or None if not found."""
        registry = _load_registry()
        entry = registry.get(dataset_id)
        if entry is None:
            return None
        record = DatasetRecord(**entry)
        record_tenant = getattr(record, "tenant_id", "default") or "default"
        if record_tenant != (tenant_id or "default"):
            return None
        return record

    # ── Load rows (for trainer) ────────────────────────────────────────────────

    def load_rows(self, dataset_id: str, tenant_id: str = "default") -> list[dict]:
        """
        Load and return validated rows for a given dataset_id.
        Used by the Trainer to iterate training samples.

        Raises:
            FileNotFoundError: If dataset_id not in registry.
            ValueError: If file is missing or unparsable.
        """
        record = self.get_dataset(dataset_id, tenant_id=tenant_id)
        if record is None:
            raise FileNotFoundError(f"Dataset '{dataset_id}' not found in registry.")

        file_path = Path(record.file_path)
        if not file_path.exists():
            raise ValueError(f"Dataset file missing from disk: {file_path}")

        content = file_path.read_bytes()
        if record.format == "jsonl":
            raw_rows = _parse_jsonl(content)
        else:
            raw_rows = _parse_csv(content)

        return list(_iter_valid_rows(raw_rows))

    # ── Delete ────────────────────────────────────────────────────────────────

    def delete_dataset(self, dataset_id: str, tenant_id: str = "default") -> bool:
        """
        Remove dataset file from disk and unregister it.

        Returns:
            True if the dataset was found and deleted, False otherwise.
        """
        registry = _load_registry()
        entry = registry.get(dataset_id)
        if entry is None:
            return False
        entry_tenant = (entry.get("tenant_id") or "default").strip() or "default"
        if entry_tenant != (tenant_id or "default"):
            return False

        # Remove file
        file_path = Path(entry.get("file_path", ""))
        if file_path.exists():
            try:
                file_path.unlink()
                logger.info("Deleted dataset file: %s", file_path)
            except OSError as exc:
                logger.warning("Could not delete dataset file %s: %s", file_path, exc)

        del registry[dataset_id]
        _save_registry(registry)
        return True

    def create_from_rows(
        self,
        filename: str,
        rows: list[dict],
        tenant_id: str = "default",
    ) -> DatasetUploadResponse:
        import json

        content = "\n".join(json.dumps(r, default=str) for r in rows).encode("utf-8")
        return self.ingest(filename=filename, content=content, tenant_id=tenant_id)
