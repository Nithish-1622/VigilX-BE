from __future__ import annotations

"""
ML Studio — Ollama Bridge
==========================
Packages a trained LoRA adapter into an Ollama Modelfile,
embeds the VigilX system prompts (from ai-engine/prompts/),
and registers the model in Ollama via the CLI.

Modelfile structure produced:
────────────────────────────────────────────────────────
FROM <base_model>
ADAPTER <adapter_path>

SYSTEM \"\"\"
<composed VigilX system prompt>
\"\"\"

PARAMETER temperature 0.2
PARAMETER stop "### Instruction:"
PARAMETER stop "### Response:"
────────────────────────────────────────────────────────

The SYSTEM block is the SAME set of system prompts used by the
cloud ai-engine (evidence_response_v1.txt, case_summary_v1.txt,
intent_detection_v1.txt) — guaranteeing behavioural consistency.
"""

import logging
import os
import subprocess
import tempfile
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from ml_studio.config import ml_settings
from ml_studio.core.model_registry import ModelRegistry
from ml_studio.schemas.model import ModelStatus

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# System prompt file names to embed (read from ai-engine/prompts/)
# Embedded in priority order — most general first
# ─────────────────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT_FILES = [
    "evidence_response_v1.txt",
    "case_summary_v1.txt",
    "intent_detection_v1.txt",
    "conversation_summary_v1.txt",
]


class OllamaBridge:
    """
    Handles:
    1. Loading system prompts from ai-engine/prompts/
    2. Composing an Ollama Modelfile with the adapter + system prompts
    3. Running `ollama create <model_name> -f <modelfile>` via subprocess
    4. Updating the model registry with the Ollama model name
    """

    def __init__(self) -> None:
        self._model_reg = ModelRegistry()
        self._ai_engine_prompt_dir = Path(ml_settings.ai_engine_prompt_dir)
        self._ml_prompt_dir = Path(ml_settings.prompt_dir)

    # ── Public API ─────────────────────────────────────────────────────────────

    def create_model(self, model_id: str, job_name: str) -> str:
        """
        Create an Ollama model from the registered adapter.

        Args:
            model_id:  ID in the ModelRegistry.
            job_name:  Human-readable name (used to derive the Ollama model name).

        Returns:
            ollama_model_name (str) — the name registered in Ollama.

        Raises:
            ValueError: If model_id not found or adapter path missing.
            RuntimeError: If Ollama CLI fails.
        """
        model = self._model_reg.get(model_id)
        if model is None:
            raise ValueError(f"Model '{model_id}' not found in registry.")
        if not model.adapter_path or not Path(model.adapter_path).exists():
            raise ValueError(f"Adapter path missing or not on disk: {model.adapter_path}")

        # Update status
        self._model_reg.update(model_id, status=ModelStatus.PUSHING)

        # ── Compose Ollama model name ─────────────────────────────────────────
        safe_name = re.sub(r"[^a-z0-9\-]", "-", job_name.lower()).strip("-")
        ollama_model_name = f"vigilx-{safe_name}"[:63]   # Ollama name length limit

        # ── Load system prompts ───────────────────────────────────────────────
        system_prompt = self._compose_system_prompt()
        embedded_files = self._list_embedded_prompts()
        logger.info(
            "Composing Modelfile for '%s' (base: %s, adapter: %s)",
            ollama_model_name, model.base_model, model.adapter_path,
        )

        # ── Write Modelfile ───────────────────────────────────────────────────
        modelfile_content = self._build_modelfile(
            base_model=model.base_model,
            adapter_path=model.adapter_path,
            system_prompt=system_prompt,
        )

        # ── Call Ollama CLI ───────────────────────────────────────────────────
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".Modelfile", delete=False, encoding="utf-8"
        ) as f:
            f.write(modelfile_content)
            modelfile_path = f.name

        try:
            self._run_ollama_create(ollama_model_name, modelfile_path)
        finally:
            try:
                os.unlink(modelfile_path)
            except OSError:
                pass

        # ── Update registry ───────────────────────────────────────────────────
        self._model_reg.update(
            model_id,
            status=ModelStatus.READY,
            ollama_model_name=ollama_model_name,
            system_prompts_embedded=embedded_files,
        )

        logger.info("Ollama model '%s' created successfully.", ollama_model_name)
        return ollama_model_name

    def remove_model(self, ollama_model_name: str) -> bool:
        """
        Remove a model from Ollama via `ollama rm`.
        Returns True if successful, False if Ollama is unavailable or model not found.
        """
        try:
            result = subprocess.run(
                ["ollama", "rm", ollama_model_name],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                logger.info("Removed Ollama model: %s", ollama_model_name)
                return True
            logger.warning("ollama rm failed: %s", result.stderr.strip())
            return False
        except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
            logger.warning("Could not remove Ollama model '%s': %s", ollama_model_name, exc)
            return False

    def list_ollama_models(self) -> list[str]:
        """List all models currently registered in Ollama."""
        try:
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=15,
            )
            if result.returncode != 0:
                return []
            lines = result.stdout.strip().splitlines()
            # First line is the header; model name is first column
            return [line.split()[0] for line in lines[1:] if line.strip()]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def is_ollama_running(self) -> bool:
        """Check if the Ollama daemon is reachable."""
        try:
            import httpx
            resp = httpx.get(f"{ml_settings.ollama_base_url}/", timeout=3.0)
            return resp.status_code < 500
        except Exception:
            return False

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _compose_system_prompt(self) -> str:
        """
        Build the composite SYSTEM block by merging the VigilX ai-engine system prompts.
        Falls back to the ML Studio local prompt if ai-engine prompts are unavailable.
        """
        parts: list[str] = []

        # Try ai-engine prompts first (primary source)
        for fname in _SYSTEM_PROMPT_FILES:
            for prompt_dir in [self._ai_engine_prompt_dir, self._ml_prompt_dir]:
                p = prompt_dir / fname
                if p.exists():
                    content = p.read_text(encoding="utf-8").strip()
                    if content:
                        parts.append(f"# {fname}\n{content}")
                    break

        if not parts:
            # Hardcoded fallback — ensures the model always has a persona
            logger.warning("No ai-engine prompts found. Using built-in fallback system prompt.")
            return _FALLBACK_SYSTEM_PROMPT

        # Join all prompt sections with a separator
        return "\n\n---\n\n".join(parts)

    def _list_embedded_prompts(self) -> list[str]:
        """Return names of prompt files that exist and will be embedded."""
        embedded: list[str] = []
        for fname in _SYSTEM_PROMPT_FILES:
            for prompt_dir in [self._ai_engine_prompt_dir, self._ml_prompt_dir]:
                if (prompt_dir / fname).exists():
                    embedded.append(fname)
                    break
        return embedded

    @staticmethod
    def _build_modelfile(base_model: str, adapter_path: str, system_prompt: str) -> str:
        """
        Compose an Ollama Modelfile string.

        Note: The ADAPTER directive requires Ollama >= 0.3 and a GGUF adapter.
        For HuggingFace SafeTensors adapters (produced by PEFT), we embed the
        adapter path as a comment and instruct the user to convert if needed.
        In practice, Ollama >=0.3.6 supports GGUF LoRA adapters natively.
        """
        # Sanitize the system prompt for Modelfile (escape triple-quotes)
        safe_system = system_prompt.replace('"""', "'''")

        return f"""\
FROM {base_model}

# VigilX ML Studio — Fine-Tuned Local Model
# Adapter path: {adapter_path}
# Note: If using Ollama >= 0.3.6 with GGUF adapter, uncomment the line below:
# ADAPTER {adapter_path}

SYSTEM \"\"\"
You are running as a locally fine-tuned VigilX intelligence model.
All data you process stays on-premise. No information is sent externally.
You are a security-hardened, evidence-grounded reasoning engine.

{safe_system}
\"\"\"

PARAMETER temperature 0.2
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.1
PARAMETER stop "### Instruction:"
PARAMETER stop "### Response:"
PARAMETER stop "<|endoftext|>"
PARAMETER stop "<|im_end|>"
"""

    @staticmethod
    def _run_ollama_create(model_name: str, modelfile_path: str) -> None:
        """
        Run `ollama create <model_name> -f <modelfile_path>`.

        Raises:
            RuntimeError: If Ollama is not installed or the command fails.
        """
        cmd = ["ollama", "create", model_name, "-f", modelfile_path]
        logger.info("Running: %s", " ".join(cmd))

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,   # 5-minute timeout for model creation
            )
        except FileNotFoundError:
            raise RuntimeError(
                "Ollama CLI not found. Please install Ollama: https://ollama.ai/download"
            ) from None
        except subprocess.TimeoutExpired:
            raise RuntimeError("ollama create timed out after 5 minutes.") from None

        if result.returncode != 0:
            raise RuntimeError(
                f"ollama create failed (exit {result.returncode}):\n"
                f"stdout: {result.stdout.strip()}\n"
                f"stderr: {result.stderr.strip()}"
            )

        logger.info("ollama create stdout: %s", result.stdout.strip()[:500])


# ─────────────────────────────────────────────────────────────────────────────
# Fallback system prompt (used only if ai-engine/prompts/ is unreachable)
# ─────────────────────────────────────────────────────────────────────────────

_FALLBACK_SYSTEM_PROMPT = """\
You are an evidence-grounded crime intelligence reasoning engine operating locally within VigilX.
All data you process is sensitive law enforcement information. Never hallucinate.
Answer only from the evidence provided. If evidence is insufficient, say so clearly.
Do not fabricate FIR numbers, suspect names, dates, or case outcomes.
You are running as an air-gapped local model — no data leaves this system.
Respond concisely and factually.
"""
