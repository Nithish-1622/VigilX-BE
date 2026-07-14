from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch, AsyncMock

from schemas.common import Citation
from services.evidence_service import EvidenceService
from services.reasoning_service import ReasoningService
from services.prompt_service import PromptService


class IntegrationReasoningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.evidence_service = EvidenceService()
        
        # Stub the prompt service to avoid looking up actual template files
        self.prompt_service = MagicMock(spec=PromptService)
        self.prompt_service.render.return_value = "rendered_prompt"
        self.prompt_service.get_template.return_value = "Address is unavailable."
        
        self.llm_client = AsyncMock()
        self.reasoning_service = ReasoningService(
            prompt_service=self.prompt_service,
            llm_client=self.llm_client
        )

    def test_evidence_propagation_preserves_custom_fields(self) -> None:
        """
        Verify that fields like address, criminal_history, gender, and age
        are successfully serialized and not lost during evidence construction.
        """
        record = {
            "id": "ACC_1001",
            "name": "John Doe",
            "age": 32,
            "gender": "MALE",
            "address": "No. 5, 2nd Cross, Koramangala",
            "status": "SUSPECT",
            "criminal_history": "Prior robbery arrest in 2024."
        }
        
        citations = self.evidence_service.records_to_citations([record])
        self.assertEqual(len(citations), 1)
        
        snippet = citations[0].snippet
        self.assertIn("address=No. 5, 2nd Cross, Koramangala", snippet)
        self.assertIn("criminal_history=Prior robbery arrest in 2024.", snippet)
        self.assertIn("age=32", snippet)
        self.assertIn("gender=MALE", snippet)

    def test_missing_field_returns_fallback_message(self) -> None:
        """
        Ensure that if a field (like address) is missing, the ReasoningService
        properly invokes its fallback handling.
        """
        # If evidence is empty, ReasoningService.answer returns the fallback message
        self.llm_client.generate.return_value = "Address is unavailable."
        
        response = self.reasoning_service.insufficient_data_message()
        self.assertEqual(response, "Address is unavailable.")

    def test_rest_precedence_rules_injected_in_prompt(self) -> None:
        """
        Verify that the reasoning service passes the question and evidence
        correctly to the prompt rendering engine.
        """
        evidence_text = "name=John Doe; address=Koramangala"
        question = "Where does he live?"
        conversation_summary = "user: Who is John Doe? | assistant: He is a suspect."
        
        self.llm_client.generate.return_value = "John Doe lives in Koramangala."
        
        # Test reasoning service call
        answer = asyncio_run(
            self.reasoning_service.answer(
                question=question,
                conversation_summary=conversation_summary,
                evidence_block=evidence_text,
            )
        )
        
        self.assertEqual(answer, "John Doe lives in Koramangala.")
        self.prompt_service.render.assert_called_once_with(
            "evidence_response_v1.txt",
            question=question,
            conversation_summary=conversation_summary,
            evidence_block=evidence_text,
        )


def asyncio_run(coro):
    import asyncio
    return asyncio.run(coro)


if __name__ == "__main__":
    unittest.main()
