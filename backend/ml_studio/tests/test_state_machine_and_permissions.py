from __future__ import annotations

import importlib
from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ml_studio.config import ensure_directories
from ml_studio.core.model_registry import JobRegistry, ModelRegistry
from ml_studio.schemas.job import JobStatus, TrainingConfig
from ml_studio.schemas.model import (
    InferenceCompareRequest,
    ModelLifecycleStage,
    ModelStatus,
    RegisteredModel,
)


@pytest.fixture
def isolated_env(tmp_path, monkeypatch):
    monkeypatch.setenv("ML_STUDIO_REGISTRY_DIR", str(tmp_path / "registry"))
    monkeypatch.setenv("ML_STUDIO_DATASET_STORE", str(tmp_path / "datasets"))
    monkeypatch.setenv("ML_STUDIO_ADAPTER_STORE", str(tmp_path / "adapters"))
    monkeypatch.setenv("ML_STUDIO_REPORTS_STORE", str(tmp_path / "reports"))
    ensure_directories()
    return tmp_path


@pytest.fixture
def app_client(isolated_env):
    import ml_studio.routers.jobs as jobs_mod
    import ml_studio.routers.models as models_mod

    importlib.reload(jobs_mod)
    importlib.reload(models_mod)

    app = FastAPI()
    app.include_router(jobs_mod.router)
    app.include_router(models_mod.router)
    return TestClient(app)


def test_model_activation_synchronizes_job_status(isolated_env):
    tenant_id = "t1"
    job_reg = JobRegistry()
    model_reg = ModelRegistry()

    cfg1 = TrainingConfig(dataset_id="ds1", job_name="j1", push_to_ollama=False)
    job1 = job_reg.create(cfg1, "j1", tenant_id=tenant_id)

    model1 = RegisteredModel(
        model_id="m1",
        tenant_id=tenant_id,
        model_name="m1",
        ollama_model_name="ollama-m1",
        base_model="llama3.1",
        job_id=job1.job_id,
        adapter_path=None,
        domain="general",
        status=ModelStatus.READY,
        lifecycle_stage=ModelLifecycleStage.APPROVED,
        is_active=False,
        training_steps=0,
        final_loss=None,
        created_at=datetime.utcnow(),
    )
    model_reg.create(model1)
    job_reg.update(job1.job_id, tenant_id=tenant_id, status=JobStatus.COMPLETED, model_id=model1.model_id)

    model_reg.activate(model1.model_id, tenant_id=tenant_id)
    job1_after = job_reg.get(job1.job_id, tenant_id=tenant_id)
    assert job1_after is not None
    assert job1_after.status == JobStatus.ACTIVE

    cfg2 = TrainingConfig(dataset_id="ds2", job_name="j2", push_to_ollama=False)
    job2 = job_reg.create(cfg2, "j2", tenant_id=tenant_id)
    model2 = RegisteredModel(
        model_id="m2",
        tenant_id=tenant_id,
        model_name="m2",
        ollama_model_name="ollama-m2",
        base_model="llama3.1",
        job_id=job2.job_id,
        adapter_path=None,
        domain="general",
        status=ModelStatus.READY,
        lifecycle_stage=ModelLifecycleStage.APPROVED,
        is_active=False,
        training_steps=0,
        final_loss=None,
        created_at=datetime.utcnow(),
    )
    model_reg.create(model2)
    job_reg.update(job2.job_id, tenant_id=tenant_id, status=JobStatus.COMPLETED, model_id=model2.model_id)

    model_reg.activate(model2.model_id, tenant_id=tenant_id)
    job2_after = job_reg.get(job2.job_id, tenant_id=tenant_id)
    job1_final = job_reg.get(job1.job_id, tenant_id=tenant_id)
    assert job2_after is not None and job2_after.status == JobStatus.ACTIVE
    assert job1_final is not None and job1_final.status == JobStatus.COMPLETED


def test_permission_guard_returns_403(app_client):
    resp = app_client.post(
        "/ml/jobs/does-not-matter/approve",
        json={"approved_by": "admin_user"},
        headers={"X-Tenant-ID": "default"},
    )
    assert resp.status_code == 403

    resp = app_client.post(
        "/ml/jobs/does-not-matter/reject",
        json={"rejected_by": "admin_user", "reason": "no"},
        headers={"X-Tenant-ID": "default"},
    )
    assert resp.status_code == 403

    resp = app_client.post(
        "/ml/models/does-not-matter/activate",
        json={},
        headers={"X-Tenant-ID": "default"},
    )
    assert resp.status_code == 403


def test_tenant_filtering_on_job_list(app_client, isolated_env):
    job_reg = JobRegistry()
    cfg = TrainingConfig(dataset_id="ds", job_name="j", push_to_ollama=False)
    job_reg.create(cfg, "j", tenant_id="tenant-a")
    job_reg.create(cfg, "j", tenant_id="tenant-b")

    resp = app_client.get("/ml/jobs/list", headers={"X-Tenant-ID": "tenant-a"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["jobs"][0]["tenant_id"] == "tenant-a"


def test_job_report_has_canonical_shape(app_client, isolated_env):
    job_reg = JobRegistry()
    cfg = TrainingConfig(dataset_id="ds", job_name="j", push_to_ollama=False)
    job = job_reg.create(cfg, "j", tenant_id="tenant-a")
    job_reg.update(
        job.job_id,
        tenant_id="tenant-a",
        status=JobStatus.COMPLETED,
        pipeline_stage_results={"training": {"ok": True}},
        eval_scores={"rouge_1": 0.5},
        benchmark_result={"safety_pass_rate": 0.9},
    )

    resp = app_client.get(f"/ml/jobs/{job.job_id}/report", headers={"X-Tenant-ID": "tenant-a"})
    assert resp.status_code == 200
    body = resp.json()
    assert set(body.keys()) == {"summary", "pipeline_stage_results", "evaluation", "benchmark", "recommendations"}


def test_inference_compare_accepts_candidate_model_alias():
    req = InferenceCompareRequest.model_validate({"candidate_model": "m1", "prompt": "hi"})
    assert req.candidate_model_id == "m1"


def test_activate_allows_retry_from_error(app_client, isolated_env, monkeypatch):
    tenant_id = "t1"
    job_reg = JobRegistry()
    model_reg = ModelRegistry()

    cfg = TrainingConfig(dataset_id="ds1", job_name="j1", push_to_ollama=False)
    job = job_reg.create(cfg, "j1", tenant_id=tenant_id)

    model = RegisteredModel(
        model_id="m-retry",
        tenant_id=tenant_id,
        model_name="m-retry",
        ollama_model_name=None,
        base_model="llama3.1",
        job_id=job.job_id,
        adapter_path=str(isolated_env / "adapter"),
        domain="general",
        status=ModelStatus.ERROR,
        lifecycle_stage=ModelLifecycleStage.APPROVED,
        is_active=False,
        training_steps=0,
        final_loss=None,
        created_at=datetime.utcnow(),
    )
    (isolated_env / "adapter").write_text("x", encoding="utf-8")
    model_reg.create(model)

    import ml_studio.routers.models as models_mod

    def _fake_create_model(model_id: str, job_name: str) -> str:
        model_reg.update(model_id, tenant_id=tenant_id, status=ModelStatus.READY, ollama_model_name="vigilx-retry")
        return "vigilx-retry"

    monkeypatch.setattr(models_mod._bridge, "create_model", _fake_create_model)

    resp = app_client.post(
        "/ml/models/m-retry/activate",
        headers={
            "X-Tenant-ID": tenant_id,
            "X-User-ID": "1",
            "X-Username": "admin",
            "X-Permissions": "ml_studio.activate_model",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_active"] is True
    assert body["ollama_model_name"] == "vigilx-retry"
