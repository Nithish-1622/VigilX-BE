from __future__ import annotations

import sys
from pathlib import Path
import pytest

_backend_root = Path(__file__).resolve().parent.parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from ml_studio.trainers.factory import get_trainer
from ml_studio.trainers.lora import LoRATrainer
from ml_studio.trainers.qlora import QLoRATrainer
from ml_studio.trainers.rag_embed import RAGEmbedTrainer
from ml_studio.trainers.base import TrainerStepMetrics


SAMPLE_DATASET = [
    {"prompt": f"Prompt {i}", "completion": f"Completion {i}"}
    for i in range(1, 21)
]


class TestTrainers:

    def test_factory_returns_correct_strategy(self, tmp_path):
        out_dir = str(tmp_path)
        t_lora = get_trainer("lora", "j-1", "llama3.1", out_dir)
        t_qlora = get_trainer("qlora", "j-2", "llama3.1", out_dir)
        t_rag = get_trainer("rag_embed", "j-3", "llama3.1", out_dir)

        assert isinstance(t_lora, LoRATrainer)
        assert isinstance(t_qlora, QLoRATrainer)
        assert isinstance(t_rag, RAGEmbedTrainer)

    def test_lora_training_flow(self, tmp_path):
        out_dir = str(tmp_path)
        metrics_logged = []

        def _cb(m: TrainerStepMetrics):
            metrics_logged.append(m)

        trainer = LoRATrainer("j-lora", "llama3.1", out_dir, progress_callback=_cb)
        trainer.prepare(SAMPLE_DATASET, {"lora_rank": 16})
        res = trainer.train(steps=10, batch_size=2, learning_rate=2e-4)

        assert res["strategy"] == "lora"
        assert res["final_loss"] < 2.0
        assert len(metrics_logged) == 10
        assert metrics_logged[-1].step == 10

        adapter_path = trainer.save_adapter()
        assert Path(adapter_path).exists()
        assert (Path(adapter_path) / "adapter_config.json").exists()

    def test_qlora_training_flow(self, tmp_path):
        out_dir = str(tmp_path)
        trainer = QLoRATrainer("j-qlora", "llama3.1", out_dir)
        trainer.prepare(SAMPLE_DATASET, {"quant_bits": 4})
        res = trainer.train(steps=5, batch_size=4, learning_rate=1e-4)

        assert res["strategy"] == "qlora"
        assert res["quant_bits"] == 4

        adapter_path = trainer.save_adapter()
        assert (Path(adapter_path) / "qlora_adapter.bin").exists()

    def test_rag_embed_flow(self, tmp_path):
        out_dir = str(tmp_path)
        trainer = RAGEmbedTrainer("j-rag", "llama3.1", out_dir)
        trainer.prepare(SAMPLE_DATASET, {"embedding_dimension": 768})
        res = trainer.train(steps=3, batch_size=1, learning_rate=0.0)

        assert res["strategy"] == "rag_embed"
        assert res["indexed_documents"] == 20

        adapter_path = trainer.save_adapter()
        assert (Path(adapter_path) / "vector_index.bin").exists()
