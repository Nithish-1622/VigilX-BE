from __future__ import annotations

from schemas.common import Citation
from services.evidence_service import EvidenceService
from utils.config import settings
from v2.agents.base_agent import BaseAgent
from v2.schemas.ranked_evidence import EvidenceBundle, EvidenceScore, RankedEvidenceItem
from v2.state import V2WorkflowState

# ── Source reliability tiers ──────────────────────────────────────────────────
# Primary: authoritative structured sources (Django REST → PostgreSQL)
# Secondary: graph / vector / computed sources
# Tertiary: derived/generated sources

SOURCE_RELIABILITY: dict[str, float] = {
    # Primary tier (0.85–1.0)
    "django_api": 0.96,
    "case_search": 0.95,
    "accused_records": 0.92,
    "victim_records": 0.91,
    "case_summary": 0.87,
    "crime_records": 0.85,
    "investigation_status": 0.85,
    # Secondary tier (0.60–0.84)
    "neo4j_graph": 0.80,
    "qdrant_vector_search": 0.72,
    "analytics_engine": 0.66,
    "python_computation": 0.62,
    # Tertiary tier (0.30–0.59)
    "visualization_engine": 0.45,
    "forecast_engine": 0.40,
}

_CONFIDENCE_THRESHOLDS = {
    "very_high": 0.80,
    "high": 0.60,
    "medium": 0.40,
    "low": 0.15,
}


class EvidenceRankingAgent(BaseAgent):
    """
    Agent 13: Evidence Ranking Agent
    Single responsibility: Score every evidence citation, rank by composite score,
    select top-K for LLM prompt, produce final EvidenceBundle.

    Scoring formula: composite = confidence*0.5 + source_reliability*0.3 + relevance*0.2
    """

    def __init__(self, evidence_service: EvidenceService) -> None:
        super().__init__()
        self._evidence = evidence_service

    async def run(self, state: V2WorkflowState) -> V2WorkflowState:
        aggregated = state.get("aggregated_evidence")
        if aggregated is None:
            state["evidence_bundle"] = EvidenceBundle()
            return state

        plan = state.get("execution_plan")
        intent = plan.intent if plan else "case_lookup"
        question = state.get("question", "")

        citations = aggregated.all_citations
        ranked_items = self._rank(citations, question)

        # Top-8 evidence items form the LLM prompt block
        top_k = ranked_items[:8]
        top_evidence_text = self._format_top(top_k)

        overall_confidence = self._overall_confidence(ranked_items)
        confidence_label = self._label(overall_confidence)
        threshold_met = self._check_threshold(ranked_items, overall_confidence, intent)

        bundle = EvidenceBundle(
            ranked_items=ranked_items,
            top_evidence_text=top_evidence_text,
            overall_confidence=overall_confidence,
            confidence_label=confidence_label,
            threshold_met=threshold_met,
            evidence_count=len(citations),
            source_diversity=len(aggregated.source_breakdown),
        )

        state["evidence_bundle"] = bundle
        self.logger.info(
            "Evidence ranked: %d items | confidence=%.2f (%s) | threshold_met=%s | sources=%d",
            len(ranked_items),
            overall_confidence,
            confidence_label,
            threshold_met,
            bundle.source_diversity,
        )
        return state

    def _rank(self, citations: list[Citation], question: str) -> list[RankedEvidenceItem]:
        q_words = set(question.lower().split())
        items: list[RankedEvidenceItem] = []

        for citation in citations:
            src_reliability = SOURCE_RELIABILITY.get(citation.source or "", 0.5)

            # Confidence: blend raw score with source reliability
            raw = citation.score or 0.0
            confidence = (raw * 0.5 + src_reliability * 0.5) if raw > 0 else src_reliability * 0.7

            # Relevance: lexical overlap with question
            snippet_words = set((citation.snippet or "").lower().split())
            overlap = len(q_words & snippet_words) / max(len(q_words), 1)
            relevance = min(1.0, overlap + 0.25)

            composite = (confidence * 0.5) + (src_reliability * 0.3) + (relevance * 0.2)

            tier = (
                "primary" if src_reliability >= 0.85
                else "secondary" if src_reliability >= 0.60
                else "tertiary"
            )

            items.append(
                RankedEvidenceItem(
                    citation=citation,
                    scores=EvidenceScore(
                        confidence=round(confidence, 3),
                        freshness=1.0,
                        source_reliability=src_reliability,
                        relevance=round(relevance, 3),
                        composite=round(composite, 3),
                    ),
                    rank=0,           # Filled after sort
                    source_tier=tier,
                )
            )

        items.sort(key=lambda x: x.scores.composite, reverse=True)
        for i, item in enumerate(items):
            item.rank = i + 1
        return items

    def _format_top(self, items: list[RankedEvidenceItem]) -> str:
        parts: list[str] = []
        for item in items:
            snippet = item.citation.snippet or ""
            if snippet.strip():
                ref = item.citation.reference_id or f"EVD-{item.rank:03d}"
                parts.append(f"[{item.citation.source}|{ref}] {snippet}")
        return "\n".join(parts)

    def _overall_confidence(self, items: list[RankedEvidenceItem]) -> float:
        if not items:
            return 0.0
        top5 = items[:5]
        avg = sum(i.scores.composite for i in top5) / len(top5)
        # Diversity bonus: more unique sources = higher confidence
        diversity_bonus = min(0.08, len({i.citation.source for i in items}) * 0.015)
        return min(1.0, round(avg + diversity_bonus, 3))

    def _label(self, confidence: float) -> str:
        for label, threshold in _CONFIDENCE_THRESHOLDS.items():
            if confidence >= threshold:
                return label
        return "none"

    def _check_threshold(
        self, items: list[RankedEvidenceItem], confidence: float, intent: str
    ) -> bool:
        min_required = {
            "case_lookup": settings.min_citations_case_lookup,
            "timeline_query": settings.min_citations_timeline_query,
            "suspect_query": settings.min_citations_suspect_query,
            "victim_query": settings.min_citations_victim_query,
        }.get(intent, settings.min_citations_default)

        # Adaptive: single high-quality primary source is sufficient
        primary = [i for i in items if i.source_tier == "primary"]
        if len(primary) >= 1 and confidence >= 0.45:
            return True

        return len(items) >= min_required and confidence >= 0.15
