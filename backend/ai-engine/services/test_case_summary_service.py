from __future__ import annotations

import unittest
from unittest.mock import AsyncMock

from schemas.case_summary import CaseSummary
from services.case_summary_service import CaseSummaryService
from services.prompt_service import PromptService
from llm.client import LLMClient
from pathlib import Path


class CaseSummaryServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_generate_returns_summary_when_llm_answers(self) -> None:
        prompt_service = PromptService(prompt_dir=Path(__file__).resolve().parent.parent / "prompts")
        llm_client = LLMClient()
        llm_client.generate = AsyncMock(return_value="case summary output")
        service = CaseSummaryService(prompt_service=prompt_service, llm_client=llm_client)

        summary = await service.generate(
            question="summarize case",
            conversation_summary="conversation summary",
            evidence_block="evidence text",
        )

        self.assertIsInstance(summary, CaseSummary)
        self.assertEqual(summary.raw_output, {"raw_output": "case summary output"})

    async def test_generate_returns_fallback_when_no_evidence(self) -> None:
        prompt_service = PromptService(prompt_dir=Path(__file__).resolve().parent.parent / "prompts")
        llm_client = LLMClient()
        llm_client.generate = AsyncMock(return_value="")
        service = CaseSummaryService(prompt_service=prompt_service, llm_client=llm_client)

        summary = await service.generate(
            question="summarize case",
            conversation_summary="conversation summary",
            evidence_block="",
        )

        self.assertIsInstance(summary, CaseSummary)
        self.assertEqual(summary.confidence, "low")

    async def test_generate_returns_parsed_summary_when_llm_returns_json(self) -> None:
        prompt_service = PromptService(prompt_dir=Path(__file__).resolve().parent.parent / "prompts")
        llm_client = LLMClient()
        json_output = """
        ```json
        {
            "case_summary": "Test case summary text",
            "confidence": "high",
            "incident": {
                "title": "Incident A",
                "overview": "Overview of A",
                "crime_type": "Theft",
                "location": "Loc A",
                "occurrence_time": "2026-07-11"
            },
            "people": {
                "accused": ["Accused A"],
                "victims": ["Victim V"],
                "witnesses": [],
                "investigators": []
            },
            "evidence": {
                "physical": ["Evidence E"],
                "digital": [],
                "documents": []
            },
            "timeline": [],
            "investigation": {
                "current_status": "Open",
                "pending_actions": [],
                "important_observations": []
            },
            "reasoning": {
                "evidence_used": ["Evidence E"],
                "retrieved_sources": ["db"],
                "assumptions": []
            },
            "metadata": {
                "generated_by": "ai-engine",
                "model": "qwen3",
                "version": "1.0"
            }
        }
        ```
        """
        llm_client.generate = AsyncMock(return_value=json_output)
        service = CaseSummaryService(prompt_service=prompt_service, llm_client=llm_client)

        summary = await service.generate(
            question="summarize case",
            conversation_summary="conversation summary",
            evidence_block="evidence text",
        )

        self.assertIsInstance(summary, CaseSummary)
        self.assertEqual(summary.case_summary, "Test case summary text")
        self.assertEqual(summary.confidence, "high")
        self.assertEqual(summary.incident.title, "Incident A")
        self.assertEqual(summary.people.accused, ["Accused A"])
        self.assertEqual(summary.evidence.physical, ["Evidence E"])


if __name__ == "__main__":
    unittest.main()
