from __future__ import annotations

from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from schemas.common import Citation
from v2.schemas.chart_spec import ChartSpec
from v2.schemas.ranked_evidence import EvidenceBundle


class TimelineEvent(BaseModel):
    timestamp: str | None = None
    event: str
    source: str
    confidence: float = 0.0
    citation_id: str | None = None


class KeyFinding(BaseModel):
    finding: str
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    supported: bool = True               # False if ResponseCriticAgent flagged it


class RelatedEntity(BaseModel):
    entity_type: str                     # person | location | organization | account
    name: str
    role: str
    relationship_to_case: str
    confidence: float = 0.0


class InvestigationResponse(BaseModel):
    """
    Full V2 response schema returned by POST /ai/v2/ask.
    Replaces V1 StandardResponse for the V2 pipeline.
    """

    response_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    user_id: str
    intent: str
    complexity: str = "simple"

    # --- Core content ---
    executive_summary: str = ""
    key_findings: list[KeyFinding] = Field(default_factory=list)
    timeline: list[TimelineEvent] = Field(default_factory=list)
    related_entities: list[RelatedEntity] = Field(default_factory=list)

    # --- Evidence + citations ---
    evidence_bundle: EvidenceBundle | None = None
    citations: list[Citation] = Field(default_factory=list)

    # --- Recommendations + visualizations ---
    recommendations: list[str] = Field(default_factory=list)
    chart_specs: list[ChartSpec] = Field(default_factory=list)

    # --- Confidence ---
    confidence: float = 0.0
    confidence_label: str = "none"       # none | low | medium | high | very_high

    # --- Clarification mode ---
    clarification_needed: bool = False
    clarification_question: str | None = None

    # --- Response Critic audit ---
    critic_passed: bool = True
    critic_warnings: list[str] = Field(default_factory=list)

    # --- Meta ---
    metadata: dict[str, Any] = Field(default_factory=dict)
    v2: bool = True
