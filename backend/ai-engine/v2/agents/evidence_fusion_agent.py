from __future__ import annotations

from collections import Counter

from schemas.common import Citation
from services.evidence_service import EvidenceService
from v2.agents.base_agent import BaseAgent
from v2.schemas.tool_result import AggregatedEvidence, ToolResult
from v2.state import V2WorkflowState


class EvidenceFusionAgent(BaseAgent):
    """
    Agent 12: Evidence Fusion Agent
    Single responsibility: Merge all tool results into a unified, deduplicated
    AggregatedEvidence object with consistent citation attribution.

    Extends V1 EvidenceService deduplication methods.
    Does NOT rank or score — that is EvidenceRankingAgent's job.
    """

    def __init__(self, evidence_service: EvidenceService) -> None:
        super().__init__()
        self._evidence = evidence_service

    async def run(self, state: V2WorkflowState) -> V2WorkflowState:
        tool_results: list[ToolResult] = state.get("tool_results", [])

        # Use ToolRouter's pre-aggregated object as base if available
        aggregated = state.get("aggregated_evidence") or self._fuse(tool_results)

        # Deduplicate citations by compound key
        seen_keys: set[str] = set()
        unique_citations: list[Citation] = []
        for c in aggregated.all_citations:
            # Compound key: prefer reference_id, fallback to snippet hash
            key = c.reference_id or (c.snippet[:80] if c.snippet else None) or c.source
            if key and key not in seen_keys:
                seen_keys.add(key)
                unique_citations.append(c)

        aggregated.all_citations = unique_citations
        aggregated.source_breakdown = dict(
            Counter(c.source for c in unique_citations if c.source)
        )

        state["aggregated_evidence"] = aggregated

        self.logger.info(
            "Evidence fused: %d unique citations from %d sources, %d total records",
            len(unique_citations),
            len(aggregated.source_breakdown),
            aggregated.total_records,
        )
        return state

    def _fuse(self, results: list[ToolResult]) -> AggregatedEvidence:
        """Build AggregatedEvidence from raw tool results (fallback if ToolRouter didn't)."""
        all_citations: list[Citation] = []
        all_texts: list[str] = []
        total_records = 0

        for result in results:
            if result.success:
                all_citations.extend(result.citations)
                if result.text.strip():
                    all_texts.append(f"[{result.tool.value}] {result.text}")
                total_records += len(result.records)

        return AggregatedEvidence(
            tool_results=results,
            merged_text="\n".join(all_texts),
            all_citations=all_citations,
            source_breakdown={},
            total_records=total_records,
        )
