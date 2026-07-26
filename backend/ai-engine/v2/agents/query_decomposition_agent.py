from __future__ import annotations

import json

from llm.client import LLMClient
from services.prompt_service import PromptService
from v2.agents.base_agent import BaseAgent
from v2.schemas.execution_plan import Subtask
from v2.state import V2WorkflowState


class QueryDecompositionAgent(BaseAgent):
    """
    Agent 4: Query Decomposition Agent
    Single responsibility: Break complex multi-hop questions into ordered,
    independently-executable subtasks.

    Placed between PlanningAgent and ToolRouterAgent.
    Simple and moderate queries pass through unchanged (single subtask = full question).
    Only complex/multi_hop plans trigger actual decomposition.
    """

    def __init__(self, prompt_service: PromptService, llm_client: LLMClient) -> None:
        super().__init__()
        self._prompt_service = prompt_service
        self._llm_client = llm_client

    async def run(self, state: V2WorkflowState) -> V2WorkflowState:
        plan = state.get("execution_plan")
        if plan is None:
            state["decomposed_subtasks"] = []
            return state

        # Simple/moderate: no decomposition needed — wrap as single subtask
        if plan.complexity not in {"complex", "multi_hop"}:
            single = Subtask(
                description="Primary investigation query",
                question_fragment=state["question"],
            )
            state["decomposed_subtasks"] = [single.model_dump()]
            self.logger.info("Complexity[%s]: passing through as single subtask", plan.complexity)
            return state

        # Complex/multi-hop: decompose via LLM
        subtasks = await self._decompose(
            state["question"],
            state.get("conversation_summary", ""),
        )

        plan.subtasks = subtasks
        state["execution_plan"] = plan
        state["decomposed_subtasks"] = [s.model_dump() for s in subtasks]

        self.logger.info(
            "Multi-hop decomposition: %d subtasks for complexity[%s]",
            len(subtasks),
            plan.complexity,
        )
        return state

    async def _decompose(self, question: str, context: str) -> list[Subtask]:
        """Decompose via LLM, fall back to single subtask on parse failure."""
        prompt = self._prompt_service.render(
            "query_decomposition_v2.txt",
            question=question,
            conversation_summary=context,
        )
        raw = await self._llm_client.generate(prompt)

        try:
            # Extract JSON array even if LLM wraps it in markdown
            start = raw.find("[")
            end = raw.rfind("]") + 1
            if start != -1 and end > start:
                items = json.loads(raw[start:end])
                if isinstance(items, list) and items:
                    return [Subtask.model_validate(item) for item in items]
        except Exception as exc:
            self.logger.warning("Decomposition parse failed (%s). Single subtask fallback.", exc)

        return [Subtask(description="Primary query", question_fragment=question)]
