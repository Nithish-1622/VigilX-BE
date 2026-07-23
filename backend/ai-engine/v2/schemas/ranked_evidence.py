from __future__ import annotations

from pydantic import BaseModel, Field

from schemas.common import Citation


class EvidenceScore(BaseModel):
    """Composite scoring for a single evidence item."""

    confidence: float = 0.0              # 0.0–1.0 — raw + source-adjusted score
    freshness: float = 1.0               # 1.0 = current; decays with record age
    source_reliability: float = 0.5      # Tier-based source trustworthiness
    relevance: float = 0.5               # Semantic overlap with question
    composite: float = 0.0               # Weighted: conf*0.5 + src*0.3 + rel*0.2


class RankedEvidenceItem(BaseModel):
    citation: Citation
    scores: EvidenceScore
    rank: int                            # 1 = highest ranked
    source_tier: str = "secondary"       # primary | secondary | tertiary


class EvidenceBundle(BaseModel):
    """
    Output of EvidenceRankingAgent.
    top_evidence_text is what gets sent to LLMReasoningAgent.
    """

    ranked_items: list[RankedEvidenceItem] = Field(default_factory=list)
    top_evidence_text: str = ""          # Top-K items formatted for LLM prompt
    overall_confidence: float = 0.0
    confidence_label: str = "none"       # none | low | medium | high | very_high
    threshold_met: bool = False
    evidence_count: int = 0
    source_diversity: int = 0            # Number of distinct source types
