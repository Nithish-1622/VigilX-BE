from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import AliasChoices, BaseModel, Field


class ModelStatus(str, Enum):
    ADAPTER_SAVED = "adapter_saved"      # LoRA weights saved, not yet in Ollama
    PUSHING = "pushing"                   # Being pushed to Ollama
    READY = "ready"                       # In Ollama, ready for inference
    ACTIVE = "active"                     # Currently routed as the primary local model
    INACTIVE = "inactive"                 # In Ollama but not active
    ERROR = "error"                       # Push failed


class ModelLifecycleStage(str, Enum):
    DRAFT = "draft"
    TRAINING = "training"
    EVALUATING = "evaluating"
    APPROVED = "approved"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class RegisteredModel(BaseModel):
    """A fine-tuned model entry in the model registry."""
    model_id: str
    tenant_id: str = "default"
    model_name: str                       # User-friendly name
    ollama_model_name: Optional[str]      # e.g. "vigilx-finetune-v1"
    base_model: str                       # e.g. "llama3.1"
    job_id: str                           # Source training job
    adapter_path: Optional[str]           # Path to LoRA adapter weights on disk
    domain: Optional[str] = "general"     # Domain: legal, finance, security, faq, general
    version: int = 1                      # Domain-specific version number (e.g., 1 for v1)
    version_label: Optional[str] = None   # e.g., "Finance-v2"
    status: ModelStatus = ModelStatus.ADAPTER_SAVED
    lifecycle_stage: ModelLifecycleStage = ModelLifecycleStage.DRAFT
    is_active: bool = False
    training_steps: int = 0
    final_loss: Optional[float] = None
    eval_scores: Optional[dict[str, Any]] = None
    predecessor_model_id: Optional[str] = None
    system_prompts_embedded: list[str] = Field(
        default_factory=list,
        description="Names of system prompt files embedded in the Modelfile"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    activated_at: Optional[datetime] = None
    deprecated_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None


class ModelInfo(BaseModel):
    """Public-facing model info (response schema)."""
    model_id: str
    tenant_id: str = "default"
    model_name: str
    ollama_model_name: Optional[str]
    base_model: str
    job_id: str
    domain: Optional[str] = "general"
    version: int = 1
    version_label: Optional[str] = None
    status: ModelStatus
    lifecycle_stage: ModelLifecycleStage
    is_active: bool
    training_steps: int
    final_loss: Optional[float]
    eval_scores: Optional[dict[str, Any]] = None
    predecessor_model_id: Optional[str] = None
    system_prompts_embedded: list[str]
    created_at: datetime
    activated_at: Optional[datetime] = None
    deprecated_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None


class ModelListResponse(BaseModel):
    """Response for GET /ml/models/list"""
    models: list[ModelInfo]
    total: int
    active_model: Optional[str] = None   # ollama_model_name of active model


class ModelActivateResponse(BaseModel):
    """Response for POST /ml/models/{model_id}/activate"""
    model_id: str
    ollama_model_name: str
    status: ModelStatus
    lifecycle_stage: ModelLifecycleStage
    is_active: bool
    message: str


class ModelDeactivateResponse(BaseModel):
    """Response for POST /ml/models/{model_id}/deactivate"""
    model_id: str
    is_active: bool
    message: str


class ModelDeleteResponse(BaseModel):
    """Response for DELETE /ml/models/{model_id}"""
    model_id: str
    deleted: bool
    ollama_model_removed: bool
    message: str


class ModelDeprecateResponse(BaseModel):
    """Response for POST /ml/models/{model_id}/deprecate"""
    model_id: str
    lifecycle_stage: ModelLifecycleStage
    deprecated_at: Optional[datetime] = None
    message: str


class ModelRollbackResponse(BaseModel):
    """Response for POST /ml/models/{model_id}/rollback"""
    previous_model_id: str
    restored_model_id: str
    restored_version_label: str
    status: ModelStatus
    message: str


class ModelCompareItem(BaseModel):
    model_id: str
    model_name: str
    version_label: str
    domain: str
    base_model: str
    training_steps: int
    final_loss: Optional[float]
    rouge_1: Optional[float]
    bleu_4: Optional[float]
    perplexity: Optional[float]
    latency_ms: Optional[float]
    is_active: bool


class ModelCompareResponse(BaseModel):
    models: list[ModelCompareItem]


class InferenceRequest(BaseModel):
    """Request body for POST /ml/inference/query"""
    question: str = Field(..., min_length=1, description="User question")
    user_id: str = Field(default="ml_studio_user")
    session_id: str = Field(default="ml_studio_session")
    model_override: Optional[str] = Field(
        default=None,
        description="Optionally specify an ollama model name; defaults to active model"
    )
    stream: bool = Field(default=False, description="Stream the response token-by-token")


class InferenceResponse(BaseModel):
    """Response for POST /ml/inference/query — mirrors ai-engine StandardResponse shape."""
    success: bool
    message: str
    answer: str
    model_used: str
    inference_type: str = "local"         # always "local" for ML Studio
    tokens_used: Optional[int] = None
    latency_ms: Optional[float] = None


class InferenceCompareRequest(BaseModel):
    """Request body for POST /ml/inference/compare"""
    candidate_model_id: str = Field(
        ...,
        min_length=1,
        validation_alias=AliasChoices("candidate_model_id", "candidate_model"),
    )
    prompt: str = Field(..., min_length=1)
    user_id: str = Field(default="ml_studio_user")
    session_id: str = Field(default="ml_studio_session")


class InferenceCompareResponse(BaseModel):
    """Response for POST /ml/inference/compare"""
    candidate_model_id: str
    candidate_model_name: str
    candidate_response: str
    candidate_latency_ms: Optional[float] = None
    candidate_tokens_used: Optional[int] = None
    production_model_id: str
    production_model_name: str
    production_response: str
    production_latency_ms: Optional[float] = None
    production_tokens_used: Optional[int] = None
    winner: Optional[str] = None
