from __future__ import annotations

import logging
from typing import Optional
from fastapi import APIRouter, File, Header, HTTPException, Query, UploadFile, status

from ml_studio.core.dataset_manager import DatasetManager
from ml_studio.datasets.synthetic_generator import augment_dataset_with_ollama
from ml_studio.datasets.detector import classify_dataset
from ml_studio.datasets.pii_detector import PIIDetector
from ml_studio.datasets.tokenizer import analyze_sequence_lengths
from ml_studio.jobs.cost_estimator import estimate_training_cost
from ml_studio.schemas.dataset import (
    DatasetAugmentResponse,
    DatasetDeleteResponse,
    DatasetListResponse,
    DatasetUploadResponse,
)
from ml_studio.security.audit import AuditLogger

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ml/datasets", tags=["ML Studio — Datasets"])

_mgr = DatasetManager()
_audit = AuditLogger()


@router.post(
    "/upload",
    response_model=DatasetUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a training dataset",
)
async def upload_dataset(
    file: UploadFile = File(..., description="CSV or JSONL dataset file"),
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> DatasetUploadResponse:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided.",
        )

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    try:
        result = _mgr.ingest(filename=file.filename, content=content, tenant_id=tenant_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    logger.info(
        "Dataset uploaded: id=%s filename=%s rows=%d",
        result.dataset_id, result.filename, result.row_count,
    )
    _audit.log(
        "dataset_upload",
        tenant_id=tenant_id,
        details={"dataset_id": result.dataset_id, "filename": result.filename, "row_count": result.row_count},
    )
    return result


@router.get(
    "/list",
    response_model=DatasetListResponse,
    summary="List all uploaded datasets",
)
async def list_datasets(
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> DatasetListResponse:
    records = _mgr.list_datasets(tenant_id=tenant_id)
    return DatasetListResponse(datasets=records, total=len(records))


@router.get(
    "/{dataset_id}/analyze",
    summary="Smart Dataset Analyzer insights",
)
async def analyze_dataset_insights(
    dataset_id: str,
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> dict:
    """
    Returns smart insights: domain classification, PII scan summary, token statistics, and prompt recommendation.
    """
    record = _mgr.get_dataset(dataset_id, tenant_id=tenant_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset '{dataset_id}' not found.",
        )

    rows = _mgr.load_rows(dataset_id, tenant_id=tenant_id)
    detector = PIIDetector()
    _, pii_counts = detector.redact_dataset_rows(rows)
    token_stats = analyze_sequence_lengths(rows)
    classification = classify_dataset(rows)

    return {
        "dataset_id": dataset_id,
        "filename": record.filename,
        "total_rows": len(rows),
        "domain": classification.domain_type.value,
        "domain_confidence": classification.confidence,
        "detected_keywords": classification.detected_keywords,
        "recommended_prompt_template": classification.recommended_system_prompt_type,
        "pii": {
            "pii_detected": sum(pii_counts.values()) > 0,
            "counts": pii_counts,
        },
        "token_statistics": {
            "avg_tokens_per_sample": token_stats.avg_tokens,
            "max_tokens_per_sample": token_stats.max_tokens,
            "p95_tokens_per_sample": token_stats.p95_tokens,
        },
    }


@router.get(
    "/{dataset_id}/cost-estimate",
    summary="Pre-flight resource and training cost estimation",
)
async def get_cost_estimate(
    dataset_id: str,
    base_model: str = Query(default="llama3.1"),
    strategy: str = Query(default="lora"),
    max_steps: int = Query(default=500),
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> dict:
    """
    Estimate estimated tokens, training duration, VRAM usage, and recommended GPU before starting a job.
    """
    record = _mgr.get_dataset(dataset_id, tenant_id=tenant_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset '{dataset_id}' not found.",
        )

    res = estimate_training_cost(
        dataset_rows=record.row_count,
        file_size_bytes=record.file_size_bytes,
        base_model=base_model,
        strategy=strategy,
        max_steps=max_steps,
    )
    return {
        "dataset_id": dataset_id,
        "base_model": base_model,
        "strategy": strategy,
        "estimated_tokens": res.estimated_tokens,
        "estimated_training_minutes": res.estimated_training_minutes,
        "estimated_vram_gb": res.estimated_vram_gb,
        "recommended_strategy": res.recommended_strategy,
        "recommended_gpu": res.recommended_gpu,
        "can_run_on_current_hardware": res.can_run_on_current_hardware,
        "warnings": res.warnings,
    }


@router.get(
    "/{dataset_id}",
    response_model=DatasetListResponse,
    summary="Get a single dataset's metadata",
)
async def get_dataset(
    dataset_id: str,
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> DatasetListResponse:
    record = _mgr.get_dataset(dataset_id, tenant_id=tenant_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset '{dataset_id}' not found.",
        )
    return DatasetListResponse(datasets=[record], total=1)


@router.delete(
    "/{dataset_id}",
    response_model=DatasetDeleteResponse,
    summary="Delete a dataset",
)
async def delete_dataset(
    dataset_id: str,
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> DatasetDeleteResponse:
    deleted = _mgr.delete_dataset(dataset_id, tenant_id=tenant_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset '{dataset_id}' not found.",
        )
    logger.info("Dataset deleted: %s", dataset_id)
    _audit.log("dataset_deleted", tenant_id=tenant_id, details={"dataset_id": dataset_id})
    return DatasetDeleteResponse(
        dataset_id=dataset_id,
        deleted=True,
        message="Dataset removed from disk and registry.",
    )


@router.post(
    "/{dataset_id}/augment",
    response_model=DatasetAugmentResponse,
    summary="Augment a dataset with synthetic Q&A pairs using local Ollama",
)
async def augment_dataset(
    dataset_id: str,
    target_rows: int = Query(default=5000, ge=10, le=500000),
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> DatasetAugmentResponse:
    record = _mgr.get_dataset(dataset_id, tenant_id=tenant_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset '{dataset_id}' not found.",
        )

    augmented_id, generated = await augment_dataset_with_ollama(
        dataset_id=dataset_id,
        target_rows=target_rows,
        tenant_id=tenant_id,
    )
    return DatasetAugmentResponse(
        source_dataset_id=dataset_id,
        augmented_dataset_id=augmented_id,
        tenant_id=tenant_id,
        target_rows=target_rows,
        generated_rows=generated,
        message=f"Generated {generated} synthetic rows and created augmented dataset '{augmented_id}'.",
    )
