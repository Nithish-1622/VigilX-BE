from __future__ import annotations

import logging
import time
from fastapi import APIRouter, Header, HTTPException, status

from ml_studio.core.inference_client import LocalInferenceClient
from ml_studio.core.model_registry import ModelRegistry
from ml_studio.schemas.model import (
    InferenceCompareRequest,
    InferenceCompareResponse,
    InferenceRequest,
    InferenceResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ml/inference", tags=["ML Studio — Local Inference"])

_client = LocalInferenceClient()
_model_reg = ModelRegistry()


@router.post(
    "/query",
    response_model=InferenceResponse,
    summary="Query the active local model",
    description=(
        "Send a question to the currently active locally fine-tuned model via Ollama. "
        "The response shape mirrors the existing `/ai/ask` endpoint for drop-in compatibility. "
        "No data is sent to any cloud provider — all inference runs on-premise."
    ),
)
async def query_local_model(
    req: InferenceRequest,
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> InferenceResponse:
    """
    Query the active fine-tuned local model.

    **Security guarantee:** This endpoint routes exclusively to the local Ollama
    instance. No data leaves the server.

    **Prerequisites:**
    1. Upload a dataset → `POST /ml/datasets/upload`
    2. Train a model  → `POST /ml/jobs/start`
    3. Activate model → `POST /ml/models/{id}/activate`
    """
    # ── Check Ollama health ────────────────────────────────────────────────────
    health = await _client.health_check()
    if not health["ollama_reachable"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Ollama is not running or unreachable at the configured URL. "
                "Start it with: `ollama serve`"
            ),
        )

    # ── Resolve model (active or override) ────────────────────────────────────
    model_name = req.model_override
    if not model_name:
        active = _model_reg.get_active(tenant_id=tenant_id)
        if active is None or not active.ollama_model_name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "No active local model found. "
                    "Activate one via POST /ml/models/{model_id}/activate"
                ),
            )
        model_name = active.ollama_model_name

    # ── Inference ─────────────────────────────────────────────────────────────
    try:
        result = await _client.generate(
            question=req.question,
            model_override=model_name,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    logger.info(
        "Local inference: user=%s session=%s model=%s latency=%.1fms",
        req.user_id, req.session_id,
        result["model_used"], result.get("latency_ms", 0),
    )

    return InferenceResponse(
        success=True,
        message="ok",
        answer=result["answer"],
        model_used=result["model_used"],
        inference_type="local",
        tokens_used=result.get("tokens_used"),
        latency_ms=result.get("latency_ms"),
    )


@router.post(
    "/compare",
    response_model=InferenceCompareResponse,
    summary="Side-by-side inference: candidate vs production model",
)
async def compare_models(
    req: InferenceCompareRequest,
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> InferenceCompareResponse:
    health = await _client.health_check()
    if not health["ollama_reachable"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ollama is not running or unreachable.",
        )

    candidate = _model_reg.get(req.candidate_model_id, tenant_id=tenant_id)
    if candidate is None or not candidate.ollama_model_name:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate model not found or not pushed to Ollama.",
        )

    production = _model_reg.get_active(tenant_id=tenant_id)
    if production is None or not production.ollama_model_name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No active production model found for this tenant.",
        )

    cand_res = await _client.generate(question=req.prompt, model_override=candidate.ollama_model_name)
    prod_res = await _client.generate(question=req.prompt, model_override=production.ollama_model_name)

    return InferenceCompareResponse(
        candidate_model_id=candidate.model_id,
        candidate_model_name=candidate.model_name,
        candidate_response=cand_res["answer"],
        candidate_latency_ms=cand_res.get("latency_ms"),
        candidate_tokens_used=cand_res.get("tokens_used"),
        production_model_id=production.model_id,
        production_model_name=production.model_name,
        production_response=prod_res["answer"],
        production_latency_ms=prod_res.get("latency_ms"),
        production_tokens_used=prod_res.get("tokens_used"),
        winner=None,
    )


@router.get(
    "/health",
    summary="Check local inference health",
    description="Returns Ollama connectivity status and which model is currently active.",
)
async def inference_health() -> dict:
    """
    Health check for the local inference subsystem.

    Returns:
    - Whether Ollama is reachable
    - The currently active model name
    - The Ollama base URL being used
    """
    return await _client.health_check()
