from __future__ import annotations

import re
import statistics
from datetime import datetime, timedelta
from typing import Any

from schemas.common import Citation
from v2.schemas.execution_plan import ToolCall, ToolType
from v2.schemas.tool_result import ToolResult
from v2.state import V2WorkflowState


class PythonToolAgent:
    """
    Agent 7: Python Tool Agent
    Single responsibility: Deterministic computation engine.

    Handles: date math, statistical aggregations, financial calculations,
    regex pattern extraction, count/group-by operations.

    NEVER uses the LLM for any computable operation.
    Reads from state["tool_results"] for data — never queries databases directly.
    """

    async def handle(self, tool_call: ToolCall, state: V2WorkflowState) -> ToolResult:
        """Handler registered with ToolRouterAgent for ToolType.PYTHON."""
        params = tool_call.parameters or {}
        operation = params.get("operation", "")

        try:
            records_out, text = await self._dispatch(operation, params, state)
            return ToolResult(
                tool=ToolType.PYTHON,
                subtask_id=tool_call.subtask_id,
                success=True,
                records=records_out,
                text=text,
                citations=[Citation(source="python_computation", snippet=text[:200])],
            )
        except Exception as exc:
            return ToolResult(
                tool=ToolType.PYTHON,
                subtask_id=tool_call.subtask_id,
                success=False,
                error=f"Computation error in operation '{operation}': {exc}",
            )

    async def _dispatch(
        self,
        operation: str,
        params: dict[str, Any],
        state: V2WorkflowState,
    ) -> tuple[list[dict], str]:
        if operation == "date_range":
            return self._date_range(params)
        if operation == "statistics":
            return self._compute_statistics(params, state)
        if operation == "regex_extract":
            return self._regex_extract(params, state)
        if operation == "financial_sum":
            return self._financial_sum(params, state)
        if operation == "count_by":
            return self._count_by(params, state)
        if operation == "age_bracket":
            return self._age_bracket(params, state)
        return [], f"Unknown operation: '{operation}'"

    # ── Computation methods ───────────────────────────────────────────────────

    def _date_range(self, params: dict) -> tuple[list[dict], str]:
        start_str = params.get("start")
        end_str = params.get("end")
        end_dt = datetime.fromisoformat(end_str) if end_str else datetime.now()
        if start_str:
            start_dt = datetime.fromisoformat(start_str)
            delta = (end_dt - start_dt).days
            text = f"Date range: {start_dt.date()} → {end_dt.date()} = {delta} days"
            return [{"start": str(start_dt.date()), "end": str(end_dt.date()), "days": delta}], text
        return [], "Invalid date parameters — 'start' is required"

    def _compute_statistics(
        self, params: dict, state: V2WorkflowState
    ) -> tuple[list[dict], str]:
        field = params.get("field", "age")
        values: list[float] = []
        for tr in state.get("tool_results", []):
            for rec in tr.records:
                val = rec.get(field)
                if val is not None:
                    try:
                        values.append(float(val))
                    except (ValueError, TypeError):
                        pass
        if not values:
            return [], f"No numeric data for field '{field}'"
        stats: dict[str, Any] = {
            "field": field,
            "count": len(values),
            "mean": round(statistics.mean(values), 2),
            "median": round(statistics.median(values), 2),
            "min": min(values),
            "max": max(values),
        }
        if len(values) > 1:
            stats["stdev"] = round(statistics.stdev(values), 2)
        text = (
            f"Statistics for '{field}': count={stats['count']}, "
            f"mean={stats['mean']}, median={stats['median']}, "
            f"min={stats['min']}, max={stats['max']}"
        )
        return [stats], text

    def _regex_extract(
        self, params: dict, state: V2WorkflowState
    ) -> tuple[list[dict], str]:
        pattern = params.get("pattern", r"\b\d{10}\b")
        field = params.get("field", "description")
        matches: list[str] = []
        for tr in state.get("tool_results", []):
            for rec in tr.records:
                text_val = str(rec.get(field, ""))
                matches.extend(re.findall(pattern, text_val))
        unique = sorted(set(matches))
        text = f"Regex extraction — pattern: '{pattern}', found {len(unique)} unique matches"
        return [{"pattern": pattern, "field": field, "matches": unique}], text

    def _financial_sum(
        self, params: dict, state: V2WorkflowState
    ) -> tuple[list[dict], str]:
        field = params.get("field", "amount")
        total = 0.0
        count = 0
        for tr in state.get("tool_results", []):
            for rec in tr.records:
                val = rec.get(field)
                if val is not None:
                    try:
                        total += float(val)
                        count += 1
                    except (ValueError, TypeError):
                        pass
        text = f"Financial total for '{field}': ₹{total:,.2f} across {count} records"
        return [{"field": field, "total": total, "count": count}], text

    def _count_by(
        self, params: dict, state: V2WorkflowState
    ) -> tuple[list[dict], str]:
        group_field = params.get("field", "crime_type")
        counts: dict[str, int] = {}
        for tr in state.get("tool_results", []):
            for rec in tr.records:
                val = str(rec.get(group_field, "Unknown"))
                counts[val] = counts.get(val, 0) + 1
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        top_str = ", ".join(f"{k}={v}" for k, v in sorted_counts[:5])
        text = f"Count by '{group_field}': {top_str}"
        return [{"group_field": group_field, "counts": dict(sorted_counts)}], text

    def _age_bracket(
        self, params: dict, state: V2WorkflowState
    ) -> tuple[list[dict], str]:
        """Categorise records into age brackets."""
        brackets: dict[str, int] = {
            "juvenile (<18)": 0,
            "young adult (18-30)": 0,
            "adult (31-50)": 0,
            "senior (51+)": 0,
        }
        for tr in state.get("tool_results", []):
            for rec in tr.records:
                age = rec.get("age")
                if age is None:
                    continue
                try:
                    a = int(float(age))
                    if a < 18:
                        brackets["juvenile (<18)"] += 1
                    elif a <= 30:
                        brackets["young adult (18-30)"] += 1
                    elif a <= 50:
                        brackets["adult (31-50)"] += 1
                    else:
                        brackets["senior (51+)"] += 1
                except (ValueError, TypeError):
                    pass
        text = "Age brackets: " + ", ".join(f"{k}={v}" for k, v in brackets.items() if v > 0)
        return [{"age_brackets": brackets}], text
