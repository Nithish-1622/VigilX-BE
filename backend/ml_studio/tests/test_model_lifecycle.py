from __future__ import annotations

import sys
import uuid
from datetime import datetime
from pathlib import Path
import pytest

_backend_root = Path(__file__).resolve().parent.parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from ml_studio.core.model_registry import ModelRegistry
from ml_studio.schemas.model import ModelLifecycleStage, ModelStatus, RegisteredModel


@pytest.fixture
def isolated_model_reg(tmp_path, monkeypatch):
    monkeypatch.setenv("ML_STUDIO_REGISTRY_DIR", str(tmp_path))
    return ModelRegistry()


def _make_model(name: str, domain: str = "finance") -> RegisteredModel:
    return RegisteredModel(
        model_id=str(uuid.uuid4()),
        model_name=name,
        ollama_model_name=f"ollama-{name}",
        base_model="llama3.1",
        job_id=str(uuid.uuid4()),
        domain=domain,
        adapter_path="/tmp/adapter",
        status=ModelStatus.READY,
        lifecycle_stage=ModelLifecycleStage.DRAFT,
        training_steps=100,
        final_loss=0.35,
        eval_scores={"rouge_1": 0.82, "bleu_4": 0.65},
        created_at=datetime.utcnow(),
    )


class TestModelLifecycle:

    def test_auto_versioning_and_version_labels(self, isolated_model_reg):
        m1 = isolated_model_reg.create(_make_model("Finance-1", domain="finance"))
        m2 = isolated_model_reg.create(_make_model("Finance-2", domain="finance"))

        assert m1.version == 1
        assert m1.version_label == "Finance-v1"
        assert m2.version == 2
        assert m2.version_label == "Finance-v2"

    def test_lifecycle_stage_transitions_on_activate(self, isolated_model_reg):
        m1 = isolated_model_reg.create(_make_model("Legal-1", domain="legal"))
        m2 = isolated_model_reg.create(_make_model("Legal-2", domain="legal"))

        act1 = isolated_model_reg.activate(m1.model_id)
        assert act1.is_active is True
        assert act1.lifecycle_stage == ModelLifecycleStage.PRODUCTION

        act2 = isolated_model_reg.activate(m2.model_id)
        assert act2.is_active is True
        assert act2.lifecycle_stage == ModelLifecycleStage.PRODUCTION

        m1_updated = isolated_model_reg.get(m1.model_id)
        assert m1_updated.is_active is False
        assert m1_updated.lifecycle_stage == ModelLifecycleStage.DEPRECATED

    def test_predecessor_linking_and_rollback(self, isolated_model_reg):
        m1 = isolated_model_reg.create(_make_model("Sec-1", domain="security"))
        isolated_model_reg.activate(m1.model_id)

        m2 = isolated_model_reg.create(_make_model("Sec-2", domain="security"))
        assert m2.predecessor_model_id == m1.model_id

        isolated_model_reg.activate(m2.model_id)
        assert isolated_model_reg.get_active().model_id == m2.model_id

        # Rollback from m2 -> m1
        curr, restored = isolated_model_reg.rollback(m2.model_id)
        assert curr.model_id == m2.model_id
        assert restored.model_id == m1.model_id
        assert isolated_model_reg.get_active().model_id == m1.model_id

    def test_deprecate_model(self, isolated_model_reg):
        m = isolated_model_reg.create(_make_model("FAQ-1", domain="faq"))
        deprecated = isolated_model_reg.deprecate(m.model_id)
        assert deprecated.lifecycle_stage == ModelLifecycleStage.DEPRECATED
        assert deprecated.is_active is False
