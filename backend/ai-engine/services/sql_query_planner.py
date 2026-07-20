from __future__ import annotations

import json
import re
from schemas.rest import RestCapability, StructuredQuery
from llm.client import LLMClient


class SQLAgentPlanner:
    """
    Structured query planning only. No direct SQL execution is allowed.
    The planner maps intent to logical REST capabilities and extracts entity filters.
    """

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._llm_client = llm_client or LLMClient()

    async def make_plan(self, intent: str, question: str) -> StructuredQuery:
        capability = self._capability_for_intent(intent)
        filters = {}

        # 1. Regex rule-based extraction for fast, guaranteed results
        # Look for FIR number pattern (e.g. FIR-2026-101)
        fir_match = re.search(r'\b(FIR-\d{4}-\d+|FIR-\d+)\b', question, re.IGNORECASE)
        if fir_match:
            filters["fir_id"] = fir_match.group(1).upper()
            filters["fir"] = fir_match.group(1).upper()

        # Look for name patterns (e.g. "is Rajesh Kumar")
        name_match = re.search(r'\b(?:is|show|suspect|victim|for)\b\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)', question)
        if name_match:
            name_val = name_match.group(1).strip()
            # Avoid matching case or FIR words as name
            if not any(word in name_val.lower() for word in ["case", "fir", "robbery", "theft", "burglary", "timeline", "detail"]):
                filters["name"] = name_val

        # Look for crime type patterns
        for crime in ["ROBBERY", "THEFT", "BURGLARY", "BANK_ROBBERY"]:
            if crime.replace("_", " ").lower() in question.lower():
                filters["crime_type"] = crime

        # 2. LLM-based entity extraction for advanced patterns
        prompt = f"""
        Extract query filters from the user question for our REST API.
        Allowed filter fields:
        - "name": Person's name (suspect, accused, victim). E.g., "Rajesh Kumar", "Priya".
        - "fir_id": Case reference or FIR number. E.g., "FIR-2026-101", "FIR-123".
        - "crime_type": Type of crime (must be uppercase, e.g. "ROBBERY", "THEFT", "BURGLARY").
        - "fir": FIR reference.
        
        Question: "{question}"
        
        Return ONLY a raw JSON object containing these filters (empty if none found). No conversational filler or formatting blocks.
        Example: {{"name": "Rajesh Kumar"}}
        """
        try:
            res = await self._llm_client.generate(prompt)
            start = res.find("{")
            end = res.rfind("}")
            if start != -1 and end != -1:
                llm_filters = json.loads(res[start:end+1])
                if isinstance(llm_filters, dict):
                    for k, v in llm_filters.items():
                        if v and str(v).strip():
                            filters[k] = str(v).strip()
        except Exception:
            pass

        return StructuredQuery(
            capability=capability,
            intent=intent,
            question=question,
            query_text=question,
            filters=filters,
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
