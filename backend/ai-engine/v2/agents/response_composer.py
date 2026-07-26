from __future__ import annotations

from uuid import uuid4

from schemas.common import Citation
from v2.agents.base_agent import BaseAgent
from v2.schemas.chart_spec import ChartSpec
from v2.schemas.execution_plan import ToolType
from v2.schemas.investigation_response import (
    InvestigationResponse,
    KeyFinding,
    RelatedEntity,
    TimelineEvent,
)
from v2.state import V2WorkflowState


class ResponseComposerAgent(BaseAgent):
    """
    Agent 20: Response Composer Agent
    Single responsibility: Assemble the final InvestigationResponse from all prior
    agent outputs.

    Operates in two modes:
    - Clarification mode: verification_passed=False → pass through clarification response
    - Full mode: verification_passed=True → assemble complete investigation response
    """

    async def run(self, state: V2WorkflowState) -> V2WorkflowState:
        # ── Clarification mode ────────────────────────────────────────────────
        if not state.get("verification_passed", False):
            existing = state.get("final_response")
            if existing is None:
                state["final_response"] = InvestigationResponse(
                    session_id=state.get("session_id", ""),
                    user_id=state.get("user_id", ""),
                    intent=state.get("execution_plan", {}).intent if state.get("execution_plan") else "unknown",
                    clarification_needed=True,
                    clarification_question="Could you provide more details about your query?",
                    executive_summary="",
                )
            self.logger.info("Response Composer: clarification mode")
            return state

        # ── Full investigation response mode ──────────────────────────────────
        bundle = state.get("evidence_bundle")
        reasoning = state.get("reasoning_output", "")
        tool_results = state.get("tool_results", [])
        plan = state.get("execution_plan")
        critic_warnings = state.get("critic_warnings", [])
        recommendations = state.get("_recommendations", [])

        # Extract chart specs from VisualizationAgent output
        chart_specs = self._extract_charts(tool_results)

        # Build timeline from AnalyticsAgent output
        timeline = self._extract_timeline(tool_results, bundle)

        # Extract related entities from GraphAgent output
        entities = self._extract_entities(tool_results, bundle)

        # Build key findings from LLM reasoning paragraphs
        findings = self._extract_findings(reasoning, bundle, critic_warnings)

        # All citations from ranked evidence
        all_citations = self._collect_citations(bundle)

        # Override recommendations if Recommendation Agent already set them
        final_recs = recommendations or (
            state.get("final_response").recommendations
            if state.get("final_response") and state["final_response"].recommendations
            else []
        )

        response = InvestigationResponse(
            response_id=str(uuid4()),
            session_id=state.get("session_id", ""),
            user_id=state.get("user_id", ""),
            intent=plan.intent if plan else "unknown",
            complexity=plan.complexity if plan else "simple",
            executive_summary=reasoning,
            key_findings=findings,
            timeline=timeline[:20],
            related_entities=entities[:10],
            evidence_bundle=bundle,
            recommendations=final_recs[:8],
            chart_specs=chart_specs,
            citations=all_citations[:15],
            confidence=bundle.overall_confidence if bundle else 0.0,
            confidence_label=bundle.confidence_label if bundle else "none",
            clarification_needed=False,
            critic_passed=len(critic_warnings) == 0,
            critic_warnings=critic_warnings,
            metadata={
                "plan_id": plan.plan_id if plan else None,
                "correlation_id": state.get("correlation_id"),
                "tools_used": [tr.tool.value for tr in tool_results if tr.success],
                "tool_latencies_ms": {
                    tr.tool.value: tr.execution_time_ms
                    for tr in tool_results
                    if tr.execution_time_ms is not None
                },
                "source_diversity": bundle.source_diversity if bundle else 0,
                "evidence_count": bundle.evidence_count if bundle else 0,
            },
        )

        state["final_response"] = response
        self.logger.info(
            "Response composed: findings=%d, timeline=%d, entities=%d, "
            "citations=%d, charts=%d, critic_passed=%s",
            len(findings),
            len(timeline),
            len(entities),
            len(all_citations),
            len(chart_specs),
            response.critic_passed,
        )
        return state

    # ── Private helpers ───────────────────────────────────────────────────────

    def _extract_charts(self, tool_results) -> list[ChartSpec]:
        viz = next(
            (tr for tr in tool_results if tr.tool == ToolType.VISUALIZATION and tr.success),
            None,
        )
        if not viz:
            return []
        specs: list[ChartSpec] = []
        for rec in viz.records:
            try:
                specs.append(ChartSpec.model_validate(rec))
            except Exception:
                pass
        return specs

    def _extract_timeline(self, tool_results, bundle) -> list[TimelineEvent]:
        analytics = next(
            (tr for tr in tool_results if tr.tool == ToolType.ANALYTICS and tr.success),
            None,
        )
        if not analytics:
            return []
        conf = bundle.overall_confidence if bundle else 0.0
        events: list[TimelineEvent] = []
        for rec in analytics.records:
            if "timestamp" in rec and "event" in rec:
                events.append(
                    TimelineEvent(
                        timestamp=rec.get("timestamp"),
                        event=rec.get("event", ""),
                        source=rec.get("source", "analytics"),
                        confidence=conf,
                    )
                )
        return events

    def _extract_entities(self, tool_results, bundle) -> list[RelatedEntity]:
        graph = next(
            (tr for tr in tool_results if tr.tool == ToolType.GRAPH and tr.success),
            None,
        )
        if not graph:
            return []
        conf = bundle.overall_confidence if bundle else 0.0
        entities: list[RelatedEntity] = []
        for rec in graph.records[:8]:
            name = (
                rec.get("name")
                or rec.get("accused_1")
                or rec.get("hidden_link")
            )
            if name:
                entities.append(
                    RelatedEntity(
                        entity_type="person",
                        name=str(name),
                        role=rec.get("role", "suspect"),
                        relationship_to_case="identified via criminal network analysis",
                        confidence=conf,
                    )
                )
        return entities

    def _extract_findings(
        self, reasoning: str, bundle, critic_warnings: list[str]
    ) -> list[KeyFinding]:
        if not reasoning:
            return []
        paragraphs = [p.strip() for p in reasoning.split("\n") if len(p.strip()) > 30]
        conf = bundle.overall_confidence if bundle else 0.0
        evidence_ids = [
            item.citation.reference_id
            for item in (bundle.ranked_items[:3] if bundle else [])
            if item.citation.reference_id
        ]
        findings: list[KeyFinding] = []
        for para in paragraphs[:6]:
            findings.append(
                KeyFinding(
                    finding=para,
                    evidence_ids=evidence_ids,
                    confidence=conf,
                    supported=len(critic_warnings) == 0,
                )
            )
        return findings

    def _collect_citations(self, bundle) -> list[Citation]:
        if not bundle:
            return []
        return [item.citation for item in bundle.ranked_items]
