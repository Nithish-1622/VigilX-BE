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
            evidence_block=evidence_block,
        )

        logger.info("Evidence passed to PromptService: %s", evidence_block)
        logger.info("Final prompt sent to LLM:\n%s", prompt)

        response = (await self._llm_client.generate(prompt)).strip()
        if not response:
            # Dynamic generic fallback when LLM is unavailable
            try:
                # The evidence block looks like:
                # id=101; crime_type=THEFT; status=PENDING; accused=[{name=Rajesh Kumar}]
                lines = evidence_block.split('\n')
                summary = []
                import re
                seen_ids = set()
                
                for line in lines:
                    if not line.strip():
                        continue
                        
                    # Deduplicate by ID to ignore [source] prefix
                    match = re.search(r'id=(\d+)', line)
                    if match:
                        rec_id = match.group(1)
                        if rec_id in seen_ids:
                            continue
                        seen_ids.add(rec_id)
                        
                    # Clean up the [source] prefix if it exists before splitting
                    clean_line = re.sub(r'^\[.*?\]\s*', '', line)
                    parts = clean_line.split('; ')
                    summary.append("Found Record:")
                    for part in parts:
                        if '=' in part:
                            key, val = part.split('=', 1)
                            key = key.replace('_', ' ').title()
                            if val.startswith('[') and val.endswith(']'):
                                # Format lists of dicts beautifully
                                val = val.strip('[]')
                                if not val:
                                    val = "None"
                                else:
                                    items = val.split(' | ')
                                    val = ", ".join(items).replace('{', '').replace('}', '')
                            summary.append(f"  - {key}: {val}")
                return "\n".join(summary)
            except Exception:
                return evidence_block
                
        return response

    def insufficient_data_message(self) -> str:
        return self._prompt_service.get_template("insufficient_data_v1.txt").strip()

