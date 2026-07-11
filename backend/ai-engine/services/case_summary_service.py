from __future__ import annotations

import json

from llm.client import LLMClient
from schemas.case_summary import CaseSummary
from schemas.common import Citation
from services.prompt_service import PromptService


class CaseSummaryService:
    def __init__(self, prompt_service: PromptService, llm_client: LLMClient) -> None:
        self._prompt_service = prompt_service
        self._llm_client = llm_client

    async def generate(
        self,
        question: str,
        conversation_summary: str,
        evidence_block: str,
        citations: list[Citation] | None = None,
    ) -> CaseSummary:
        citations = citations or []
        fallback = self._build_fallback_summary(citations)
        if not evidence_block.strip():
            return fallback

        prompt = self._prompt_service.render(
            "case_summary_v1.txt",
            question=question,
            conversation_summary=conversation_summary,
            evidence_block=evidence_block,
        )

        summary = (await self._llm_client.generate(prompt)).strip()
        if not summary:
            return fallback

        parsed = self._parse_summary(summary)
        if parsed is None:
            fallback.raw_output = {"raw_output": summary}
            return fallback

        parsed.reasoning.evidence_used = parsed.reasoning.evidence_used or [
            citation.snippet or citation.reference_id or citation.source for citation in citations if citation
        ]
        parsed.reasoning.retrieved_sources = parsed.reasoning.retrieved_sources or [
            citation.source for citation in citations if citation.source
        ]
        if not parsed.metadata.model:
            parsed.metadata.model = getattr(self._llm_client, "model", None)
        parsed.raw_output = parsed.raw_output or parsed.model_dump()
        return parsed

    def _build_fallback_summary(self, citations: list[Citation]) -> CaseSummary:
        summary = CaseSummary()
        summary.confidence = "low"
        summary.reasoning.evidence_used = [
            citation.snippet or citation.reference_id or citation.source for citation in citations if citation
        ]
        summary.reasoning.retrieved_sources = [citation.source for citation in citations if citation.source]
        summary.metadata.model = getattr(self._llm_client, "model", None)
        return summary

    def _parse_summary(self, llm_output: str) -> CaseSummary | None:
        llm_output = llm_output.strip()
        if "```" in llm_output:
            first_idx = llm_output.find("```")
            last_idx = llm_output.rfind("```")
            if first_idx != -1 and last_idx != -1 and first_idx != last_idx:
                start_line_end = llm_output.find("\n", first_idx)
                if start_line_end != -1 and start_line_end < last_idx:
                    llm_output = llm_output[start_line_end:last_idx].strip()
        try:
            loaded = json.loads(llm_output)
            if not isinstance(loaded, dict):
                return None
            return CaseSummary.model_validate(loaded)
        except Exception:  # noqa: BLE001
            return None
