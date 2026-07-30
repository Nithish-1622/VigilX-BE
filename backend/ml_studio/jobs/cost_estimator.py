from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass
class CostEstimateResult:
    dataset_rows: int
    estimated_tokens: int
    estimated_training_minutes: float
    estimated_vram_gb: float
    recommended_strategy: str
    recommended_gpu: str
    can_run_on_current_hardware: bool
    warnings: list[str]


def estimate_training_cost(
    dataset_rows: int,
    file_size_bytes: int,
    base_model: str = "llama3.1",
    strategy: str = "lora",
    max_steps: int = 500,
    batch_size: int = 4,
) -> CostEstimateResult:
    """
    Pre-flight resource and hardware requirement estimator.
    """
    # Estimate average 150 tokens per prompt-completion pair
    estimated_tokens = int(dataset_rows * 150)
    warnings: list[str] = []

    model_lower = base_model.lower()
    if "70b" in model_lower:
        base_vram = 40.0
        sec_per_step = 1.2
    elif "13b" in model_lower or "14b" in model_lower or "9b" in model_lower:
        base_vram = 14.0
        sec_per_step = 0.5
    else:  # 7b / 8b default
        base_vram = 10.0
        sec_per_step = 0.25

    strat_lower = strategy.lower().strip()
    if strat_lower == "qlora":
        vram_multiplier = 0.45  # 4-bit quantization saves ~55% VRAM
        recommended_strategy = "qlora"
    elif strat_lower == "rag_embed":
        vram_multiplier = 0.15
        sec_per_step = 0.05
        recommended_strategy = "rag_embed"
    else:  # lora
        vram_multiplier = 1.0
        recommended_strategy = "lora"

    estimated_vram_gb = round(base_vram * vram_multiplier, 1)
    total_seconds = max_steps * sec_per_step
    estimated_minutes = round(total_seconds / 60.0, 1)

    # Hardware recommendation
    if estimated_vram_gb <= 8.0:
        recommended_gpu = "RTX 3060 / RTX 4060 (8GB VRAM)"
    elif estimated_vram_gb <= 16.0:
        recommended_gpu = "RTX 4080 / RTX 4090 (16GB - 24GB VRAM)"
    else:
        recommended_gpu = "NVIDIA A100 / H100 (40GB+ VRAM)"

    # Warnings checks
    if dataset_rows < 50:
        warnings.append("Dataset has fewer than 50 rows. Accuracy may be low; consider synthetic augmentation.")

    if estimated_vram_gb > 16.0 and strat_lower == "lora":
        warnings.append(f"Estimated VRAM ({estimated_vram_gb} GB) is high. Recommend switching strategy to QLoRA (4-bit quantization).")
        recommended_strategy = "qlora"

    return CostEstimateResult(
        dataset_rows=dataset_rows,
        estimated_tokens=estimated_tokens,
        estimated_training_minutes=estimated_minutes,
        estimated_vram_gb=estimated_vram_gb,
        recommended_strategy=recommended_strategy,
        recommended_gpu=recommended_gpu,
        can_run_on_current_hardware=True,
        warnings=warnings,
    )
