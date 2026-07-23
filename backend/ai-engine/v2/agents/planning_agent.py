from __future__ import annotations

import json

from llm.client import LLMClient
from services.prompt_service import PromptService
from v2.agents.base_agent import BaseAgent
from v2.registry.tool_registry import tool_registry
from v2.schemas.execution_plan import (
    DependencyType,
    ExecutionPlan,
    ToolCall,
    ToolType,
)
from v2.state import V2WorkflowState

# Extended V2 intent taxonomy
_INTENT_TAXONOMY = frozenset({
    "case_lookup",
    "evidence_summary",
    "timeline_query",
    "suspect_query",
    "victim_query",
    "statistics_query",
    "criminal_network",
    "investigation_status",
    "follow_up",
    "unknown",
})


class PlanningAgent(BaseAgent):
    """
    Agent 3: Planning Agent
    Single responsibility: Generate a structured ExecutionPlan by querying the
    ToolCapabilityRegistry and prompting the LLM to select appropriate tools.

    DOES NOT answer questions.
    DOES NOT query databases.
    ONLY produces a plan that tells downstream agents what to do.
    Falls back to deterministic heuristic if LLM plan fails to parse.
    """

    def __init__(self, prompt_service: PromptService, llm_client: LLMClient) -> None:
        super().__init__()
        self._prompt_service = prompt_service
        self._llm_client = llm_client

    async def run(self, state: V2WorkflowState) -> V2WorkflowState:
        question = state["question"]
        conversation_summary = state.get("conversation_summary", "No prior context.")

        # Query registry — planner sees exactly what tools exist
        available = tool_registry.all_enabled()
        available_tool_names = [t.name for t in available]
        state["available_tool_names"] = available_tool_names
        tools_description = tool_registry.names_for_prompt()

        # Generate plan (LLM → fallback on parse failure)
        plan = await self._llm_plan(question, conversation_summary, tools_description)
        plan.available_tools = available_tool_names

        state["execution_plan"] = plan
        self.logger.info(
            "Plan[%s] Intent[%s] Complexity[%s] Tools[%s]",
            plan.plan_id,
            plan.intent,
            plan.complexity,
            [tc.tool.value for tc in plan.tool_calls],
        )
        return state

    async def _llm_plan(
        self,
        question: str,
        conversation_summary: str,
        tools_description: str,
    ) -> ExecutionPlan:
        prompt = self._prompt_service.render(
            "planning_v2.txt",
            question=question,
            conversation_summary=conversation_summary,
            tools_description=tools_description,
        )
        raw = await self._llm_client.generate(prompt)

        try:
            # Extract JSON even if LLM wraps it in markdown fences
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start != -1 and end > start:
                data = json.loads(raw[start:end])
                plan = ExecutionPlan.model_validate(data)
                # Validate intent against taxonomy
                if plan.intent not in _INTENT_TAXONOMY:
                    plan.intent = self._heuristic_intent(question)
                return plan
        except Exception as exc:
            self.logger.warning("LLM plan parse failed (%s). Using heuristic fallback.", exc)

        return self._heuristic_plan(question)

    def _heuristic_plan(self, question: str) -> ExecutionPlan:
        """Deterministic fallback when LLM output cannot be parsed."""
        intent = self._heuristic_intent(question)
        lowered = question.lower()

        tool_calls: list[ToolCall] = [
            ToolCall(
                tool=ToolType.SQL,
                priority=1,
                dependency=DependencyType.INDEPENDENT,
                rationale="Primary structured data source",
            ),
            ToolCall(
                tool=ToolType.RAG,
                priority=1,
                dependency=DependencyType.INDEPENDENT,
                rationale="Semantic evidence retrieval",
            ),
        ]

        if intent in {"criminal_network", "suspect_query", "case_lookup"}:
            tool_calls.append(
                ToolCall(
                    tool=ToolType.GRAPH,
                    priority=1,
                    dependency=DependencyType.INDEPENDENT,
                    rationale="Relationship and network traversal",
                )
            )

        if intent in {"timeline_query", "evidence_summary"}:
            tool_calls.append(
                ToolCall(
                    tool=ToolType.ANALYTICS,
                    priority=2,
                    dependency=DependencyType.AFTER_SQL,
                    rationale="Timeline reconstruction from records",
                    parameters={"operation": "timeline"},
                )
            )

        complexity = "simple"
        if intent in {"criminal_network", "statistics_query"}:
            complexity = "moderate"
        if any(t in lowered for t in ["and", "also", "as well as", "besides"]):
            complexity = "complex"

        return ExecutionPlan(
            original_question=question,
            intent=intent,
            complexity=complexity,
            tool_calls=tool_calls,
            reasoning_notes="Heuristic fallback plan — LLM plan parse failed",
        )

    def _heuristic_intent(self, question: str) -> str:
        lowered = question.lower()
        if any(t in lowered for t in ["suspect", "accused", "perpetrator"]):
            return "suspect_query"
        if any(t in lowered for t in ["victim", "injured", "deceased"]):
            return "victim_query"
        if any(t in lowered for t in ["network", "gang", "linked", "connected", "relationship"]):
            return "criminal_network"
        if any(t in lowered for t in ["timeline", "when", "sequence", "chronolog"]):
            return "timeline_query"
        if any(t in lowered for t in ["predict", "forecast", "trend", "next"]):
            return "statistics_query"
        if any(t in lowered for t in ["statistics", "count", "how many", "total", "rate"]):
            return "statistics_query"
        if any(t in lowered for t in ["status", "progress", "update", "pending"]):
            return "investigation_status"
        if any(t in lowered for t in ["case", "fir", "record", "report"]):
            return "case_lookup"
        return "case_lookup"
