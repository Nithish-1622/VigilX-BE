from __future__ import annotations

from schemas.conversation import MessageRecord
from services.prompt_service import PromptService
from llm.client import LLMClient


class ConversationSummaryService:
    def __init__(self, prompt_service: PromptService, llm_client: LLMClient) -> None:
        self._prompt_service = prompt_service
        self._llm_client = llm_client

    async def summarize(self, history: list[MessageRecord]) -> str:
        if not history:
            return "No prior conversation context."

        history_text = "\n".join(f"{msg.role}: {msg.content}" for msg in history[-8:])
        prompt = self._prompt_service.render(
            "conversation_summary_v1.txt",
            history_text=history_text,
        )

        llm_summary = (await self._llm_client.generate(prompt)).strip()
        if llm_summary:
            return llm_summary

        fallback = " | ".join(f"{msg.role}: {msg.content}" for msg in history[-4:])
        return fallback or "No prior conversation context."
