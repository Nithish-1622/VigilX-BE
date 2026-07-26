from __future__ import annotations

from v2.agents.base_agent import BaseAgent
from v2.schemas.execution_plan import ToolType
from v2.state import V2WorkflowState


class RecommendationAgent(BaseAgent):
    """
    Agent 19: Recommendation Agent
    Single responsibility: Generate evidence-grounded investigation next steps,
    identify evidence gaps, and suggest follow-up actions.

    Recommendations are derived ONLY from:
    - EvidenceBundle state (gaps, low confidence)
    - CrossCheckReport (inconsistencies)
    - Tool results (graph findings, record counts)
    - Intent type (domain-specific playbooks)

    Does NOT call LLM. Does NOT query databases.
    """

    async def run(self, state: V2WorkflowState) -> V2WorkflowState:
        bundle = state.get("evidence_bundle")
        validation = state.get("validation_report")
        tool_results = state.get("tool_results", [])
        plan = state.get("execution_plan")
        intent = plan.intent if plan else "case_lookup"

        recommendations: list[str] = []

        # ── Evidence coverage gaps ─────────────────────────────────────────────
        if bundle:
            if bundle.source_diversity < 2:
                recommendations.append(
                    "Expand search to include Neo4j graph and Qdrant semantic search "
                    "for broader evidence coverage across data sources"
                )
            if bundle.evidence_count < 3:
                recommendations.append(
                    "Retrieve additional case records — current evidence count is low; "
                    "try searching with broader date range or related case numbers"
                )
            if bundle.confidence_label in {"low", "none"}:
                recommendations.append(
                    "Confidence is low — consider corroborating findings with "
                    "physical evidence records or witness statements"
                )

        # ── Cross-validation inconsistencies ──────────────────────────────────
        if validation and validation.inconsistencies:
            for inc in validation.inconsistencies[:3]:
                recommendations.append(
                    f"Reconcile data conflict in field '{inc.field}': "
                    f"SQL shows '{inc.value_from_sql}' but Graph shows '{inc.value_from_graph}'"
                )

        # ── Intent-specific investigation playbooks ────────────────────────────
        if intent == "suspect_query":
            recommendations.extend([
                "Cross-reference suspect history via Neo4j for co-accused relationships",
                "Verify suspect's alibi and cross-check with FIR timeline records",
                "Check for prior convictions in criminal records database",
            ])

        elif intent == "victim_query":
            recommendations.extend([
                "Secure victim's medical/forensic report if not already in system",
                "Interview victim's associates to establish connection to accused",
            ])

        elif intent == "criminal_network":
            recommendations.extend([
                "Run community detection algorithm to identify full criminal cluster",
                "Analyze degree centrality to prioritize interrogation of key orchestrators",
                "Flag all identified network members for surveillance review",
            ])

        elif intent == "timeline_query":
            recommendations.extend([
                "Reconstruct crime scene timeline with exact timestamps from CCTV/FIR logs",
                "Cross-reference accused location records with incident time window",
            ])

        elif intent == "case_lookup":
            recommendations.extend([
                "Review latest investigation log entries for officer notes",
                "Search for similar pattern crimes using Qdrant semantic search",
            ])

        elif intent == "statistics_query":
            recommendations.extend([
                "Export trends data to the analytics dashboard for visualization",
                "Set up automated alerts for crime type spikes in identified districts",
            ])

        # ── Graph-specific: follow up on hidden links ──────────────────────────
        graph_results = next(
            (tr for tr in tool_results if tr.tool == ToolType.GRAPH and tr.success and tr.records),
            None,
        )
        if graph_results:
            recommendations.append(
                f"Investigate {len(graph_results.records)} graph-linked entities identified "
                f"in network traversal — potential witnesses or co-accused"
            )

        # Cap at 8, deduplicate
        seen: set[str] = set()
        unique_recs: list[str] = []
        for r in recommendations:
            key = r[:50]
            if key not in seen:
                seen.add(key)
                unique_recs.append(r)

        final_recs = unique_recs[:8]

        # Store for ResponseComposerAgent
        state["_recommendations"] = final_recs

        # Also update existing final_response if it exists
        if state.get("final_response"):
            state["final_response"].recommendations = final_recs

        self.logger.info("Generated %d investigation recommendations", len(final_recs))
        return state
