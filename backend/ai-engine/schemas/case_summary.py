from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from schemas.common import Citation


class CaseSummaryPersonGroup(BaseModel):
    accused: list[str | None] = Field(default_factory=list)
    victims: list[str | None] = Field(default_factory=list)
    witnesses: list[str | None] = Field(default_factory=list)
    investigators: list[str | None] = Field(default_factory=list)


class CaseSummaryEvidenceGroup(BaseModel):
    physical: list[str | None] = Field(default_factory=list)
    digital: list[str | None] = Field(default_factory=list)
    documents: list[str | None] = Field(default_factory=list)


class CaseSummaryTimelineEvent(BaseModel):
    timestamp: str | None = None
    event: str | None = None
    source: str | None = None
    reference_id: str | None = None


class CaseSummaryIncident(BaseModel):
    title: str | None = None
    overview: str | None = None
    crime_type: str | None = None
    location: str | None = None
    occurrence_time: str | None = None


class CaseSummaryInvestigation(BaseModel):
    current_status: str | None = None
    pending_actions: list[str | None] = Field(default_factory=list)
    important_observations: list[str | None] = Field(default_factory=list)


class CaseSummaryReasoning(BaseModel):
    evidence_used: list[str | None] = Field(default_factory=list)
    retrieved_sources: list[str | None] = Field(default_factory=list)
    assumptions: list[str | None] = Field(default_factory=list)


class CaseSummaryMetadata(BaseModel):
    generated_by: str = "ai-engine"
    model: str | None = None
    version: str = "1.0"


class CaseSummary(BaseModel):
    case_summary: str | None = Field(default=None, description="A text summary of the case")
    summary_id: str = Field(default_factory=lambda: str(uuid4()))
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    confidence: str = "low"
    incident: CaseSummaryIncident = Field(default_factory=CaseSummaryIncident)
    people: CaseSummaryPersonGroup = Field(default_factory=CaseSummaryPersonGroup)
    evidence: CaseSummaryEvidenceGroup = Field(default_factory=CaseSummaryEvidenceGroup)
    timeline: list[CaseSummaryTimelineEvent] = Field(default_factory=list)
    investigation: CaseSummaryInvestigation = Field(default_factory=CaseSummaryInvestigation)
    reasoning: CaseSummaryReasoning = Field(default_factory=CaseSummaryReasoning)
    metadata: CaseSummaryMetadata = Field(default_factory=CaseSummaryMetadata)
    raw_output: dict[str, Any] | None = None


class CaseSummaryResponse(BaseModel):
    summary: CaseSummary
    citations: list[Citation] = Field(default_factory=list)
