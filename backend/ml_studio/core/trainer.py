from __future__ import annotations

"""
ML Studio — LoRA Fine-Tuning Trainer
=====================================
Uses HuggingFace `transformers` + `peft` + `trl` to perform
parameter-efficient fine-tuning (LoRA/QLoRA) on a local base model.

The trainer runs inside an asyncio background task (via asyncio.to_thread)
so the FastAPI event loop is never blocked.

Dataset format expected:
    {"prompt": "...", "completion": "..."}

Training flow:
    1. Load dataset rows from DatasetManager
    2. Tokenize with the model's tokenizer (prompt + completion concatenated)
    3. Build LoraConfig from TrainingConfig
    4. Run SFTTrainer for max_steps
    5. Save adapter to registry/adapters/<job_id>/
    6. Update JobRegistry at every checkpoint (every 10 steps)
    7. Optionally push to Ollama via OllamaBridge
"""

import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from ml_studio.config import ml_settings
from ml_studio.core.dataset_manager import DatasetManager
from ml_studio.core.model_registry import JobRegistry, ModelRegistry
from ml_studio.schemas.job import JobStatus, TrainingConfig, TrainingJob
from ml_studio.schemas.model import ModelStatus, RegisteredModel

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Lazy imports — HuggingFace stack is optional at import time.
# If not installed, jobs are rejected with a clear error.
# ─────────────────────────────────────────────────────────────────────────────

def _check_hf_stack() -> tuple[bool, str]:
    """Return (available, error_message)."""
    missing = []
    for pkg in ("transformers", "peft", "trl", "torch", "datasets"):
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        return False, f"Missing HuggingFace packages: {', '.join(missing)}. Run: pip install transformers peft trl torch datasets"
    return True, ""


# ─────────────────────────────────────────────────────────────────────────────
# Progress callback (writes to JobRegistry every N steps)
# ─────────────────────────────────────────────────────────────────────────────

class _ProgressCallback:
    """
    Custom HuggingFace TrainerCallback that syncs progress to JobRegistry.
    We avoid inheriting from TrainerCallback to keep the import lazy.
    """

    def __init__(self, job_registry: JobRegistry, job_id: str, log_prefix: str = "") -> None:
        self.job_registry = job_registry
        self.job_id = job_id
        self.log_prefix = log_prefix

    # Called by SFTTrainer via monkey-patch below
    def on_step_end(self, args, state, control, **kwargs) -> None:
        step = state.global_step
        total = state.max_steps
        loss = state.log_history[-1].get("loss") if state.log_history else None
        self.job_registry.update_progress(self.job_id, step, total, loss)
        if step % 25 == 0 or step == total:
            log_line = f"[step {step}/{total}] loss={loss:.5f}" if loss else f"[step {step}/{total}]"
            self.job_registry.append_log(self.job_id, log_line)
            logger.info("%s %s", self.log_prefix, log_line)

    def on_train_end(self, args, state, control, **kwargs) -> None:
        self.job_registry.append_log(self.job_id, "Training loop complete.")

    def on_log(self, args, state, control, logs=None, **kwargs) -> None:
        if logs:
            msg = " | ".join(f"{k}={v:.4f}" if isinstance(v, float) else f"{k}={v}" for k, v in logs.items())
            self.job_registry.append_log(self.job_id, msg)


# ─────────────────────────────────────────────────────────────────────────────
# Main Trainer class
# ─────────────────────────────────────────────────────────────────────────────

class LocalModelTrainer:
    """
    Orchestrates LoRA fine-tuning for ML Studio.

    Usage (from async context):
        trainer = LocalModelTrainer()
        await asyncio.to_thread(trainer.run, job_id, config)
    """

    def __init__(self) -> None:
        self._dataset_mgr = DatasetManager()
        self._job_reg = JobRegistry()
        self._model_reg = ModelRegistry()

    # ── Public entry point ────────────────────────────────────────────────────

    def run(self, job_id: str, config: TrainingConfig) -> str:
        """
        Blocking training function — must be called via asyncio.to_thread().

        Returns:
            adapter_path (str) — path where the LoRA adapter was saved.

        Raises:
            RuntimeError: On unrecoverable errors (logs written to registry).
        """
        log = lambda msg: (
            logger.info("[job:%s] %s", job_id, msg),
            self._job_reg.append_log(job_id, msg),
        )

        try:
            # ── 0. Check HF stack ───────────────────────────────────────────
            available, err = _check_hf_stack()
            if not available:
                self._fail(job_id, err)
                raise RuntimeError(err)

            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
            from peft import LoraConfig, get_peft_model, TaskType
            from trl import SFTTrainer, DataCollatorForCompletionOnlyLM
            from transformers import TrainerCallback
            import datasets as hf_datasets

            # ── 1. Status → preparing ───────────────────────────────────────
            self._job_reg.update(
                job_id,
                status=JobStatus.PREPARING,
                started_at=datetime.utcnow().isoformat(),
            )
            log("Loading dataset rows from registry...")

            # ── 2. Load dataset ─────────────────────────────────────────────
            rows = self._dataset_mgr.load_rows(config.dataset_id)
            log(f"Loaded {len(rows)} valid training rows.")

            # ── 3. Resolve base model path via Ollama GGUF or HF Hub ────────
            # ML Studio uses HuggingFace Hub model IDs mapped from common Ollama names.
            hf_model_id = self._resolve_hf_model(config.base_model)
            log(f"Resolved base model: '{config.base_model}' → HuggingFace '{hf_model_id}'")

            # ── 4. Determine device ─────────────────────────────────────────
            if ml_settings.device_map == "auto":
                if torch.cuda.is_available():
                    device = "cuda"
                elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                    device = "mps"
                else:
                    device = "cpu"
            else:
                device = ml_settings.device_map

            log(f"Device: {device} | LoRA rank={config.lora_rank} | Steps={config.max_steps}")

            # ── 5. Load tokenizer ───────────────────────────────────────────
            log("Loading tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(hf_model_id, trust_remote_code=True)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            # ── 6. Format rows as "### Instruction:\n...\n### Response:\n..." ─
            def _format(row: dict) -> str:
                return (
                    f"### Instruction:\n{row['prompt'].strip()}\n\n"
                    f"### Response:\n{row['completion'].strip()}"
                )

            formatted_texts = [_format(r) for r in rows]
            hf_dataset = hf_datasets.Dataset.from_dict({"text": formatted_texts})

            # ── 7. Load model ───────────────────────────────────────────────
            log("Loading base model (this may take a few minutes)...")
            load_kwargs: dict = {
                "trust_remote_code": True,
                "low_cpu_mem_usage": True,
            }
            if device == "cuda":
                load_kwargs["torch_dtype"] = torch.float16
                load_kwargs["device_map"] = "auto"
            elif device == "mps":
                load_kwargs["torch_dtype"] = torch.float16
            else:
                load_kwargs["torch_dtype"] = torch.float32

            model = AutoModelForCausalLM.from_pretrained(hf_model_id, **load_kwargs)
            model.config.use_cache = False
            log("Base model loaded.")

            # ── 8. LoRA config ──────────────────────────────────────────────
            peft_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=config.lora_rank,
                lora_alpha=config.lora_alpha,
                lora_dropout=config.lora_dropout,
                bias="none",
                target_modules=["q_proj", "v_proj"],  # Standard for LLaMA/Mistral/Gemma
            )
            model = get_peft_model(model, peft_config)
            trainable, total_params = model.get_nb_trainable_parameters()
            log(f"LoRA applied. Trainable params: {trainable:,} / {total_params:,} ({100*trainable/total_params:.2f}%)")

            # ── 9. Training arguments ───────────────────────────────────────
            adapter_dir = Path(ml_settings.adapter_store_path) / job_id
            adapter_dir.mkdir(parents=True, exist_ok=True)

            training_args = TrainingArguments(
                output_dir=str(adapter_dir / "checkpoints"),
                max_steps=config.max_steps,
                per_device_train_batch_size=config.batch_size,
                learning_rate=config.learning_rate,
                fp16=(device == "cuda"),
                bf16=False,
                logging_steps=10,
                save_steps=config.max_steps,    # Save only at end
                save_total_limit=1,
                report_to="none",               # Never report to wandb/tensorboard
                no_cuda=(device == "cpu"),
                dataloader_num_workers=0,
            )

            # ── 10. Progress callback ───────────────────────────────────────
            class _HFCallback(TrainerCallback):
                def __init__(self_, cb: _ProgressCallback):
                    self_._cb = cb

                def on_step_end(self_, args, state, control, **kwargs):
                    self_._cb.on_step_end(args, state, control, **kwargs)

                def on_train_end(self_, args, state, control, **kwargs):
                    self_._cb.on_train_end(args, state, control, **kwargs)

                def on_log(self_, args, state, control, logs=None, **kwargs):
                    self_._cb.on_log(args, state, control, logs=logs, **kwargs)

            progress_cb = _ProgressCallback(self._job_reg, job_id, log_prefix=f"[job:{job_id[:8]}]")
            hf_callback = _HFCallback(progress_cb)

            # ── 11. Status → training ───────────────────────────────────────
            self._job_reg.update(job_id, status=JobStatus.TRAINING)

            trainer = SFTTrainer(
                model=model,
                train_dataset=hf_dataset,
                dataset_text_field="text",
                max_seq_length=config.max_seq_length,
                args=training_args,
                callbacks=[hf_callback],
            )

            log("Starting training loop...")
            trainer.train()
            log("Training complete. Saving LoRA adapter...")

            # ── 12. Save adapter ────────────────────────────────────────────
            self._job_reg.update(job_id, status=JobStatus.SAVING)
            adapter_save_path = adapter_dir / "adapter"
            model.save_pretrained(str(adapter_save_path))
            tokenizer.save_pretrained(str(adapter_save_path))
            log(f"Adapter saved to: {adapter_save_path}")

            # ── 13. Register model ──────────────────────────────────────────
            job = self._job_reg.get(job_id)
            final_loss = job.loss if job else None
            model_id = str(uuid.uuid4())
            registered = RegisteredModel(
                model_id=model_id,
                model_name=f"{config.job_name}-adapter",
                ollama_model_name=None,
                base_model=config.base_model,
                job_id=job_id,
                adapter_path=str(adapter_save_path),
                status=ModelStatus.ADAPTER_SAVED,
                is_active=False,
                training_steps=config.max_steps,
                final_loss=final_loss,
                created_at=datetime.utcnow(),
            )
            self._model_reg.create(registered)
            log(f"Model registered with ID: {model_id}")

            # ── 14. Finalize job ────────────────────────────────────────────
            self._job_reg.update(
                job_id,
                status=JobStatus.COMPLETED,
                adapter_path=str(adapter_save_path),
                model_id=model_id,
                completed_at=datetime.utcnow().isoformat(),
                progress=100.0,
            )

            # ── 15. Auto-push to Ollama if configured ───────────────────────
            if config.push_to_ollama:
                self._job_reg.update(job_id, status=JobStatus.PUSHING_TO_OLLAMA)
                log("Pushing adapter to Ollama...")
                try:
                    from ml_studio.core.ollama_bridge import OllamaBridge
                    bridge = OllamaBridge()
                    ollama_name = bridge.create_model(model_id=model_id, job_name=config.job_name)
                    self._job_reg.update(job_id, ollama_model_name=ollama_name, status=JobStatus.COMPLETED)
                    log(f"Ollama model created: {ollama_name}")
                except Exception as push_err:
                    logger.warning("[job:%s] Ollama push failed (non-fatal): %s", job_id, push_err)
                    self._job_reg.append_log(job_id, f"WARNING: Ollama push failed: {push_err}")
                    self._job_reg.update(job_id, status=JobStatus.COMPLETED)

            logger.info("[job:%s] Finished successfully.", job_id)
            return str(adapter_save_path)

        except Exception as exc:  # noqa: BLE001
            error_msg = str(exc)
            logger.exception("[job:%s] Training failed: %s", job_id, error_msg)
            self._fail(job_id, error_msg)
            raise

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _fail(self, job_id: str, error: str) -> None:
        self._job_reg.update(
            job_id,
            status=JobStatus.FAILED,
            error_message=error[:500],
            completed_at=datetime.utcnow().isoformat(),
        )
        self._job_reg.append_log(job_id, f"FAILED: {error[:200]}")

    @staticmethod
    def _resolve_hf_model(ollama_name: str) -> str:
        """
        Map common Ollama short model names → HuggingFace Hub model IDs.
        Users can override by specifying the full HF ID directly.
        """
        _MAP = {
            "llama3.1":       "meta-llama/Llama-3.1-8B",
            "llama3.1:8b":    "meta-llama/Llama-3.1-8B",
            "llama3.1:70b":   "meta-llama/Llama-3.1-70B",
            "llama3.2":       "meta-llama/Llama-3.2-3B",
            "llama3.2:3b":    "meta-llama/Llama-3.2-3B",
            "llama2":         "meta-llama/Llama-2-7b-hf",
            "llama2:7b":      "meta-llama/Llama-2-7b-hf",
            "mistral":        "mistralai/Mistral-7B-v0.1",
            "mistral:7b":     "mistralai/Mistral-7B-v0.1",
            "gemma2":         "google/gemma-2-9b",
            "gemma2:9b":      "google/gemma-2-9b",
            "gemma2:2b":      "google/gemma-2-2b",
            "phi3":           "microsoft/Phi-3-mini-4k-instruct",
            "phi3:mini":      "microsoft/Phi-3-mini-4k-instruct",
            "qwen2.5":        "Qwen/Qwen2.5-7B",
            "qwen2.5:7b":     "Qwen/Qwen2.5-7B",
        }
        name_lower = ollama_name.strip().lower()
        if name_lower in _MAP:
            return _MAP[name_lower]
        # If it looks like a HF model ID (contains "/"), use as-is
        if "/" in ollama_name:
            return ollama_name
        # Fallback: try it as-is and let HF throw a clear error
        logger.warning("Unknown base model '%s' — using as HuggingFace model ID directly.", ollama_name)
        return ollama_name
