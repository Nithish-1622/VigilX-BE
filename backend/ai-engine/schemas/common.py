from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None


class Citation(BaseModel):
    source: str
    reference_id: str | None = None
    snippet: str | None = None
    score: float | None = None


class ResponseMetadata(BaseModel):
    intent: str | None = None
    query_plan: str | None = None
    evidence_sources: int = 0
    api_records: int = 0
    langgraph_enabled: bool = False
    correlation_id: str | None = None
    confidence: str = "low"
    evidence_threshold_met: bool = False
    evidence_required: int = 0
    rag_citations: int = 0
    sql_citations: int = 0
    evidence_source_breakdown: dict[str, int] = Field(default_factory=dict)
    persistence_enabled: bool = False
    conversation_store_path: str | None = None


class StandardResponse(BaseModel):
    success: bool
    message: str = ""
    data: dict[str, Any] = Field(default_factory=dict)
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata)
    citations: list[Citation] = Field(default_factory=list)
    errors: list[ErrorDetail] | None = None
