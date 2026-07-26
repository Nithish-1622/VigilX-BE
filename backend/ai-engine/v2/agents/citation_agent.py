from __future__ import annotations

# pyrefly: ignore [missing-import]
from schemas.common import Citation
from v2.agents.base_agent import BaseAgent
from v2.state import V2WorkflowState


class CitationAgent(BaseAgent):
    """
    Agent 18: Citation Agent
    Single responsibility: Enrich and attach structured citations to the evidence bundle.

    Maps ranked evidence items to citation references.
    Assigns deterministic reference IDs (EVD-001, EVD-002...) for traceability.
    These references are used by ResponseComposerAgent for KeyFinding.evidence_ids.
    """

    async def run(self, state: V2WorkflowState) -> V2WorkflowState:
        bundle = state.get("evidence_bundle")
        if bundle is None or not bundle.ranked_items:
            self.logger.info("Citation Agent: no ranked items to enrich")
            return state

        enriched: list[Citation] = []
        for i, ranked in enumerate(bundle.ranked_items[:15]):
            citation = ranked.citation
            ref_id = citation.reference_id or f"EVD-{i + 1:03d}"

            enriched.append(
                Citation(
                    source=citation.source,
                    reference_id=ref_id,
                    snippet=citation.snippet,
                    score=citation.score,
                )
            )
            # Update ranked item's citation in place for downstream consistency
            ranked.citation = enriched[-1]

        # Propagate enriched citations back to aggregated evidence if available
        aggregated = state.get("aggregated_evidence")
        if aggregated:
            aggregated.all_citations = enriched

        self.logger.info("Citations enriched: %d items with reference IDs", len(enriched))
        return state
