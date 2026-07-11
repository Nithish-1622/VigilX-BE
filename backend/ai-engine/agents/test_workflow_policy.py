from __future__ import annotations

import unittest
from unittest.mock import AsyncMock

from agents.workflow import AIOrchestrator
from schemas.common import Citation
from schemas.conversation import AskRequest


class WorkflowPolicyTests(unittest.IsolatedAsyncioTestCase):
    async def test_insufficient_evidence_skips_reasoning(self) -> None:
        orchestrator = AIOrchestrator()
        orchestrator._graph = None
        orchestrator._intent.detect = AsyncMock(return_value="suspect_query")
        orchestrator._retriever.retrieve = AsyncMock(
            return_value=type(
                "Retrieved",
                (),
                {"evidence_text": "", "citations": []},
            )()
        )
        orchestrator._sql_agent.execute_plan = AsyncMock(
            return_value=type("SQLResult", (), {"records": [], "plan": "none"})()
        )
        orchestrator._reasoning.answer = AsyncMock(return_value="should not be used")

        response = await orchestrator.run(
            AskRequest(session_id="sess-1", user_id="user-1", question="show suspect details")
        )

        self.assertEqual(response.data["answer"], "This cannot be determined from the available data.")
        self.assertEqual(response.metadata.evidence_threshold_met, False)
        self.assertEqual(response.metadata.confidence, "low")
        orchestrator._reasoning.answer.assert_not_awaited()

    async def test_response_metadata_is_typed(self) -> None:
        orchestrator = AIOrchestrator()
        orchestrator._graph = None
        orchestrator._intent.detect = AsyncMock(return_value="case_lookup")
        orchestrator._retriever.retrieve = AsyncMock(
            return_value=type(
                "Retrieved",
                (),
                {
                    "evidence_text": "case evidence",
                    "citations": [Citation(source="api", reference_id="1", snippet="case evidence")],
                },
            )()
        )
        orchestrator._sql_agent.execute_plan = AsyncMock(
            return_value=type("SQLResult", (), {"records": [{"id": "1", "case_id": "C-1"}], "plan": "cases/search?q=x"})()
        )
        orchestrator._reasoning.answer = AsyncMock(return_value="case answer")
        orchestrator._case_summary.generate = AsyncMock(
            return_value=type(
                "CaseSummary",
                (),
                {
                    "model_dump": lambda self: {
                        "summary_id": "summary-1",
                        "generated_at": "2026-07-11T00:00:00+00:00",
                        "confidence": "medium",
                        "incident": {
                            "title": "Case title",
                            "overview": "Case overview",
                            "crime_type": "unknown",
                            "location": None,
                            "occurrence_time": None,
                        },
                        "people": {
                            "accused": [],
                            "victims": [],
                            "witnesses": [],
                            "investigators": [],
                        },
                        "evidence": {
                            "physical": [],
                            "digital": [],
                            "documents": [],
                        },
                        "timeline": [],
                        "investigation": {
                            "current_status": None,
                            "pending_actions": [],
                            "important_observations": [],
                        },
                        "reasoning": {
                            "evidence_used": ["case evidence"],
                            "retrieved_sources": ["api"],
                            "assumptions": [],
                        },
                        "metadata": {
                            "generated_by": "ai-engine",
                            "model": "qwen3",
                            "version": "1.0",
                        },
                        "raw_output": None,
                    }
                },
            )()
        )

        response = await orchestrator.run(
            AskRequest(session_id="sess-2", user_id="user-2", question="case 1")
        )

        self.assertEqual(response.metadata.intent, "case_lookup")
        self.assertTrue(response.metadata.evidence_threshold_met)
        self.assertEqual(response.metadata.rag_citations, 1)
        self.assertEqual(response.metadata.sql_citations, 1)
        self.assertEqual(response.metadata.evidence_source_breakdown["api"], 1)
        self.assertEqual(response.metadata.evidence_source_breakdown["django_api"], 1)
        self.assertTrue(response.metadata.persistence_enabled)
        self.assertIsNotNone(response.metadata.conversation_store_path)
        self.assertIsInstance(response.data["case_summary"], dict)
        self.assertEqual(response.data["case_summary"]["confidence"], "medium")
        self.assertIn("case answer", response.data["answer"])


if __name__ == "__main__":
    unittest.main()
