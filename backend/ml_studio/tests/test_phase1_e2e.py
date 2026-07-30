"""
Phase 1 End-to-End Verification Test Suite
===========================================
Validates the entire foundation pipeline across all 4 sample datasets:
1. faq_small_50.csv      (50 rows — Criminal law FAQ)
2. chat_small.jsonl      (10 rows — Multi-turn investigation chat)
3. legal_policy.jsonl    (10 rows — Security & law enforcement SOPs)
4. financial_fraud.csv   (10 rows — Financial intelligence & hawala)

Pipeline sequence verified:
  Dataset Ingestion → Storage → Job Creation → Step Progress Tracking →
  Adapter Registration → Ollama Modelfile Generation → Activation → Inference Query

Run with:
  pytest backend/ml_studio/tests/test_phase1_e2e.py -v
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ── Path setup ─────────────────────────────────────────────────────────────────
_backend_root = Path(__file__).resolve().parent.parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

_SAMPLES_DIR = _backend_root / "ml_studio" / "samples"


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def isolated_ml_studio(tmp_path, monkeypatch):
    """Isolate registry and storage paths to a temporary directory."""
    datasets_dir = tmp_path / "datasets"
    adapters_dir = tmp_path / "adapters"
    registry_dir = tmp_path / "registry"
    datasets_dir.mkdir(parents=True, exist_ok=True)
    adapters_dir.mkdir(parents=True, exist_ok=True)
    registry_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("ML_STUDIO_DATASET_STORE", str(datasets_dir))
    monkeypatch.setenv("ML_STUDIO_ADAPTER_STORE", str(adapters_dir))
    monkeypatch.setenv("ML_STUDIO_REGISTRY_DIR", str(registry_dir))
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")

    yield tmp_path


# ── Phase 1 E2E Test Class ──────────────────────────────────────────────────────

class TestPhase1FoundationE2E:

    def test_samples_exist(self):
        """Verify all 4 required sample datasets exist on disk."""
        assert (_SAMPLES_DIR / "faq_small_50.csv").exists()
        assert (_SAMPLES_DIR / "chat_small.jsonl").exists()
        assert (_SAMPLES_DIR / "legal_policy.jsonl").exists()
        assert (_SAMPLES_DIR / "financial_fraud.csv").exists()

    def test_ingest_all_four_sample_datasets(self, isolated_ml_studio):
        """Step 1: Upload and ingest all 4 sample datasets."""
        from ml_studio.core.dataset_manager import DatasetManager
        mgr = DatasetManager()

        # 1. FAQ CSV (50 rows)
        faq_bytes = (_SAMPLES_DIR / "faq_small_50.csv").read_bytes()
        res_faq = mgr.ingest("faq_small_50.csv", faq_bytes)
        assert res_faq.row_count == 50
        assert res_faq.format == "csv"

        # 2. Chat JSONL (10 rows)
        chat_bytes = (_SAMPLES_DIR / "chat_small.jsonl").read_bytes()
        res_chat = mgr.ingest("chat_small.jsonl", chat_bytes)
        assert res_chat.row_count == 10
        assert res_chat.format == "jsonl"

        # 3. Legal Policy JSONL (10 rows)
        policy_bytes = (_SAMPLES_DIR / "legal_policy.jsonl").read_bytes()
        res_policy = mgr.ingest("legal_policy.jsonl", policy_bytes)
        assert res_policy.row_count == 10
        assert res_policy.format == "jsonl"

        # 4. Financial Fraud CSV (10 rows)
        fraud_bytes = (_SAMPLES_DIR / "financial_fraud.csv").read_bytes()
        res_fraud = mgr.ingest("financial_fraud.csv", fraud_bytes)
        assert res_fraud.row_count == 10
        assert res_fraud.format == "csv"

        # Verify all 4 are present in registry
        registered = mgr.list_datasets()
        assert len(registered) == 4

    def test_end_to_end_job_and_ollama_bridge_pipeline(self, isolated_ml_studio):
        """
        Step 2: Full pipeline execution across job creation, progress tracking,
        adapter simulation, Ollama Modelfile construction, and model activation.
        """
        from ml_studio.core.dataset_manager import DatasetManager
        from ml_studio.core.model_registry import JobRegistry, ModelRegistry
        from ml_studio.core.ollama_bridge import OllamaBridge
        from ml_studio.schemas.job import JobStatus, TrainingConfig
        from ml_studio.schemas.model import ModelStatus, RegisteredModel
        from datetime import datetime
        import uuid

        dataset_mgr = DatasetManager()
        job_reg = JobRegistry()
        model_reg = ModelRegistry()
        bridge = OllamaBridge()

        # Ingest FAQ dataset
        faq_bytes = (_SAMPLES_DIR / "faq_small_50.csv").read_bytes()
        ds = dataset_mgr.ingest("faq_small_50.csv", faq_bytes)

        # Create training config & job
        config = TrainingConfig(
            dataset_id=ds.dataset_id,
            job_name="Phase1-FAQ-FineTune",
            base_model="llama3.1",
            lora_rank=8,
            max_steps=50,
            push_to_ollama=False,
        )
        job = job_reg.create(config, "Phase1-FAQ-FineTune")
        assert job.status == JobStatus.QUEUED

        # Simulate job execution progress
        job_reg.update(job.job_id, status=JobStatus.PREPARING)
        job_reg.update_progress(job.job_id, step=25, total=50, loss=0.85)
        job_reg.append_log(job.job_id, "Halfway done")
        job_reg.update_progress(job.job_id, step=50, total=50, loss=0.32)
        job_reg.update(job.job_id, status=JobStatus.SAVING)

        # Simulate adapter path creation
        adapter_path = isolated_ml_studio / "adapters" / job.job_id / "adapter"
        adapter_path.mkdir(parents=True, exist_ok=True)
        (adapter_path / "adapter_model.bin").write_text("dummy weights")

        # Register completed model
        model_id = str(uuid.uuid4())
        model = RegisteredModel(
            model_id=model_id,
            model_name="phase1-faq-adapter",
            ollama_model_name=None,
            base_model="llama3.1",
            job_id=job.job_id,
            adapter_path=str(adapter_path),
            status=ModelStatus.ADAPTER_SAVED,
            is_active=False,
            training_steps=50,
            final_loss=0.32,
            created_at=datetime.utcnow(),
        )
        model_reg.create(model)
        job_reg.update(job.job_id, status=JobStatus.COMPLETED, model_id=model_id)

        # Test Ollama Modelfile construction
        system_prompt = bridge._compose_system_prompt()
        assert len(system_prompt) > 50
        assert "evidence" in system_prompt.lower() or "vigilx" in system_prompt.lower()

        modelfile = bridge._build_modelfile(
            base_model="llama3.1",
            adapter_path=str(adapter_path),
            system_prompt=system_prompt,
        )
        assert "FROM llama3.1" in modelfile
        assert "SYSTEM" in modelfile
        assert "temperature 0.2" in modelfile

        # Mock ollama CLI create
        with patch.object(bridge, "_run_ollama_create") as mock_cli:
            mock_cli.return_value = None
            ollama_name = bridge.create_model(model_id, "Phase1-FAQ-FineTune")

        assert ollama_name.startswith("vigilx-")
        activated = model_reg.activate(model_id)
        assert activated.is_active is True
        assert activated.status == ModelStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_inference_query_with_mocked_ollama(self, isolated_ml_studio):
        """
        Step 3: Verify local inference client query execution using an active model.
        """
        from ml_studio.core.inference_client import LocalInferenceClient
        from ml_studio.core.model_registry import ModelRegistry
        from ml_studio.schemas.model import ModelStatus, RegisteredModel
        from datetime import datetime
        import uuid

        model_reg = ModelRegistry()
        m_id = str(uuid.uuid4())
        model = RegisteredModel(
            model_id=m_id,
            model_name="phase1-active-model",
            ollama_model_name="vigilx-phase1-test",
            base_model="llama3.1",
            job_id="j-test",
            adapter_path=str(isolated_ml_studio),
            status=ModelStatus.ACTIVE,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        model_reg.create(model)
        model_reg.activate(m_id)

        client = LocalInferenceClient()

        # Mock Ollama chat completion API response
        mock_body = {
            "choices": [{"message": {"role": "assistant", "content": "An FIR is a First Information Report."}}],
            "usage": {"total_tokens": 30},
        }
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_body

        with patch("httpx.AsyncClient") as mock_cls:
            mock_http = AsyncMock()
            mock_cls.return_value.__aenter__.return_value = mock_http
            mock_http.post = AsyncMock(return_value=mock_resp)

            result = await client.generate("What is an FIR?")

        assert result["answer"] == "An FIR is a First Information Report."
        assert result["model_used"] == "vigilx-phase1-test"
        assert result["tokens_used"] == 30
        assert result["latency_ms"] > 0
