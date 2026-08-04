"""
Tests for ModelRegistry and JobRegistry.
Run: pytest backend/ml_studio/tests/test_model_registry.py -v
"""
from __future__ import annotations

import sys
import time
from datetime import datetime
from pathlib import Path

import pytest

_backend_root = Path(__file__).resolve().parent.parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def job_registry(tmp_path, monkeypatch):
    monkeypatch.setenv("ML_STUDIO_REGISTRY_DIR", str(tmp_path))
    from ml_studio.core.model_registry import JobRegistry
    return JobRegistry()


@pytest.fixture
def model_registry(tmp_path, monkeypatch):
    monkeypatch.setenv("ML_STUDIO_REGISTRY_DIR", str(tmp_path))
    from ml_studio.core.model_registry import ModelRegistry
    return ModelRegistry()


def _sample_config():
    from ml_studio.schemas.job import TrainingConfig
    return TrainingConfig(
        dataset_id="ds-001",
        job_name="Test Fine-Tune",
        base_model="llama3.1",
        lora_rank=8,
        max_steps=100,
    )


def _sample_model(job_id: str):
    from ml_studio.schemas.model import ModelStatus, RegisteredModel
    import uuid
    return RegisteredModel(
        model_id=str(uuid.uuid4()),
        model_name="test-model-v1",
        ollama_model_name=None,
        base_model="llama3.1",
        job_id=job_id,
        adapter_path="/tmp/adapter",
        status=ModelStatus.ADAPTER_SAVED,
        is_active=False,
        training_steps=100,
        created_at=datetime.utcnow(),
    )


# ── Job Registry tests ─────────────────────────────────────────────────────────

class TestJobRegistry:

    def test_create_job(self, job_registry):
        job = job_registry.create(_sample_config(), "My Job")
        assert job.job_id
        assert job.job_name == "My Job"
        from ml_studio.schemas.job import JobStatus
        assert job.status == JobStatus.QUEUED

    def test_get_job(self, job_registry):
        job = job_registry.create(_sample_config(), "Job A")
        retrieved = job_registry.get(job.job_id)
        assert retrieved is not None
        assert retrieved.job_id == job.job_id

    def test_get_nonexistent_returns_none(self, job_registry):
        assert job_registry.get("no-such-id") is None

    def test_list_all_jobs(self, job_registry):
        job_registry.create(_sample_config(), "Job 1")
        job_registry.create(_sample_config(), "Job 2")
        jobs = job_registry.list_all()
        assert len(jobs) == 2

    def test_update_job_status(self, job_registry):
        from ml_studio.schemas.job import JobStatus
        job = job_registry.create(_sample_config(), "Update Test")
        job_registry.update(job.job_id, status=JobStatus.TRAINING)
        updated = job_registry.get(job.job_id)
        assert updated.status == JobStatus.TRAINING

    def test_update_progress(self, job_registry):
        job = job_registry.create(_sample_config(), "Progress Test")
        job_registry.update_progress(job.job_id, step=50, total=100, loss=1.234)
        updated = job_registry.get(job.job_id)
        assert updated.progress == 50.0
        assert updated.current_step == 50
        assert updated.loss == 1.234

    def test_append_log(self, job_registry):
        job = job_registry.create(_sample_config(), "Log Test")
        job_registry.append_log(job.job_id, "Step 1 complete")
        job_registry.append_log(job.job_id, "Step 2 complete")
        updated = job_registry.get(job.job_id)
        assert "Step 1 complete" in updated.log_tail
        assert "Step 2 complete" in updated.log_tail

    def test_log_tail_ring_buffer(self, job_registry):
        job = job_registry.create(_sample_config(), "Ring Test")
        for i in range(100):
            job_registry.append_log(job.job_id, f"Line {i}", max_lines=10)
        updated = job_registry.get(job.job_id)
        assert len(updated.log_tail) == 10
        assert "Line 99" in updated.log_tail

    def test_delete_job(self, job_registry):
        job = job_registry.create(_sample_config(), "Delete Test")
        assert job_registry.delete(job.job_id) is True
        assert job_registry.get(job.job_id) is None

    def test_delete_nonexistent_returns_false(self, job_registry):
        assert job_registry.delete("not-there") is False


# ── Model Registry tests ───────────────────────────────────────────────────────

class TestModelRegistry:

    def test_create_model(self, model_registry):
        from ml_studio.schemas.model import ModelStatus
        m = _sample_model("job-001")
        created = model_registry.create(m)
        assert created.model_id == m.model_id
        assert created.status == ModelStatus.ADAPTER_SAVED

    def test_get_model(self, model_registry):
        m = _sample_model("job-002")
        model_registry.create(m)
        retrieved = model_registry.get(m.model_id)
        assert retrieved is not None
        assert retrieved.model_id == m.model_id

    def test_get_nonexistent(self, model_registry):
        assert model_registry.get("fake") is None

    def test_list_all_models(self, model_registry):
        model_registry.create(_sample_model("j1"))
        model_registry.create(_sample_model("j2"))
        assert len(model_registry.list_all()) == 2

    def test_activate_model(self, model_registry):
        m1 = _sample_model("j1")
        m2 = _sample_model("j2")
        model_registry.create(m1)
        model_registry.create(m2)

        model_registry.update(m1.model_id, ollama_model_name="vigilx-m1")
        model_registry.update(m2.model_id, ollama_model_name="vigilx-m2")

        model_registry.activate(m1.model_id)
        assert model_registry.get(m1.model_id).is_active is True
        assert model_registry.get(m2.model_id).is_active is False

        # Activate m2 — m1 should deactivate
        model_registry.activate(m2.model_id)
        assert model_registry.get(m2.model_id).is_active is True
        assert model_registry.get(m1.model_id).is_active is False

    def test_get_active_model(self, model_registry):
        m = _sample_model("j1")
        model_registry.create(m)
        model_registry.update(m.model_id, ollama_model_name="vigilx-test")
        model_registry.activate(m.model_id)
        active = model_registry.get_active()
        assert active is not None
        assert active.model_id == m.model_id

    def test_get_active_when_none(self, model_registry):
        assert model_registry.get_active() is None

    def test_deactivate_all(self, model_registry):
        m = _sample_model("j1")
        model_registry.create(m)
        model_registry.update(m.model_id, ollama_model_name="vigilx-test")
        model_registry.activate(m.model_id)
        model_registry.deactivate_all()
        assert model_registry.get_active() is None

    def test_delete_model(self, model_registry):
        m = _sample_model("j1")
        model_registry.create(m)
        assert model_registry.delete(m.model_id) is True
        assert model_registry.get(m.model_id) is None

    def test_update_model_fields(self, model_registry):
        from ml_studio.schemas.model import ModelStatus
        m = _sample_model("j1")
        model_registry.create(m)
        model_registry.update(m.model_id, ollama_model_name="new-name", status=ModelStatus.READY)
        updated = model_registry.get(m.model_id)
        assert updated.ollama_model_name == "new-name"
        assert updated.status == ModelStatus.READY
