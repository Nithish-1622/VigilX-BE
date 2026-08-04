from __future__ import annotations

from schemas.rest import RestCapability
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
                        val = str(v).strip()
                        if k in {"search", "query"}:
                            continue
                        if k == "crime_type" and val.upper() not in {"ROBBERY", "THEFT", "BURGLARY", "BANK_ROBBERY", "MURDER", "ASSAULT", "KIDNAPPING", "FRAUD", "CYBERCRIME", "DRUG_TRAFFICKING"}:
                            continue
                        structured_query.filters[k] = val

            # Execute primary query via V1 SQLAgentService → DjangoRestGateway
            result = await self._sql_agent.execute_plan(
                structured_query,
                auth_header=auth_header,
                context_headers=context_headers,
            )

            all_records = list(result.records)

            # Supplementary queries for person details (accused/victim records) if name filter present or suspect/victim query
            name_val = structured_query.filters.get("name")
            if name_val or intent in {"suspect_query", "victim_query"}:
                for extra_cap in [RestCapability.ACCUSED_RECORDS, RestCapability.VICTIM_RECORDS]:
                    try:
                        supp_query = structured_query.model_copy(deep=True)
                        supp_query.capability = extra_cap
                        if name_val:
                            supp_query.filters = {"name": name_val}
                            supp_query.query_text = name_val
                        supp_res = await self._sql_agent.execute_plan(
                            supp_query,
                            auth_header=auth_header,
                            context_headers=context_headers,
                        )
                        if supp_res.records:
                            all_records.extend(supp_res.records)
                    except Exception:
                        pass

            # Fallback query if zero records returned: run broad case search with original question
            if not all_records:
                try:
                    fallback_query = structured_query.model_copy(deep=True)
                    fallback_query.capability = RestCapability.CASE_SEARCH
                    fallback_query.filters = {}
                    fallback_query.query_text = question
                    fb_res = await self._sql_agent.execute_plan(
                        fallback_query,
                        auth_header=auth_header,
                        context_headers=context_headers,
                    )
                    if fb_res.records:
                        all_records.extend(fb_res.records)
                except Exception:
                    pass

            # Deduplicate records by id / name
            seen_keys: set[str] = set()
            unique_records: list[dict] = []
            for rec in all_records:
                key = str(rec.get("id") or rec.get("fir_number") or rec.get("name") or str(rec))
                if key not in seen_keys:
                    seen_keys.add(key)
                    unique_records.append(rec)

            text = self._evidence.records_to_text(unique_records)
            citations = self._evidence.records_to_citations(unique_records)

            return ToolResult(
                tool=ToolType.SQL,
                subtask_id=tool_call.subtask_id,
                success=True,
                records=unique_records,
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
