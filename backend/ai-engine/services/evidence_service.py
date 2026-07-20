from __future__ import annotations

from collections import Counter

from schemas.common import Citation
from utils.config import settings


class EvidenceService:
    def records_to_text(self, rows: list[dict]) -> str:
        if not rows:
            return ""
        limited = rows[:5]
        return "\n".join(self._row_to_line(row) for row in limited)

    def records_to_citations(self, rows: list[dict]) -> list[Citation]:
        citations: list[Citation] = []
        for row in rows[:5]:
            ref_id = row.get("id") if isinstance(row, dict) else None
            citations.append(
                Citation(
                    source="django_api",
                    reference_id=str(ref_id) if ref_id is not None else None,
                    snippet=self._row_to_line(row),
                    score=None,
                )
            )
        return citations

    def format_row(self, row: dict) -> str:
        if not isinstance(row, dict):
            return str(row)

        parts = []
        for key, value in row.items():
            if value is not None and str(value).strip():
                parts.append(f"{key}={value}")
        if parts:
            return "; ".join(parts)
        return str(row)

    def required_citations_for_intent(self, intent: str) -> int:
        if intent == "case_lookup":
            return settings.min_citations_case_lookup
        if intent == "timeline_query":
            return settings.min_citations_timeline_query
        if intent == "suspect_query":
            return settings.min_citations_suspect_query
        if intent == "victim_query":
            return settings.min_citations_victim_query
        return settings.min_citations_default

    def has_minimum_evidence(
        self,
        citations: list[Citation],
        evidence_text: str,
        intent: str,
    ) -> bool:
        required = self.required_citations_for_intent(intent)
        
        # Adaptive Threshold: If exactly 1 high-quality record exists and is retrieved from the Django REST API,
        # adapt the threshold to 1 so the user gets the answer instead of a fallback "unavailable".
        if len(citations) == 1 and any(c.source in {"django_api", "accused_records", "victim_records", "case_search", "case_summary"} for c in citations):
            required = 1
            
        return len(citations) >= required and bool(evidence_text.strip())

    def confidence_level(self, citations: list[Citation], intent: str) -> str:
        required = self.required_citations_for_intent(intent)
        if len(citations) == 1 and any(c.source in {"django_api", "accused_records", "victim_records", "case_search", "case_summary"} for c in citations):
            required = 1
        count = len(citations)
        source_count = len(self.source_breakdown(citations))

        if intent in {"timeline_query", "suspect_query", "victim_query"}:
            if count >= required + 1 and source_count >= 2:
                return "high"
            if count >= required and source_count >= 2:
                return "medium"
            if count >= required:
                return "low"
            return "low"

        if count >= required + 2 and source_count >= 2:
            return "high"
        if count >= required:
            return "medium"
        return "low"

    def source_breakdown(self, citations: list[Citation]) -> dict[str, int]:
        counts = Counter(citation.source for citation in citations if citation.source)
        return dict(counts)

    def _row_to_line(self, row: dict) -> str:
        return self.format_row(row)
