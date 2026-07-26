from __future__ import annotations

import statistics
from collections import Counter
from datetime import datetime, timedelta

from schemas.common import Citation
from v2.schemas.execution_plan import ToolCall, ToolType
from v2.schemas.tool_result import ToolResult
from v2.state import V2WorkflowState


class ForecastAgent:
    """
    OPTIONAL Agent: Forecast Agent
    Single responsibility: Statistical crime trend forecasting.

    NOT part of the core pipeline.
    Only invoked when the ExecutionPlan includes ToolType.FORECAST.
    Only activated for explicit prediction/forecast queries.

    Uses Python's statistics module and moving averages — NO LLM.
    Reads historical records from SQL tool results already in state.
    """

    async def handle(self, tool_call: ToolCall, state: V2WorkflowState) -> ToolResult:
        """Handler registered with ToolRouterAgent for ToolType.FORECAST."""
        params = tool_call.parameters or {}
        horizon_days = int(params.get("horizon_days", 30))
        method = params.get("method", "moving_average")

        # Pull SQL records from already-executed tool results
        historical_records: list[dict] = []
        for tr in state.get("tool_results", []):
            if tr.tool == ToolType.SQL and tr.success:
                historical_records.extend(tr.records)

        if not historical_records:
            return ToolResult(
                tool=ToolType.FORECAST,
                subtask_id=tool_call.subtask_id,
                success=False,
                error="Forecast requires historical SQL records. No data available.",
            )

        try:
            forecast_records, text = self._forecast(historical_records, horizon_days, method)
            return ToolResult(
                tool=ToolType.FORECAST,
                subtask_id=tool_call.subtask_id,
                success=True,
                records=forecast_records,
                text=text,
                citations=[
                    Citation(
                        source="forecast_engine",
                        snippet=text[:200],
                    )
                ],
                metadata={
                    "method": method,
                    "horizon_days": horizon_days,
                    "historical_records": len(historical_records),
                },
            )
        except Exception as exc:
            return ToolResult(
                tool=ToolType.FORECAST,
                subtask_id=tool_call.subtask_id,
                success=False,
                error=f"Forecast computation failed: {exc}",
            )

    def _forecast(
        self,
        records: list[dict],
        horizon: int,
        method: str,
    ) -> tuple[list[dict], str]:
        """Moving average forecast over historical daily crime counts."""
        date_fields = [
            "reported_date_time", "incident_date_time",
            "crimeregistereddate", "created_at",
        ]

        # Build time-series: count records per day
        date_counts: Counter = Counter()
        for rec in records:
            for df in date_fields:
                val = rec.get(df)
                if val:
                    try:
                        dt = datetime.fromisoformat(str(val)[:10])
                        date_counts[dt.strftime("%Y-%m-%d")] += 1
                        break
                    except (ValueError, TypeError):
                        pass

        if not date_counts:
            return [], "Insufficient time-series data — no valid date fields found in records"

        sorted_dates = sorted(date_counts.items())
        values = [v for _, v in sorted_dates]

        # Moving average
        window = min(7, len(values))
        if len(values) >= window:
            recent = values[-window:]
            avg = statistics.mean(recent)
        else:
            avg = statistics.mean(values)

        variance = statistics.variance(values) if len(values) > 1 else 0.0
        trend = "stable"
        if len(values) >= 3:
            recent_avg = statistics.mean(values[-3:])
            older_avg = statistics.mean(values[:3])
            if recent_avg > older_avg * 1.15:
                trend = "increasing"
            elif recent_avg < older_avg * 0.85:
                trend = "decreasing"

        # Project forward (cap return at 7 days preview)
        last_date = datetime.fromisoformat(sorted_dates[-1][0])
        forecast_records: list[dict] = []
        preview_days = min(7, horizon)
        for i in range(1, preview_days + 1):
            future = last_date + timedelta(days=i)
            forecast_records.append({
                "date": future.strftime("%Y-%m-%d"),
                "predicted_cases": round(avg),
                "trend": trend,
                "method": method,
                "confidence": "low" if variance > 5 else "medium",
            })

        text = (
            f"Forecast ({method}): predicted avg {avg:.1f} cases/day "
            f"over next {horizon} days. Trend: {trend}. "
            f"Based on {len(records)} historical records."
        )
        return forecast_records, text
