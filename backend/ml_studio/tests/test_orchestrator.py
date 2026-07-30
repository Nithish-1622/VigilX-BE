from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

_backend_root = Path(__file__).resolve().parent.parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from ml_studio.schemas.job import JobStatus, TrainingConfig
from ml_studio.jobs.orchestrator import PipelineOrchestrator
from ml_studio.core.dataset_manager import DatasetManager
from ml_studio.core.model_registry import JobRegistry


@pytest.fixture
def isolated_orchestrator(tmp_path, monkeypatch):
    monkeypatch.setenv("ML_STUDIO_REGISTRY_DIR", str(tmp_path / "registry"))
    monkeypatch.setenv("ML_STUDIO_DATASET_STORE", str(tmp_path / "datasets"))
    monkeypatch.setenv("ML_STUDIO_ADAPTER_STORE", str(tmp_path / "adapters"))
    return tmp_path


SAMPLE_ROWS = [
    {"prompt": f"FIR Question {i}?", "completion": f"Investigative Answer {i}."}
    for i in range(1, 25)
]


class TestPipelineOrchestrator:

    def test_full_pipeline_with_auto_approve(self, isolated_orchestrator):
        ds_mgr = DatasetManager()
        job_reg = JobRegistry()
        orchestrator = PipelineOrchestrator()

        # 1. Ingest sample dataset
        import json
        content = "\n".join(json.dumps(r) for r in SAMPLE_ROWS).encode()
        ds_res = ds_mgr.ingest("sample.jsonl", content)

        # 2. Create job config
        config = TrainingConfig(
            dataset_id=ds_res.dataset_id,
            job_name="Test-Pipeline-Job",
            base_model="llama3.1",
            training_strategy="lora",
            max_steps=10,
            auto_approve=True,
            push_to_ollama=False,
        )
        job = job_reg.create(config, "Test-Pipeline-Job")

        # 3. Run pipeline
        res = orchestrator.run_pipeline(job.job_id, config)

        assert res.status == JobStatus.COMPLETED
        assert res.progress == 100.0
        assert "validating" in res.pipeline_stage_results
        assert "preprocessing" in res.pipeline_stage_results
        assert "training" in res.pipeline_stage_results
        assert "evaluating" in res.pipeline_stage_results
        assert "benchmarking" in res.pipeline_stage_results

    def test_pipeline_pauses_at_pending_approval(self, isolated_orchestrator):
        ds_mgr = DatasetManager()
        job_reg = JobRegistry()
        orchestrator = PipelineOrchestrator()

        import json
        content = "\n".join(json.dumps(r) for r in SAMPLE_ROWS).encode()
        ds_res = ds_mgr.ingest("sample2.jsonl", content)

        config = TrainingConfig(
            dataset_id=ds_res.dataset_id,
            job_name="Pause-Approval-Job",
            base_model="llama3.1",
            training_strategy="lora",
            max_steps=10,
            auto_approve=False,  # Should pause
            push_to_ollama=False,
        )
        job = job_reg.create(config, "Pause-Approval-Job")

        res = orchestrator.run_pipeline(job.job_id, config)
        assert res.status == JobStatus.PENDING_APPROVAL
        assert res.approval_required is True

        # Approve job
        res_approved = orchestrator.approve_job(job.job_id, approved_by="senior_analyst")
        assert res_approved.status == JobStatus.COMPLETED
        assert res_approved.approved_by == "senior_analyst"
