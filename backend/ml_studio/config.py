from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# Resolve .env from repo root (four levels up from this file)
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path, override=False)

# ─────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────
_ML_STUDIO_DIR = Path(__file__).resolve().parent
_REGISTRY_DIR = _ML_STUDIO_DIR / "registry"
_DATASET_DIR = _REGISTRY_DIR / "datasets"
_ADAPTER_DIR = _REGISTRY_DIR / "adapters"
_REPORTS_DIR = _REGISTRY_DIR / "reports"
_PROMPT_DIR = _ML_STUDIO_DIR / "prompts"
_AI_ENGINE_PROMPT_DIR = _ML_STUDIO_DIR.parent / "ai-engine" / "prompts"


@dataclass(frozen=True)
class MLStudioSettings:
    # ── Service ──────────────────────────────────────────────
    app_name: str = os.getenv("ML_STUDIO_APP_NAME", "VigilX ML Studio")
    app_version: str = os.getenv("ML_STUDIO_APP_VERSION", "1.0.0")
    log_level: str = os.getenv("ML_STUDIO_LOG_LEVEL", "INFO")
    port: int = int(os.getenv("ML_STUDIO_PORT", "8002"))

    # ── Ollama ───────────────────────────────────────────────
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_api_version: str = os.getenv("OLLAMA_API_VERSION", "v1")

    # ── Default training parameters ──────────────────────────
    default_base_model: str = os.getenv("ML_STUDIO_BASE_MODEL", "llama3.1")
    default_lora_rank: int = int(os.getenv("ML_STUDIO_LORA_RANK", "8"))
    default_lora_alpha: int = int(os.getenv("ML_STUDIO_LORA_ALPHA", "16"))
    default_lora_dropout: float = float(os.getenv("ML_STUDIO_LORA_DROPOUT", "0.05"))
    default_max_steps: int = int(os.getenv("ML_STUDIO_MAX_STEPS", "500"))
    default_batch_size: int = int(os.getenv("ML_STUDIO_BATCH_SIZE", "4"))
    default_learning_rate: float = float(os.getenv("ML_STUDIO_LR", "2e-4"))
    default_max_seq_length: int = int(os.getenv("ML_STUDIO_MAX_SEQ_LEN", "512"))

    # ── Device ───────────────────────────────────────────────
    # "auto" → detect CUDA → MPS → CPU; "cpu" → force CPU; "cuda" → force CUDA
    device_map: str = os.getenv("ML_STUDIO_DEVICE_MAP", "auto")

    # ── Paths (as dynamic properties for environment isolation) ───────────
    @property
    def registry_dir(self) -> str:
        return os.getenv("ML_STUDIO_REGISTRY_DIR", str(_REGISTRY_DIR))

    @property
    def dataset_store_path(self) -> str:
        return os.getenv("ML_STUDIO_DATASET_STORE", str(_DATASET_DIR))

    @property
    def adapter_store_path(self) -> str:
        return os.getenv("ML_STUDIO_ADAPTER_STORE", str(_ADAPTER_DIR))

    @property
    def reports_store_path(self) -> str:
        return os.getenv("ML_STUDIO_REPORTS_STORE", str(_REPORTS_DIR))

    @property
    def prompt_dir(self) -> str:
        return os.getenv("ML_STUDIO_PROMPT_DIR", str(_PROMPT_DIR))

    @property
    def ai_engine_prompt_dir(self) -> str:
        return os.getenv("ML_STUDIO_AI_ENGINE_PROMPT_DIR", str(_AI_ENGINE_PROMPT_DIR))

    @property
    def jobs_registry_file(self) -> str:
        return str(Path(self.registry_dir) / "jobs.json")

    @property
    def models_registry_file(self) -> str:
        return str(Path(self.registry_dir) / "models.json")

    # ── Security ─────────────────────────────────────────────
    # Maximum dataset file size in bytes (default: 100 MB)
    max_dataset_size_bytes: int = int(os.getenv("ML_STUDIO_MAX_DATASET_MB", "100")) * 1024 * 1024
    allowed_dataset_extensions: tuple[str, ...] = (".jsonl", ".csv")

    # ── Inference temperature (same as cloud model) ───────────
    inference_temperature: float = float(os.getenv("ML_STUDIO_INFERENCE_TEMP", "0.2"))


ml_settings = MLStudioSettings()


def ensure_directories() -> None:
    """Create all required runtime directories if they don't exist."""
    for d in [
        Path(ml_settings.registry_dir),
        Path(ml_settings.dataset_store_path),
        Path(ml_settings.adapter_store_path),
        Path(ml_settings.reports_store_path),
    ]:
        d.mkdir(parents=True, exist_ok=True)
