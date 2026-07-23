from __future__ import annotations

from services.evidence_service import EvidenceService
from services.sql_agent_service import SQLAgentService
from services.sql_query_planner import SQLAgentPlanner
from v2.schemas.execution_plan import ToolCall, ToolType
from v2.schemas.tool_result import ToolResult
from v2.state import V2WorkflowState


class SQLToolAgent:
    """
    Agent 6: SQL Tool Agent
    Single responsibility: Execute structured queries against Django REST API.

    Wraps V1 SQLAgentPlanner + SQLAgentService. No raw SQL ever executed.
    Exposes a handler method registered with ToolRouterAgent.
    Not a BaseAgent subclass — it is a tool handler, not a graph node.
    """

    def __init__(
        self,
        sql_agent_service: SQLAgentService,
        sql_agent_planner: SQLAgentPlanner,
        evidence_service: EvidenceService,
    ) -> None:
        self._sql_agent = sql_agent_service
        self._planner = sql_agent_planner
        self._evidence = evidence_service

    async def handle(self, tool_call: ToolCall, state: V2WorkflowState) -> ToolResult:
        """Handler registered with ToolRouterAgent for ToolType.SQL."""
        question = state["question"]
        plan = state.get("execution_plan")
        intent = plan.intent if plan else "case_lookup"
        auth_header = state.get("auth_header")
        context_headers = state.get("context_headers", {})
        extra_params = tool_call.parameters or {}

        try:
            # Use V1 SQLAgentPlanner for structured query generation
            structured_query = await self._planner.make_plan(intent, question)

            # Override with explicit tool_call parameters if provided
            if extra_params:
                for k, v in extra_params.items():
                    if v is not None and str(v).strip():
                        structured_query.filters[k] = str(v)

            # Execute via V1 SQLAgentService → DjangoRestGateway
            result = await self._sql_agent.execute_plan(
                structured_query,
                auth_header=auth_header,
                context_headers=context_headers,
            )

            text = self._evidence.records_to_text(result.records)
            citations = self._evidence.records_to_citations(result.records)

            return ToolResult(
                tool=ToolType.SQL,
                subtask_id=tool_call.subtask_id,
                success=True,
                records=result.records,
                text=text,
                citations=citations,
                metadata={"plan": structured_query.model_dump_json()},
            )

        except Exception as exc:
            return ToolResult(
                tool=ToolType.SQL,
                subtask_id=tool_call.subtask_id,
                success=False,
                error=str(exc),
            )
