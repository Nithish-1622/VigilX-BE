from __future__ import annotations

from llm.client import LLMClient
from services.prompt_service import PromptService
from utils.logging import get_logger

logger = get_logger(__name__)


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
            evidence_block=evidence_block[:10000],
        )

        logger.info("Evidence passed to PromptService: %s", evidence_block)
        logger.info("Final prompt sent to LLM:\n%s", prompt)

        response = (await self._llm_client.generate(prompt)).strip()
        if not response:
            # Dynamic generic fallback when LLM is unavailable
            try:
                lines = evidence_block.split('\n')
                summary = ["Based on available records:"]
                
                for line in lines[:30]:  # Allow more lines to capture nested data
                    clean = re.sub(r"^\[.*?\]\s*", "", line)
                    if clean.strip():
                        summary.append(f"• {clean.strip()}")

                if len(lines) > 30:
                    summary.append("• ... (additional details truncated)")

                return "\n".join(summary)
            except Exception:
                return evidence_block
                
        return response

    def insufficient_data_message(self) -> str:
        return self._prompt_service.get_template("insufficient_data_v1.txt").strip()

