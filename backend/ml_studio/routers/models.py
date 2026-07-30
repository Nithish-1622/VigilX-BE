from __future__ import annotations

import logging
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from ml_studio.core.model_registry import JobRegistry, ModelRegistry
from ml_studio.core.ollama_bridge import OllamaBridge
from ml_studio.schemas.model import (
    ModelActivateResponse,
    ModelCompareItem,
    ModelCompareResponse,
    ModelDeactivateResponse,
    ModelDeprecateResponse,
    ModelDeleteResponse,
    ModelInfo,
    ModelLifecycleStage,
    ModelListResponse,
    ModelRollbackResponse,
    ModelStatus,
)
from ml_studio.schemas.job import JobStatus
from ml_studio.security.auth import Identity, require_permission

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ml/models", tags=["ML Studio — Model Registry"])

_model_reg = ModelRegistry()
_bridge = OllamaBridge()
_job_reg = JobRegistry()


def _to_info(m) -> ModelInfo:
    return ModelInfo(
        model_id=m.model_id,
        tenant_id=getattr(m, "tenant_id", "default") or "default",
        model_name=m.model_name,
        ollama_model_name=m.ollama_model_name,
        base_model=m.base_model,
        job_id=m.job_id,
        domain=m.domain or "general",
        version=m.version or 1,
        version_label=m.version_label or f"v{m.version or 1}",
        status=m.status,
        lifecycle_stage=m.lifecycle_stage or ModelLifecycleStage.DRAFT,
        is_active=m.is_active,
        training_steps=m.training_steps,
        final_loss=m.final_loss,
        eval_scores=m.eval_scores,
        predecessor_model_id=m.predecessor_model_id,
        system_prompts_embedded=m.system_prompts_embedded,
        created_at=m.created_at,
        activated_at=m.activated_at,
        deprecated_at=m.deprecated_at,
        archived_at=m.archived_at,
    )


@router.get(
    "/list",
    response_model=ModelListResponse,
    summary="List all registered fine-tuned models",
)
async def list_models(
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> ModelListResponse:
    models = _model_reg.list_all(tenant_id=tenant_id)
    active = _model_reg.get_active(tenant_id=tenant_id)
    return ModelListResponse(
        models=[_to_info(m) for m in models],
        total=len(models),
        active_model=active.ollama_model_name if active else None,
    )


@router.get(
    "/compare",
    response_model=ModelCompareResponse,
    summary="Compare evaluation metrics across multiple models",
)
async def compare_models(
    ids: str = Query(..., description="Comma-separated list of model_ids to compare"),
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> ModelCompareResponse:
    model_ids = [i.strip() for i in ids.split(",") if i.strip()]
    if not model_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide at least one model_id in 'ids' query parameter.",
        )

    items: list[ModelCompareItem] = []
    for mid in model_ids:
        m = _model_reg.get(mid, tenant_id=tenant_id)
        if m:
            scores = m.eval_scores or {}
            items.append(
                ModelCompareItem(
                    model_id=m.model_id,
                    model_name=m.model_name,
                    version_label=m.version_label or f"v{m.version}",
                    domain=m.domain or "general",
                    base_model=m.base_model,
                    training_steps=m.training_steps,
                    final_loss=m.final_loss,
                    rouge_1=scores.get("rouge_1"),
                    bleu_4=scores.get("bleu_4"),
                    perplexity=scores.get("perplexity"),
                    latency_ms=scores.get("latency_ms"),
                    is_active=m.is_active,
                )
            )

    return ModelCompareResponse(models=items)


@router.get(
    "/{model_id}",
    response_model=ModelInfo,
    summary="Get a specific model's details",
)
async def get_model(
    model_id: str,
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> ModelInfo:
    model = _model_reg.get(model_id, tenant_id=tenant_id)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{model_id}' not found.",
        )
    return _to_info(model)


@router.post(
    "/{model_id}/activate",
    response_model=ModelActivateResponse,
    summary="Activate a fine-tuned model",
)
async def activate_model(
    model_id: str,
    ident: Identity = Depends(require_permission("ml_studio.activate_model")),
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> ModelActivateResponse:
    model = _model_reg.get(model_id, tenant_id=tenant_id)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{model_id}' not found.",
        )

    if model.status == ModelStatus.ERROR:
        logger.warning("Model %s is in ERROR state; attempting activation anyway.", model_id)

    if not model.ollama_model_name or model.status == ModelStatus.ADAPTER_SAVED:
        logger.info("Pushing model %s to Ollama before activation...", model_id)
        try:
            ollama_name = _bridge.create_model(
                model_id=model_id,
                job_name=model.model_name,
            )
        except RuntimeError as exc:
            _model_reg.update(model_id, tenant_id=tenant_id, status=ModelStatus.ERROR)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to push model to Ollama: {exc}",
            ) from exc
        model = _model_reg.get(model_id, tenant_id=tenant_id)

    if not model or not model.ollama_model_name:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ollama model name not set after push attempt.",
        )

    activated = _model_reg.activate(model_id, tenant_id=tenant_id)
    if activated is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate model in registry.",
        )

    _job_reg.update(activated.job_id, tenant_id=tenant_id, status=JobStatus.ACTIVE)

    logger.info("Model activated: %s → %s", model_id, activated.ollama_model_name)
    return ModelActivateResponse(
        model_id=model_id,
        ollama_model_name=activated.ollama_model_name,
        status=activated.status,
        lifecycle_stage=activated.lifecycle_stage,
        is_active=True,
        message=f"Model '{activated.model_name}' ({activated.version_label}) is now active in production.",
    )


@router.post(
    "/{model_id}/rollback",
    response_model=ModelRollbackResponse,
    summary="Rollback to predecessor model version",
)
async def rollback_model(
    model_id: str,
    ident: Identity = Depends(require_permission("ml_studio.rollback_model")),
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> ModelRollbackResponse:
    curr, restored = _model_reg.rollback(model_id, tenant_id=tenant_id)
    if not curr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{model_id}' not found.",
        )

    if not restored:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model '{model_id}' does not have an active predecessor to rollback to.",
        )

    _job_reg.update(restored.job_id, tenant_id=tenant_id, status=JobStatus.ACTIVE)

    return ModelRollbackResponse(
        previous_model_id=model_id,
        restored_model_id=restored.model_id,
        restored_version_label=restored.version_label or restored.model_name,
        status=restored.status,
        message=f"Successfully rolled back from '{curr.model_name}' to '{restored.version_label}'.",
    )


@router.post(
    "/{model_id}/deactivate",
    response_model=ModelDeactivateResponse,
    summary="Deactivate a model",
)
async def deactivate_model(
    model_id: str,
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> ModelDeactivateResponse:
    model = _model_reg.get(model_id, tenant_id=tenant_id)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{model_id}' not found.",
        )

    _model_reg.update(model_id, tenant_id=tenant_id, is_active=False, status=ModelStatus.READY, lifecycle_stage=ModelLifecycleStage.APPROVED)
    return ModelDeactivateResponse(
        model_id=model_id,
        is_active=False,
        message=f"Model '{model.model_name}' deactivated.",
    )


@router.post(
    "/{model_id}/deprecate",
    response_model=ModelDeprecateResponse,
    summary="Mark a model as deprecated",
)
async def deprecate_model(
    model_id: str,
    ident: Identity = Depends(require_permission("ml_studio.deprecate_model")),
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> ModelDeprecateResponse:
    model = _model_reg.get(model_id, tenant_id=tenant_id)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{model_id}' not found.",
        )

    deprecated = _model_reg.deprecate(model_id, tenant_id=tenant_id)
    if deprecated is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to deprecate model.")

    return ModelDeprecateResponse(
        model_id=model_id,
        lifecycle_stage=ModelLifecycleStage.DEPRECATED,
        deprecated_at=deprecated.deprecated_at,
        message=f"Model '{model.model_name}' marked as deprecated.",
    )


@router.delete(
    "/{model_id}",
    response_model=ModelDeleteResponse,
    summary="Delete a registered model",
)
async def delete_model(model_id: str) -> ModelDeleteResponse:
    tenant_id: str = Header(default="default", alias="X-Tenant-ID")
    model = _model_reg.get(model_id, tenant_id=tenant_id)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{model_id}' not found.",
        )

    ollama_removed = False
    if model.ollama_model_name:
        ollama_removed = _bridge.remove_model(model.ollama_model_name)

    if model.adapter_path:
        import shutil
        from pathlib import Path
        adapter_dir = Path(model.adapter_path).parent
        if adapter_dir.exists():
            try:
                shutil.rmtree(str(adapter_dir))
            except OSError as exc:
                logger.warning("Could not remove adapter dir %s: %s", adapter_dir, exc)

    _model_reg.delete(model_id, tenant_id=tenant_id)
    return ModelDeleteResponse(
        model_id=model_id,
        deleted=True,
        ollama_model_removed=ollama_removed,
        message=f"Model '{model.model_name}' deleted.",
    )
