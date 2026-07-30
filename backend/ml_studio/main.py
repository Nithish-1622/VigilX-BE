from __future__ import annotations

"""
ML Studio — FastAPI Application Entry Point
============================================
Runs on Port 8002 (configurable via ML_STUDIO_PORT env var).

Start with:
    uvicorn ml_studio.main:app --port 8002 --reload

Or alongside the main AI engine by adding to run_servers.bat:
    start uvicorn ml_studio.main:app --port 8002
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi import Header
from fastapi.middleware.cors import CORSMiddleware

# ── Path setup — allow `from ml_studio.x import y` when running from backend/ ──
_backend_root = Path(__file__).resolve().parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from ml_studio.config import ensure_directories, ml_settings

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, ml_settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Routers ────────────────────────────────────────────────────────────────────
from ml_studio.routers.datasets import router as datasets_router
from ml_studio.routers.jobs import router as jobs_router
from ml_studio.routers.models import router as models_router
from ml_studio.routers.inference import router as inference_router
from ml_studio.routers.telemetry import router as telemetry_router


# ── Lifespan ───────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Startup: ensure registry directories and files exist."""
    logger.info("Starting %s v%s", ml_settings.app_name, ml_settings.app_version)
    ensure_directories()

    # Ensure registry JSON files exist (prevents read errors on first boot)
    from ml_studio.core.model_registry import JobRegistry, ModelRegistry
    JobRegistry()   # Constructor-free; registry file created on first write
    ModelRegistry()

    # Log Ollama connectivity check (non-blocking)
    from ml_studio.core.inference_client import LocalInferenceClient
    client = LocalInferenceClient()
    try:
        health = await client.health_check()
        if health["ollama_reachable"]:
            active = health.get("active_model")
            logger.info(
                "Ollama reachable at %s | Active model: %s",
                ml_settings.ollama_base_url,
                active or "none",
            )
        else:
            logger.warning(
                "Ollama not reachable at %s — inference will fail until 'ollama serve' is running.",
                ml_settings.ollama_base_url,
            )
    except Exception as exc:
        logger.warning("Ollama health check failed at startup: %s", exc)

    logger.info(
        "ML Studio ready | Datasets: %s | Adapters: %s",
        ml_settings.dataset_store_path,
        ml_settings.adapter_store_path,
    )
    yield
    logger.info("Shutting down %s", ml_settings.app_name)


# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=ml_settings.app_name,
    version=ml_settings.app_version,
    description="""
## VigilX ML Studio

**Runtime Local Model Trainer & Fine-Tuner**

Train and deploy locally fine-tuned LLMs on sensitive criminal intelligence data
without sending a single byte to the cloud.

### Security Model
- ✅ All training data stays on-premise
- ✅ LoRA fine-tuning runs on local hardware (GPU or CPU)  
- ✅ Trained model served by local Ollama instance
- ✅ Same system prompts as cloud AI engine → identical behaviour
- ✅ Air-gap compatible (no internet required after initial model pull)

### Workflow
1. `POST /ml/datasets/upload` — Upload a CSV/JSONL training dataset
2. `POST /ml/jobs/start` — Start a LoRA fine-tuning job
3. `GET /ml/jobs/{id}/status` — Poll training progress
4. `POST /ml/models/{id}/activate` — Push to Ollama and activate
5. `POST /ml/inference/query` — Query the local model

### Docs
- OpenAPI: `/docs`
- Redoc: `/redoc`
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ── CORS ───────────────────────────────────────────────────────────────────────

is_catalyst = bool(os.getenv("X_ZOHO_CATALYST_LISTEN_PORT")) or os.getenv("ENVIRONMENT") == "production"
if not is_catalyst:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            o.strip().rstrip("/")
            for o in os.getenv(
                "CORS_ALLOWED_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
            ).split(",")
            if o.strip()
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# ── Register routers ───────────────────────────────────────────────────────────

app.include_router(datasets_router)
app.include_router(jobs_router)
app.include_router(models_router)
app.include_router(inference_router)
app.include_router(telemetry_router)


# ── Root endpoints ─────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root(
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> dict:
    return {
        "status": "success",
        "service": ml_settings.app_name,
        "version": ml_settings.app_version,
        "docs": "/docs",
        "security": "air-gapped local inference — no data leaves the perimeter",
    }


@app.get("/health", tags=["Health"])
async def health(
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> dict:
    from ml_studio.core.inference_client import LocalInferenceClient
    from ml_studio.core.model_registry import ModelRegistry, JobRegistry

    ollama_health = await LocalInferenceClient().health_check()
    models = ModelRegistry().list_all(tenant_id=tenant_id)
    jobs = JobRegistry().list_all(tenant_id=tenant_id)

    return {
        "status": "ok",
        "service": ml_settings.app_name,
        "version": ml_settings.app_version,
        "ollama": ollama_health,
        "stats": {
            "total_models": len(models),
            "active_model": next((m.ollama_model_name for m in models if m.is_active), None),
            "total_jobs": len(jobs),
            "completed_jobs": sum(1 for j in jobs if j.status.value == "completed"),
        },
    }
