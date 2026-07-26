from __future__ import annotations

from collections import Counter
from typing import Any

from schemas.common import Citation
from v2.schemas.execution_plan import ToolCall, ToolType
from v2.schemas.tool_result import ToolResult
from v2.state import V2WorkflowState


class AnalyticsAgent:
    """
    Agent 10: Analytics Agent
    Single responsibility: Compute timelines, crime trends, demographic breakdowns,
    and spatio-temporal patterns from already-retrieved SQL/Graph records.

    Operates ONLY on state["tool_results"] — no DB calls, no LLM.
    Must run AFTER_SQL per the ToolCapabilityRegistry default.
    """

    async def handle(self, tool_call: ToolCall, state: V2WorkflowState) -> ToolResult:
        """Handler registered with ToolRouterAgent for ToolType.ANALYTICS."""
        params = tool_call.parameters or {}
        operation = params.get("operation", "all")

        # Collect records from previous tool results (SQL priority)
        all_records = self._collect_records(state)

        if not all_records:
            return ToolResult(
                tool=ToolType.ANALYTICS,
                subtask_id=tool_call.subtask_id,
                success=True,
                text="No records available for analytics",
                records=[],
            )

        try:
            records_out, text = self._dispatch(operation, all_records, params)
            return ToolResult(
                tool=ToolType.ANALYTICS,
                subtask_id=tool_call.subtask_id,
                success=True,
                records=records_out,
                text=text,
                citations=[Citation(source="analytics_engine", snippet=text[:200])],
            )
        except Exception as exc:
            return ToolResult(
                tool=ToolType.ANALYTICS,
                subtask_id=tool_call.subtask_id,
                success=False,
                error=f"Analytics computation failed: {exc}",
            )

    def _collect_records(self, state: V2WorkflowState) -> list[dict]:
        all_records: list[dict] = []
        for tr in state.get("tool_results", []):
            if tr.success and tr.tool == ToolType.SQL:
                all_records.extend(tr.records)
        # Fallback: include all successful tool records if SQL has none
        if not all_records:
            for tr in state.get("tool_results", []):
                if tr.success:
                    all_records.extend(tr.records)
        return all_records

    def _dispatch(
        self, operation: str, records: list[dict], params: dict
    ) -> tuple[list[dict], str]:
        if operation == "timeline":
            return self._timeline(records, params)
        if operation == "crime_trends":
            return self._crime_trends(records)
        if operation == "demographics":
            return self._demographics(records)
        if operation == "spatio_temporal":
            return self._spatio_temporal(records)
        # Default: run all
        return self._all_analytics(records)

    def _timeline(self, records: list[dict], params: dict) -> tuple[list[dict], str]:
        date_fields = [
            "reported_date_time", "incident_date_time",
            "crimeregistereddate", "created_at", "date",
        ]
        timeline: list[dict] = []
        for rec in records:
            for df in date_fields:
                val = rec.get(df)
                if val:
                    timeline.append({
                        "timestamp": str(val),
                        "event": (
                            f"Case {rec.get('fir_number', rec.get('id', 'N/A'))} — "
                            f"{rec.get('crime_type', rec.get('crimetypetext', ''))}"
                        ),
                        "source": "sql_records",
                        "status": rec.get("status", ""),
                    })
                    break
        timeline.sort(key=lambda x: x["timestamp"])
        return timeline, f"Timeline: {len(timeline)} events reconstructed from records"

    def _crime_trends(self, records: list[dict]) -> tuple[list[dict], str]:
        crime_counts = Counter(
            rec.get("crime_type") or rec.get("crimetypetext") or "Unknown"
            for rec in records
        )
        status_counts = Counter(rec.get("status", "Unknown") for rec in records)
        result = [
            {"metric": "crime_type_distribution", "data": dict(crime_counts.most_common(10))},
            {"metric": "status_distribution", "data": dict(status_counts.most_common(10))},
        ]
        top = crime_counts.most_common(1)
        text = f"Trends over {len(records)} records: {len(crime_counts)} crime types. Top: {top[0] if top else 'N/A'}"
        return result, text

    def _demographics(self, records: list[dict]) -> tuple[list[dict], str]:
        genders = Counter(str(rec.get("gender", "Unknown")).upper() for rec in records)
        ages = [rec.get("age") for rec in records if rec.get("age") is not None]
        numeric_ages = []
        for a in ages:
            try:
                numeric_ages.append(float(a))
            except (ValueError, TypeError):
                pass
        avg_age = round(sum(numeric_ages) / len(numeric_ages), 1) if numeric_ages else None
        result = [
            {"metric": "gender_distribution", "data": dict(genders)},
            {"metric": "average_age", "data": avg_age},
        ]
        text = f"Demographics: {dict(genders)}, avg age: {avg_age or 'N/A'}"
        return result, text

    def _spatio_temporal(self, records: list[dict]) -> tuple[list[dict], str]:
        locations = Counter(
            rec.get("location") or rec.get("district") or rec.get("city") or "Unknown"
            for rec in records
        )
        result = [
            {"metric": "location_distribution", "data": dict(locations.most_common(10))}
        ]
        top_locs = [f"{k}({v})" for k, v in locations.most_common(3)]
        text = f"Spatio-temporal: Top locations — {', '.join(top_locs)}"
        return result, text

    def _all_analytics(self, records: list[dict]) -> tuple[list[dict], str]:
        timeline, _ = self._timeline(records, {})
        trends, _ = self._crime_trends(records)
        demographics, _ = self._demographics(records)
        text = f"Full analytics suite over {len(records)} records"
        return timeline + trends + demographics, text
