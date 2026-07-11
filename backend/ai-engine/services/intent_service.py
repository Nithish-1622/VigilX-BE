from __future__ import annotations

from llm.client import LLMClient
from schemas.conversation import MessageRecord
from services.prompt_service import PromptService


class IntentService:
    _valid_labels = {
        "case_lookup",
        "evidence_summary",
        "timeline_query",
        "suspect_query",
        "victim_query",
        "statistics_query",
        "follow_up",
        "unknown",
    }

    def __init__(self, prompt_service: PromptService, llm_client: LLMClient) -> None:
        self._prompt_service = prompt_service
        self._llm_client = llm_client

    async def detect(self, question: str, history: list[MessageRecord]) -> str:
        prompt = self._prompt_service.render(
            "intent_detection_v1.txt",
            question=question,
        )
        raw_label = (await self._llm_client.generate(prompt)).strip().lower()
        if raw_label in self._valid_labels:
            return raw_label

        return self._heuristic_detect(question, history)

    def _heuristic_detect(self, question: str, history: list[MessageRecord]) -> str:
        lowered = question.lower()
        if any(token in lowered for token in ["summary", "summarize", "brief"]):
            return "evidence_summary"
        if any(token in lowered for token in ["timeline", "when", "time"]):
            return "timeline_query"
        if any(token in lowered for token in ["suspect", "accused"]):
            return "suspect_query"
        if any(token in lowered for token in ["victim", "injured"]):
            return "victim_query"
        if any(token in lowered for token in ["case", "fir", "record"]):
            return "case_lookup"
        if history and any(token in lowered for token in ["this", "that", "it", "them"]):
            return "follow_up"
        return "unknown"
