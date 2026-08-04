from __future__ import annotations

import json
import random
from typing import Any

from ml_studio.config import ml_settings
from ml_studio.core.dataset_manager import DatasetManager
from ml_studio.core.inference_client import LocalInferenceClient
from ml_studio.datasets.cleaner import clean_dataset_rows
from ml_studio.datasets.pii_detector import PIIDetector


async def augment_dataset_with_ollama(
    dataset_id: str,
    target_rows: int,
    tenant_id: str = "default",
    model_override: str | None = None,
) -> tuple[str, int]:
    mgr = DatasetManager()
    client = LocalInferenceClient()

    record = mgr.get_dataset(dataset_id, tenant_id=tenant_id)
    if record is None:
        raise FileNotFoundError(f"Dataset '{dataset_id}' not found.")

    seed_rows = mgr.load_rows(dataset_id, tenant_id=tenant_id)
    existing = len(seed_rows)
    if existing >= target_rows:
        new_name = f"{record.filename.rsplit('.', 1)[0]}_copy.jsonl"
        new_ds = mgr.create_from_rows(filename=new_name, rows=seed_rows, tenant_id=tenant_id)
        return new_ds.dataset_id, 0

    to_generate = target_rows - existing
    generated: list[dict[str, str]] = []

    health = await client.health_check()
    if not health.get("ollama_reachable"):
        raise RuntimeError("Ollama is not reachable; cannot generate synthetic data.")

    base_model = model_override or getattr(ml_settings, "default_base_model", "llama3.1")
    attempts = 0
    max_attempts = max(25, (to_generate // 5) * 10)

    while len(generated) < to_generate and attempts < max_attempts:
        attempts += 1
        seed = random.choice(seed_rows)
        seed_prompt = str(seed.get("prompt", "")).strip()
        seed_completion = str(seed.get("completion", "")).strip()
        if not seed_prompt or not seed_completion:
            continue

        ask = {
            "instruction": "Generate exactly 5 distinct but similar Q&A training pairs in JSON array format.",
            "schema": [{"prompt": "string", "completion": "string"}],
            "rules": [
                "Return ONLY valid JSON.",
                "No markdown.",
                "No extra keys.",
                "No PII.",
            ],
            "seed_example": {"prompt": seed_prompt, "completion": seed_completion},
        }
        question = json.dumps(ask, ensure_ascii=False)

        result = await client.generate(question=question, model_override=base_model)
        answer = (result.get("answer") or "").strip()

        try:
            parsed = json.loads(answer)
        except Exception:
            continue

        if not isinstance(parsed, list):
            continue

        for item in parsed:
            if len(generated) >= to_generate:
                break
            if not isinstance(item, dict):
                continue
            p = str(item.get("prompt", "")).strip()
            c = str(item.get("completion", "")).strip()
            if not p or not c:
                continue
            generated.append({"prompt": p, "completion": c})

    cleaned = clean_dataset_rows(generated)
    detector = PIIDetector()
    redacted, _ = detector.redact_dataset_rows(cleaned)

    combined = seed_rows + redacted
    out_name = f"{record.filename.rsplit('.', 1)[0]}_augmented.jsonl"
    new_ds = mgr.create_from_rows(filename=out_name, rows=combined, tenant_id=tenant_id)
    return new_ds.dataset_id, len(redacted)
