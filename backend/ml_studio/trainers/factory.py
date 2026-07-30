from __future__ import annotations

from typing import Any
from ml_studio.trainers.base import BaseTrainer, ProgressCallback
from ml_studio.trainers.lora import LoRATrainer
from ml_studio.trainers.qlora import QLoRATrainer
from ml_studio.trainers.rag_embed import RAGEmbedTrainer


def get_trainer(
    strategy: str,
    job_id: str,
    base_model: str,
    output_dir: str,
    progress_callback: ProgressCallback | None = None,
) -> BaseTrainer:
    """
    Factory method to instantiate appropriate trainer strategy implementation.
    """
    strat = strategy.lower().strip()
    if strat in ("lora", "standard"):
        return LoRATrainer(job_id, base_model, output_dir, progress_callback)
    elif strat in ("qlora", "quantized"):
        return QLoRATrainer(job_id, base_model, output_dir, progress_callback)
    elif strat in ("rag", "rag_embed", "embedding"):
        return RAGEmbedTrainer(job_id, base_model, output_dir, progress_callback)
    else:
        # Default to LoRA
        return LoRATrainer(job_id, base_model, output_dir, progress_callback)
