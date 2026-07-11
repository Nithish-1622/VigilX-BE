from __future__ import annotations

from llm.client import LLMClient
from services.prompt_service import PromptService


class ReasoningService:
    def __init__(self, prompt_service: PromptService, llm_client: LLMClient) -> None:
        self._prompt_service = prompt_service
        self._llm_client = llm_client

    async def answer(
        self,
        question: str,
        conversation_summary: str,
        evidence_block: str,
    ) -> str:
        if not evidence_block.strip():
            return self.insufficient_data_message()

        prompt = self._prompt_service.render(
            "evidence_response_v1.txt",
            question=question,
            conversation_summary=conversation_summary,
            evidence_block=evidence_block,
        )

        response = (await self._llm_client.generate(prompt)).strip()
        if not response:
            return self.insufficient_data_message()
        return response

    def insufficient_data_message(self) -> str:
        return self._prompt_service.get_template("insufficient_data_v1.txt").strip()
