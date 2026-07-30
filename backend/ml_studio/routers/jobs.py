from __future__ import annotations

import asyncio
import logging
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import FileResponse

from ml_studio.core.dataset_manager import DatasetManager
from ml_studio.core.model_registry import JobRegistry
from ml_studio.jobs.orchestrator import PipelineOrchestrator
from ml_studio.jobs.reporting import build_canonical_report, generate_report_artifacts
from ml_studio.schemas.job import (
    JobApproveRequest,
    JobApproveResponse,
    JobCancelResponse,
    JobListResponse,
    JobRejectRequest,
    JobRejectResponse,
    JobReportResponse,
    JobStartResponse,
    JobStatus,
    JobStatusResponse,
    StartJobRequest,
    TrainingJob,
)
from ml_studio.security.auth import Identity, require_permission

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ml/jobs", tags=["ML Studio — Training Jobs"])

_job_reg = JobRegistry()
_dataset_mgr = DatasetManager()

# Active asyncio tasks (job_id → Task) for cancellation support
_running_tasks: dict[str, asyncio.Task] = {}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _to_response(job: TrainingJob) -> JobStatusResponse:
    return JobStatusResponse(
        job_id=job.job_id,
        tenant_id=getattr(job, "tenant_id", "default") or "default",
        job_name=job.job_name,
        status=job.status,
        progress=job.progress,
        current_step=job.current_step,
        total_steps=job.total_steps,
        loss=job.loss,
        log_tail=job.log_tail,
        adapter_path=job.adapter_path,
        ollama_model_name=job.ollama_model_name,
        pipeline_stage_results=job.pipeline_stage_results or {},
        preprocessing_report=job.preprocessing_report,
        eval_scores=job.eval_scores,
        benchmark_result=job.benchmark_result,
        approval_required=job.approval_required,
        approved_by=job.approved_by,
        approved_at=job.approved_at,
        report_artifacts=getattr(job, "report_artifacts", None),
        error_message=job.error_message,
        started_at=job.started_at,
        completed_at=job.completed_at,
        created_at=job.created_at,
    )


async def _run_pipeline_task(job_id: str, config, tenant_id: str) -> None:
    """Asyncio task wrapper — runs the multi-stage pipeline orchestrator."""
    try:
        orchestrator = PipelineOrchestrator()
        await asyncio.to_thread(orchestrator.run_pipeline, job_id, config, tenant_id)
    except Exception as exc:
        logger.error("Pipeline task %s raised: %s", job_id, exc)
    finally:
        _running_tasks.pop(job_id, None)


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post(
    "/start",
    response_model=JobStartResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start a fine-tuning job",
    description=(
        "Kick off an end-to-end multi-stage training pipeline (Validation → Preprocessing → Training → Evaluation → Benchmarking → Approval → Deployment). "
        "The job runs asynchronously — poll `/ml/jobs/{job_id}/status` for progress."
    ),
)
async def start_job(
    req: StartJobRequest,
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> JobStartResponse:
    config = req.config

    dataset = _dataset_mgr.get_dataset(config.dataset_id, tenant_id=tenant_id)
    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset '{config.dataset_id}' not found. Upload it first via POST /ml/datasets/upload",
        )

    if dataset.row_count < 10:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Dataset has only {dataset.row_count} valid rows. Minimum 10 required for training.",
        )

    # Guard: max 1 running job at a time
    all_jobs = _job_reg.list_all(tenant_id=tenant_id)
    running_statuses = {
        JobStatus.QUEUED, JobStatus.VALIDATING, JobStatus.PREPROCESSING,
        JobStatus.PREPARING, JobStatus.TRAINING, JobStatus.SAVING,
        JobStatus.EVALUATING, JobStatus.BENCHMARKING, JobStatus.DEPLOYING, JobStatus.PUSHING_TO_OLLAMA
    }
    running = [j for j in all_jobs if j.status in running_statuses]
    if running:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Job '{running[0].job_id}' is already running (status: {running[0].status.value}). "
                "Wait for it to complete before starting a new job."
            ),
        )

    job = _job_reg.create(config=config, job_name=config.job_name, tenant_id=tenant_id)
    logger.info(
        "Training pipeline created: id=%s name=%s dataset=%s strategy=%s",
        job.job_id, job.job_name, config.dataset_id, config.training_strategy,
    )

    task = asyncio.create_task(_run_pipeline_task(job.job_id, config, tenant_id))
    _running_tasks[job.job_id] = task

    return JobStartResponse(
        job_id=job.job_id,
        job_name=job.job_name,
        status=JobStatus.QUEUED,
        message=(
            f"Training job '{job.job_name}' queued. "
            f"Dataset: {dataset.row_count} rows | Strategy: {config.training_strategy} | Base model: {config.base_model}. "
            f"Poll GET /ml/jobs/{job.job_id}/status for progress."
        ),
        config=config,
    )


@router.post(
    "/{job_id}/approve",
    response_model=JobApproveResponse,
    summary="Approve a paused job for deployment",
)
async def approve_job(
    job_id: str,
    req: JobApproveRequest,
    ident: Identity = Depends(require_permission("ml_studio.approve_job")),
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> JobApproveResponse:
    """
    Approve a model job currently paused at PENDING_APPROVAL and resume deployment to Ollama.
    """
    job = _job_reg.get(job_id, tenant_id=tenant_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )

    if job.status != JobStatus.PENDING_APPROVAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job '{job_id}' is in status '{job.status.value}' — only PENDING_APPROVAL jobs can be approved.",
        )

    orchestrator = PipelineOrchestrator()
    task = asyncio.create_task(asyncio.to_thread(orchestrator.approve_job, job_id, req.approved_by, tenant_id))
    _running_tasks[job_id] = task

    return JobApproveResponse(
        job_id=job_id,
        status=JobStatus.DEPLOYING,
        approved_by=req.approved_by,
        message=f"Job '{job_id}' approved by '{req.approved_by}'. Deployment to Ollama resumed.",
    )


@router.post(
    "/{job_id}/reject",
    response_model=JobRejectResponse,
    summary="Reject a paused job with a reason",
)
async def reject_job(
    job_id: str,
    req: JobRejectRequest,
    ident: Identity = Depends(require_permission("ml_studio.reject_job")),
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> JobRejectResponse:
    job = _job_reg.get(job_id, tenant_id=tenant_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )

    orchestrator = PipelineOrchestrator()
    await asyncio.to_thread(orchestrator.reject_job, job_id, req.reason, req.rejected_by, tenant_id)
    return JobRejectResponse(
        job_id=job_id,
        status=JobStatus.FAILED,
        rejected_by=req.rejected_by,
        message=f"Job '{job_id}' rejected by '{req.rejected_by}'.",
    )


@router.get(
    "/list",
    response_model=JobListResponse,
    summary="List all training jobs",
)
async def list_jobs(
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> JobListResponse:
    jobs = _job_reg.list_all(tenant_id=tenant_id)
    running_statuses = {
        JobStatus.QUEUED, JobStatus.VALIDATING, JobStatus.PREPROCESSING,
        JobStatus.PREPARING, JobStatus.TRAINING, JobStatus.SAVING,
        JobStatus.EVALUATING, JobStatus.BENCHMARKING, JobStatus.DEPLOYING, JobStatus.PUSHING_TO_OLLAMA
    }
    return JobListResponse(
        jobs=[_to_response(j) for j in jobs],
        total=len(jobs),
        running=sum(1 for j in jobs if j.status in running_statuses),
        completed=sum(1 for j in jobs if j.status in (JobStatus.COMPLETED, JobStatus.ACTIVE)),
        failed=sum(1 for j in jobs if j.status == JobStatus.FAILED),
    )


@router.get(
    "/{job_id}/status",
    response_model=JobStatusResponse,
    summary="Get training job status",
)
async def get_job_status(
    job_id: str,
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> JobStatusResponse:
    job = _job_reg.get(job_id, tenant_id=tenant_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )
    return _to_response(job)


@router.get(
    "/{job_id}/report",
    response_model=JobReportResponse,
    summary="Get canonical JSON training report",
)
async def get_job_report(
    job_id: str,
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> JobReportResponse:
    job = _job_reg.get(job_id, tenant_id=tenant_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job '{job_id}' not found.")
    return build_canonical_report(job)


@router.get(
    "/{job_id}/report.html",
    summary="Download HTML training report",
)
async def get_job_report_html(
    job_id: str,
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> FileResponse:
    job = _job_reg.get(job_id, tenant_id=tenant_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job '{job_id}' not found.")
    if not getattr(job, "report_artifacts", None):
        meta = generate_report_artifacts(job)
        _job_reg.update(job_id, tenant_id=tenant_id, report_artifacts=meta)
    html_path = (job.report_artifacts or {}).get("html_path") if getattr(job, "report_artifacts", None) else None
    if not html_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="HTML report not available.")
    return FileResponse(html_path, media_type="text/html")


@router.get(
    "/{job_id}/report.pdf",
    summary="Download PDF training report",
)
async def get_job_report_pdf(
    job_id: str,
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> FileResponse:
    job = _job_reg.get(job_id, tenant_id=tenant_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job '{job_id}' not found.")
    if not getattr(job, "report_artifacts", None):
        meta = generate_report_artifacts(job)
        _job_reg.update(job_id, tenant_id=tenant_id, report_artifacts=meta)
    meta = job.report_artifacts or {}
    if not meta.get("pdf_ok", False):
        err = meta.get("pdf_error") or "PDF generation failed."
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)
    pdf_path = meta.get("pdf_path")
    if not pdf_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF report not available.")
    return FileResponse(pdf_path, media_type="application/pdf")


@router.delete(
    "/{job_id}",
    response_model=JobCancelResponse,
    summary="Cancel or remove a job",
)
async def cancel_job(
    job_id: str,
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> JobCancelResponse:
    job = _job_reg.get(job_id, tenant_id=tenant_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )

    cancelled = False
    message = "Job removed from registry."

    task = _running_tasks.get(job_id)
    if task and not task.done():
        task.cancel()
        _running_tasks.pop(job_id, None)
        _job_reg.update(job_id, tenant_id=tenant_id, status=JobStatus.CANCELLED)
        cancelled = True
        message = "Running job cancelled."
        logger.info("Cancelled running job: %s", job_id)

    _job_reg.delete(job_id, tenant_id=tenant_id)
    return JobCancelResponse(job_id=job_id, cancelled=cancelled, message=message)
