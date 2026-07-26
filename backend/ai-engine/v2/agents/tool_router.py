from __future__ import annotations

import asyncio
import time
from collections import Counter
from typing import Awaitable, Callable

from schemas.common import Citation
from v2.agents.base_agent import BaseAgent
from v2.schemas.execution_plan import DependencyType, ToolCall, ToolType
from v2.schemas.tool_result import AggregatedEvidence, ToolResult
from v2.state import V2WorkflowState

# Type alias: each tool agent exposes one handler with this signature
ToolHandler = Callable[[ToolCall, V2WorkflowState], Awaitable[ToolResult]]


class ToolRouterAgent(BaseAgent):
    """
    Agent 5: Dynamic Tool Router (Event-Driven)
    Single responsibility: Read ExecutionPlan, execute independent tools in parallel,
    then execute dependent tools sequentially respecting their dependency group.

    Event-driven execution model:
    - Phase 1: All INDEPENDENT tools run concurrently via asyncio.gather()
    - Phase 2: AFTER_SQL tools run after Phase 1 SQL results are available
    - Phase 3: AFTER_GRAPH tools run after Phase 1 Graph results are available
    - Phase 4: AFTER_ALL tools run after all Phase 1-3 tools complete

    Handlers are registered via register_handler() — no hardcoded tool dispatch.
    """

    def __init__(self) -> None:
        super().__init__()
        self._handlers: dict[ToolType, ToolHandler] = {}

    def register_handler(self, tool_type: ToolType, handler: ToolHandler) -> None:
        """Register a tool agent handler. Called once during orchestrator setup."""
        self._handlers[tool_type] = handler
        self.logger.debug("Registered handler for tool: %s", tool_type.value)

    async def run(self, state: V2WorkflowState) -> V2WorkflowState:
        plan = state.get("execution_plan")
        if plan is None or not plan.tool_calls:
            state["tool_results"] = []
            state["aggregated_evidence"] = AggregatedEvidence()
            return state

        all_results: list[ToolResult] = []

        # ── Phase 1: Independent tools in parallel ────────────────────────────
        independent = [tc for tc in plan.tool_calls if tc.dependency == DependencyType.INDEPENDENT]
        if independent:
            self.logger.info(
                "Phase 1: Executing %d independent tools in parallel: %s",
                len(independent),
                [tc.tool.value for tc in independent],
            )
            gathered = await asyncio.gather(
                *[self._execute_tool(tc, state) for tc in independent],
                return_exceptions=True,
            )
            for res in gathered:
                if isinstance(res, Exception):
                    self.logger.error("Parallel tool raised exception: %s", res)
                elif isinstance(res, ToolResult):
                    all_results.append(res)

        # Inject intermediate results so dependent tools can read them
        state["tool_results"] = list(all_results)

        # ── Phase 2: AFTER_SQL dependents ─────────────────────────────────────
        after_sql = sorted(
            [tc for tc in plan.tool_calls if tc.dependency == DependencyType.AFTER_SQL],
            key=lambda x: x.priority,
        )
        for tc in after_sql:
            result = await self._execute_tool(tc, state)
            all_results.append(result)
            state["tool_results"] = list(all_results)

        # ── Phase 3: AFTER_GRAPH dependents ───────────────────────────────────
        after_graph = sorted(
            [tc for tc in plan.tool_calls if tc.dependency == DependencyType.AFTER_GRAPH],
            key=lambda x: x.priority,
        )
        for tc in after_graph:
            result = await self._execute_tool(tc, state)
            all_results.append(result)
            state["tool_results"] = list(all_results)

        # ── Phase 4: AFTER_ALL dependents ─────────────────────────────────────
        after_all = sorted(
            [tc for tc in plan.tool_calls if tc.dependency == DependencyType.AFTER_ALL],
            key=lambda x: x.priority,
        )
        for tc in after_all:
            result = await self._execute_tool(tc, state)
            all_results.append(result)

        state["tool_results"] = all_results
        state["aggregated_evidence"] = self._aggregate(all_results)

        success_count = sum(1 for r in all_results if r.success)
        self.logger.info(
            "Tool routing complete: %d/%d tools succeeded",
            success_count,
            len(all_results),
        )
        return state

    async def _execute_tool(self, tool_call: ToolCall, state: V2WorkflowState) -> ToolResult:
        """Dispatch a single tool call to its registered handler."""
        handler = self._handlers.get(tool_call.tool)
        if handler is None:
            self.logger.warning("No handler registered for tool: %s", tool_call.tool.value)
            return ToolResult(
                tool=tool_call.tool,
                success=False,
                error=f"No handler registered for tool: {tool_call.tool.value}",
            )

        start = time.monotonic()
        try:
            result = await handler(tool_call, state)
            result.execution_time_ms = round((time.monotonic() - start) * 1000, 1)
            self.logger.info(
                "Tool[%s] success=%s records=%d time=%.0fms",
                tool_call.tool.value,
                result.success,
                len(result.records),
                result.execution_time_ms,
            )
            return result
        except Exception as exc:
            elapsed = round((time.monotonic() - start) * 1000, 1)
            self.logger.error(
                "Tool[%s] raised exception after %.0fms: %s",
                tool_call.tool.value,
                elapsed,
                exc,
            )
            return ToolResult(
                tool=tool_call.tool,
                success=False,
                error=str(exc),
                execution_time_ms=elapsed,
            )

    def _aggregate(self, results: list[ToolResult]) -> AggregatedEvidence:
        """Merge all tool results into a single AggregatedEvidence object."""
        all_citations: list[Citation] = []
        all_texts: list[str] = []
        total_records = 0

        for result in results:
            if result.success:
                all_citations.extend(result.citations)
                if result.text.strip():
                    all_texts.append(f"[{result.tool.value}] {result.text}")
                total_records += len(result.records)

        source_breakdown = dict(
            Counter(c.source for c in all_citations if c.source)
        )

        return AggregatedEvidence(
            tool_results=results,
            merged_text="\n".join(all_texts),
            all_citations=all_citations,
            source_breakdown=source_breakdown,
            total_records=total_records,
        )
