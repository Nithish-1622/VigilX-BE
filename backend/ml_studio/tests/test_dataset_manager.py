"""
Tests for DatasetManager — upload, validation, listing, deletion.
Run: pytest backend/ml_studio/tests/test_dataset_manager.py -v
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

# ── Path setup ─────────────────────────────────────────────────────────────────
_backend_root = Path(__file__).resolve().parent.parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def temp_registry(tmp_path, monkeypatch):
    """Redirect all registry/dataset paths to a temp directory for isolation."""
    monkeypatch.setenv("ML_STUDIO_DATASET_STORE", str(tmp_path / "datasets"))
    monkeypatch.setenv("ML_STUDIO_REGISTRY_DIR", str(tmp_path))
    yield tmp_path


def _make_jsonl(rows: list[dict]) -> bytes:
    return "\n".join(json.dumps(r) for r in rows).encode()


def _make_csv(rows: list[dict], extra_cols: list[str] | None = None) -> bytes:
    headers = ["prompt", "completion"] + (extra_cols or [])
    lines = [",".join(headers)]
    for r in rows:
        lines.append(",".join(str(r.get(h, "")) for h in headers))
    return "\n".join(lines).encode()


SAMPLE_ROWS = [
    {"prompt": f"Summarise FIR-2025-0{i:02d}", "completion": f"Accused: Person {i}, Status: Under investigation"}
    for i in range(1, 21)
]


# ── Upload tests ───────────────────────────────────────────────────────────────

class TestDatasetUpload:

    def test_jsonl_upload_success(self, temp_registry):
        from ml_studio.core.dataset_manager import DatasetManager
        mgr = DatasetManager()
        content = _make_jsonl(SAMPLE_ROWS)
        result = mgr.ingest("test_data.jsonl", content)

        assert result.dataset_id
        assert result.filename == "test_data.jsonl"
        assert result.format == "jsonl"
        assert result.row_count == 20
        assert len(result.preview) == 3
        assert result.file_size_bytes == len(content)

    def test_csv_upload_success(self, temp_registry):
        from ml_studio.core.dataset_manager import DatasetManager
        mgr = DatasetManager()
        content = _make_csv(SAMPLE_ROWS)
        result = mgr.ingest("training.csv", content)

        assert result.format == "csv"
        assert result.row_count == 20

    def test_unsupported_format_rejected(self, temp_registry):
        from ml_studio.core.dataset_manager import DatasetManager
        mgr = DatasetManager()
        with pytest.raises(ValueError, match="Unsupported file format"):
            mgr.ingest("data.txt", b"some text")

    def test_empty_file_rejected(self, temp_registry):
        from ml_studio.core.dataset_manager import DatasetManager
        mgr = DatasetManager()
        with pytest.raises(ValueError):
            mgr.ingest("empty.jsonl", b"")

    def test_invalid_jsonl_rejected(self, temp_registry):
        from ml_studio.core.dataset_manager import DatasetManager
        mgr = DatasetManager()
        with pytest.raises(ValueError, match="JSONL parse error"):
            mgr.ingest("bad.jsonl", b'{"prompt": "ok"}\nNOT_JSON\n')

    def test_missing_completion_field_warns(self, temp_registry):
        from ml_studio.core.dataset_manager import DatasetManager
        mgr = DatasetManager()
        rows = [{"prompt": f"Q{i}"} for i in range(20)]
        content = _make_jsonl(rows)
        with pytest.raises(ValueError, match="No valid rows"):
            mgr.ingest("missing_completion.jsonl", content)

    def test_partial_missing_rows_warns_but_accepts(self, temp_registry):
        from ml_studio.core.dataset_manager import DatasetManager
        mgr = DatasetManager()
        good_rows = SAMPLE_ROWS[:15]
        bad_rows = [{"prompt": "q without completion"}] * 5
        content = _make_jsonl(good_rows + bad_rows)
        result = mgr.ingest("partial.jsonl", content)
        assert result.row_count == 15
        assert any("missing" in w.lower() for w in result.warnings)

    def test_preview_capped_at_3_rows(self, temp_registry):
        from ml_studio.core.dataset_manager import DatasetManager
        mgr = DatasetManager()
        content = _make_jsonl(SAMPLE_ROWS)
        result = mgr.ingest("data.jsonl", content)
        assert len(result.preview) <= 3

    def test_file_persisted_on_disk(self, temp_registry):
        from ml_studio.core.dataset_manager import DatasetManager
        mgr = DatasetManager()
        content = _make_jsonl(SAMPLE_ROWS)
        result = mgr.ingest("data.jsonl", content)
        assert Path(
            temp_registry / "datasets" / f"{result.dataset_id}.jsonl"
        ).exists()


# ── Listing tests ──────────────────────────────────────────────────────────────

class TestDatasetList:

    def test_list_empty(self, temp_registry):
        from ml_studio.core.dataset_manager import DatasetManager
        mgr = DatasetManager()
        assert mgr.list_datasets() == []

    def test_list_returns_uploaded(self, temp_registry):
        from ml_studio.core.dataset_manager import DatasetManager
        mgr = DatasetManager()
        mgr.ingest("a.jsonl", _make_jsonl(SAMPLE_ROWS))
        mgr.ingest("b.csv", _make_csv(SAMPLE_ROWS))
        records = mgr.list_datasets()
        assert len(records) == 2

    def test_list_ordered_newest_first(self, temp_registry):
        from ml_studio.core.dataset_manager import DatasetManager
        import time
        mgr = DatasetManager()
        mgr.ingest("first.jsonl", _make_jsonl(SAMPLE_ROWS))
        time.sleep(0.05)
        mgr.ingest("second.jsonl", _make_jsonl(SAMPLE_ROWS))
        records = mgr.list_datasets()
        assert records[0].filename == "second.jsonl"


# ── Deletion tests ─────────────────────────────────────────────────────────────

class TestDatasetDelete:

    def test_delete_existing(self, temp_registry):
        from ml_studio.core.dataset_manager import DatasetManager
        mgr = DatasetManager()
        result = mgr.ingest("del.jsonl", _make_jsonl(SAMPLE_ROWS))
        assert mgr.delete_dataset(result.dataset_id) is True
        assert mgr.get_dataset(result.dataset_id) is None

    def test_delete_nonexistent_returns_false(self, temp_registry):
        from ml_studio.core.dataset_manager import DatasetManager
        mgr = DatasetManager()
        assert mgr.delete_dataset("nonexistent-id") is False

    def test_delete_removes_file_from_disk(self, temp_registry):
        from ml_studio.core.dataset_manager import DatasetManager
        mgr = DatasetManager()
        result = mgr.ingest("del2.jsonl", _make_jsonl(SAMPLE_ROWS))
        file_path = Path(temp_registry / "datasets" / f"{result.dataset_id}.jsonl")
        assert file_path.exists()
        mgr.delete_dataset(result.dataset_id)
        assert not file_path.exists()


# ── Load rows tests ────────────────────────────────────────────────────────────

class TestLoadRows:

    def test_load_rows_returns_valid_rows(self, temp_registry):
        from ml_studio.core.dataset_manager import DatasetManager
        mgr = DatasetManager()
        result = mgr.ingest("load.jsonl", _make_jsonl(SAMPLE_ROWS))
        rows = mgr.load_rows(result.dataset_id)
        assert len(rows) == 20
        assert all("prompt" in r and "completion" in r for r in rows)

    def test_load_rows_not_found_raises(self, temp_registry):
        from ml_studio.core.dataset_manager import DatasetManager
        mgr = DatasetManager()
        with pytest.raises(FileNotFoundError):
            mgr.load_rows("fake-id-that-doesnt-exist")
