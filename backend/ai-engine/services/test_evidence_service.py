from __future__ import annotations

import unittest

from schemas.common import Citation
from services.evidence_service import EvidenceService


class EvidenceServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = EvidenceService()

    def test_threshold_for_timeline_requires_multiple_citations(self) -> None:
        citations = [Citation(source="a"), Citation(source="b")]
        result = self.service.has_minimum_evidence(
            citations=citations,
            evidence_text="timeline evidence",
            intent="timeline_query",
        )
        self.assertTrue(result)

    def test_threshold_fails_when_citations_below_required(self) -> None:
        citations = [Citation(source="a")]
        result = self.service.has_minimum_evidence(
            citations=citations,
            evidence_text="suspect evidence",
            intent="suspect_query",
        )
        self.assertFalse(result)

    def test_confidence_high_for_large_margin(self) -> None:
        citations = [
            Citation(source="rag"),
            Citation(source="django_api"),
            Citation(source="django_api"),
        ]
        confidence = self.service.confidence_level(citations, intent="case_lookup")
        self.assertEqual(confidence, "high")

    def test_source_breakdown_counts_sources(self) -> None:
        citations = [
            Citation(source="rag"),
            Citation(source="django_api"),
            Citation(source="django_api"),
        ]
        breakdown = self.service.source_breakdown(citations)
        self.assertEqual(breakdown["rag"], 1)
        self.assertEqual(breakdown["django_api"], 2)


if __name__ == "__main__":
    unittest.main()
