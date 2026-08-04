from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    QUEUED = "queued"
    VALIDATING = "validating"
    PREPROCESSING = "preprocessing"
    PREPARING = "preparing"
    TRAINING = "training"
    SAVING = "saving"
    EVALUATING = "evaluating"
    BENCHMARKING = "benchmarking"
    PENDING_APPROVAL = "pending_approval"
    DEPLOYING = "deploying"
    PUSHING_TO_OLLAMA = "pushing_to_ollama"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TrainingConfig(BaseModel):
    """Configuration for a fine-tuning job."""
    dataset_id: str = Field(..., description="ID of the uploaded dataset to train on")
    job_name: str = Field(..., description="Human-readable name for this job")
    base_model: str = Field(default="llama3.1", description="Ollama base model name")
    training_strategy: str = Field(default="lora", description="Training strategy: lora, qlora, rag_embed")
    lora_rank: int = Field(default=8, ge=1, le=128, description="LoRA rank (r)")
    lora_alpha: int = Field(default=16, description="LoRA scaling alpha")
    lora_dropout: float = Field(default=0.05, ge=0.0, le=0.5)
    max_steps: int = Field(default=500, ge=10, le=5000, description="Max training steps")
    batch_size: int = Field(default=4, ge=1, le=32)
    learning_rate: float = Field(default=2e-4)
    max_seq_length: int = Field(default=512, ge=64, le=4096)
    pii_redaction: bool = Field(default=True, description="Enable automated PII scanning & redaction during preprocessing")
    auto_approve: bool = Field(default=False, description="Auto-approve model deployment without human gate")
    eval_min_rouge1: float = Field(default=0.40, description="Minimum ROUGE-1 score threshold to pass evaluation")
    eval_min_bleu4: float = Field(default=0.25, description="Minimum BLEU-4 score threshold to pass evaluation")
    push_to_ollama: bool = Field(default=True, description="Auto-push adapter to Ollama on completion")


class StartJobRequest(BaseModel):
    """Request body for POST /ml/jobs/start"""
    config: TrainingConfig


class TrainingJob(BaseModel):
    """Full training job record (stored in registry)."""
    job_id: str
    tenant_id: str = "default"
    job_name: str
    status: JobStatus = JobStatus.QUEUED
    config: TrainingConfig
    progress: float = Field(default=0.0, ge=0.0, le=100.0, description="Progress percentage")
    current_step: int = 0
    total_steps: int = 0
    loss: Optional[float] = None
    log_tail: list[str] = Field(default_factory=list, description="Last 20 log lines")
    adapter_path: Optional[str] = None
    ollama_model_name: Optional[str] = None
    model_id: Optional[str] = None
    pipeline_stage_results: dict[str, Any] = Field(default_factory=dict, description="Detailed per-stage results")
    preprocessing_report: Optional[dict[str, Any]] = None
    eval_scores: Optional[dict[str, Any]] = None
    benchmark_result: Optional[dict[str, Any]] = None
    approval_required: bool = True
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    report_artifacts: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class JobStatusResponse(BaseModel):
    """Response for GET /ml/jobs/{job_id}/status"""
    job_id: str
    tenant_id: str = "default"
    job_name: str
    status: JobStatus
    progress: float
    current_step: int
    total_steps: int
    loss: Optional[float]
    log_tail: list[str]
    adapter_path: Optional[str]
    ollama_model_name: Optional[str]
    pipeline_stage_results: dict[str, Any] = Field(default_factory=dict)
    preprocessing_report: Optional[dict[str, Any]] = None
    eval_scores: Optional[dict[str, Any]] = None
    benchmark_result: Optional[dict[str, Any]] = None
    approval_required: bool = True
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    report_artifacts: Optional[dict[str, Any]] = None
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime


class JobListResponse(BaseModel):
    """Response for GET /ml/jobs/list"""
    jobs: list[JobStatusResponse]
    total: int
    running: int
    completed: int
    failed: int


class JobStartResponse(BaseModel):
    """Response for POST /ml/jobs/start"""
    job_id: str
    job_name: str
    status: JobStatus
    message: str
    config: TrainingConfig


class JobCancelResponse(BaseModel):
    """Response for DELETE /ml/jobs/{job_id}"""
    job_id: str
    cancelled: bool
    message: str


class JobApproveRequest(BaseModel):
    """Request body for POST /ml/jobs/{job_id}/approve"""
    approved_by: str = Field(default="admin_user")
    comment: Optional[str] = None


class JobApproveResponse(BaseModel):
    """Response for POST /ml/jobs/{job_id}/approve"""
    job_id: str
    status: JobStatus
    approved_by: str
    message: str


class JobRejectRequest(BaseModel):
    """Request body for POST /ml/jobs/{job_id}/reject"""
    rejected_by: str = Field(default="admin_user")
    reason: str = Field(..., min_length=1, max_length=500)


class JobRejectResponse(BaseModel):
    """Response for POST /ml/jobs/{job_id}/reject"""
    job_id: str
    status: JobStatus
    rejected_by: str
    message: str


class JobReportResponse(BaseModel):
    """Response for GET /ml/jobs/{job_id}/report"""
    summary: dict[str, Any] = Field(default_factory=dict)
    pipeline_stage_results: dict[str, Any] = Field(default_factory=dict)
    evaluation: dict[str, Any] = Field(default_factory=dict)
    benchmark: dict[str, Any] = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)
