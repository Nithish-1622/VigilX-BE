from __future__ import annotations

from schemas.rest import RestCapability, StructuredQuery


class SQLAgentPlanner:
    """
    Structured query planning only. No direct SQL execution is allowed.
    The planner maps intent to logical REST capabilities.
    """

    def make_plan(self, intent: str, question: str) -> StructuredQuery:
        capability = self._capability_for_intent(intent)
        return StructuredQuery(
            capability=capability,
            intent=intent,
            question=question,
            query_text=question,
        )

    def _capability_for_intent(self, intent: str) -> RestCapability:
        if intent == "case_lookup":
            return RestCapability.CASE_SEARCH
        if intent == "suspect_query":
            return RestCapability.ACCUSED_RECORDS
        if intent == "victim_query":
            return RestCapability.VICTIM_RECORDS
        if intent == "timeline_query":
            return RestCapability.CASE_SUMMARY
        if intent == "evidence_summary":
            return RestCapability.CASE_SUMMARY
        if intent == "statistics_query":
            return RestCapability.INVESTIGATION_STATUS
        return RestCapability.CRIME_RECORDS
