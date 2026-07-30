from __future__ import annotations

import sys
from pathlib import Path
import pytest

_backend_root = Path(__file__).resolve().parent.parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from ml_studio.jobs.cost_estimator import estimate_training_cost


class TestCostEstimator:

    def test_lora_cost_estimation(self):
        res = estimate_training_cost(
            dataset_rows=500,
            file_size_bytes=500000,
            base_model="llama3.1",
            strategy="lora",
            max_steps=500,
        )
        assert res.estimated_tokens == 75000
        assert res.estimated_vram_gb == 10.0
        assert res.estimated_training_minutes > 0
        assert res.recommended_strategy == "lora"

    def test_qlora_reduces_estimated_vram(self):
        lora_res = estimate_training_cost(1000, 1000000, base_model="llama3.1", strategy="lora")
        qlora_res = estimate_training_cost(1000, 1000000, base_model="llama3.1", strategy="qlora")

        assert qlora_res.estimated_vram_gb < lora_res.estimated_vram_gb
        assert qlora_res.recommended_strategy == "qlora"

    def test_small_dataset_triggers_warning(self):
        res = estimate_training_cost(dataset_rows=20, file_size_bytes=2000)
        assert any("fewer than 50 rows" in w for w in res.warnings)
