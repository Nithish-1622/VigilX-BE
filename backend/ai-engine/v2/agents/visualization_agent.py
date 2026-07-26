from __future__ import annotations

from uuid import uuid4

from schemas.common import Citation
from v2.schemas.chart_spec import ChartSpec, ChartType
from v2.schemas.execution_plan import ToolCall, ToolType
from v2.schemas.tool_result import ToolResult
from v2.state import V2WorkflowState


class VisualizationAgent:
    """
    Agent 11: Visualization Agent
    Single responsibility: Generate frontend-consumable chart specification JSON.

    Does NOT generate images. Returns ChartSpec objects that the React frontend
    renders via Recharts / D3 / Leaflet based on chart_type.

    Inspects available evidence data and recommends the most appropriate chart types.
    Must run AFTER_ALL per ToolCapabilityRegistry (needs all evidence data).
    """

    async def handle(self, tool_call: ToolCall, state: V2WorkflowState) -> ToolResult:
        """Handler registered with ToolRouterAgent for ToolType.VISUALIZATION."""
        tool_results = state.get("tool_results", [])
        plan = state.get("execution_plan")
        intent = plan.intent if plan else "case_lookup"

        all_records = [rec for tr in tool_results if tr.success for rec in tr.records]
        preferred = (tool_call.parameters or {}).get("preferred_type")

        specs = self._recommend_charts(intent, all_records, tool_results, preferred)

        text = f"Generated {len(specs)} chart spec(s): {[s.chart_type.value for s in specs]}"
        records = [spec.model_dump() for spec in specs]

        return ToolResult(
            tool=ToolType.VISUALIZATION,
            subtask_id=tool_call.subtask_id,
            success=True,
            records=records,
            text=text,
            citations=[Citation(source="visualization_engine", snippet=text)],
            metadata={"chart_count": len(specs)},
        )

    def _recommend_charts(
        self,
        intent: str,
        records: list[dict],
        tool_results,
        preferred: str | None,
    ) -> list[ChartSpec]:
        specs: list[ChartSpec] = []

        # Override: if preferred type specified, attempt it first
        if preferred:
            spec = self._make_preferred(preferred, records, intent)
            if spec:
                specs.append(spec)
                return specs  # Return early with user-preferred chart

        # --- Timeline chart for temporal intents ---
        if intent in {"timeline_query", "case_lookup", "investigation_status"}:
            timeline_data = [
                r for r in records
                if any(f in r for f in ["timestamp", "reported_date_time", "event", "crimeregistereddate"])
            ]
            if timeline_data:
                specs.append(ChartSpec(
                    chart_id=str(uuid4())[:8],
                    chart_type=ChartType.TIMELINE,
                    title="Investigation Timeline",
                    description="Chronological sequence of case events and records",
                    data=timeline_data[:25],
                    x_axis="timestamp",
                    y_axis="event",
                    rationale="Timeline chosen because query relates to case chronology",
                ))

        # --- Bar chart for statistics ---
        if intent in {"statistics_query", "evidence_summary", "case_lookup"}:
            crime_dist: dict[str, int] = {}
            for r in records:
                ct = r.get("crime_type") or r.get("crimetypetext")
                if ct:
                    crime_dist[str(ct)] = crime_dist.get(str(ct), 0) + 1
            if crime_dist:
                specs.append(ChartSpec(
                    chart_id=str(uuid4())[:8],
                    chart_type=ChartType.BAR,
                    title="Crime Type Distribution",
                    description="Number of cases per crime type",
                    data=[{"label": k, "value": v} for k, v in sorted(crime_dist.items(), key=lambda x: x[1], reverse=True)],
                    x_axis="label",
                    y_axis="value",
                    rationale="Bar chart chosen for categorical crime type comparison",
                ))

        # --- Network chart for graph intent ---
        if intent in {"criminal_network", "suspect_query"}:
            graph_results = [tr for tr in tool_results if tr.tool == ToolType.GRAPH and tr.success]
            if graph_results:
                network_data = graph_results[0].records[:30]
                if network_data:
                    specs.append(ChartSpec(
                        chart_id=str(uuid4())[:8],
                        chart_type=ChartType.NETWORK,
                        title="Criminal Network Graph",
                        description="Relationship network between suspects, victims, and cases",
                        data=network_data,
                        rationale="Network chart chosen to visualize suspect relationships",
                    ))

        # --- Geo map if location data exists ---
        geo_records = [r for r in records if r.get("latitude") and r.get("longitude")]
        if geo_records:
            specs.append(ChartSpec(
                chart_id=str(uuid4())[:8],
                chart_type=ChartType.GEO,
                title="Crime Incident Locations",
                description="Geographic distribution of crime incidents",
                data=geo_records[:50],
                rationale="Geo map chosen because latitude/longitude data is available",
            ))

        # --- Pie chart for status breakdown ---
        status_dist: dict[str, int] = {}
        for r in records:
            s = r.get("status")
            if s:
                status_dist[str(s)] = status_dist.get(str(s), 0) + 1
        if len(status_dist) > 1:
            specs.append(ChartSpec(
                chart_id=str(uuid4())[:8],
                chart_type=ChartType.PIE,
                title="Case Status Breakdown",
                description="Proportion of cases by investigation status",
                data=[{"label": k, "value": v} for k, v in status_dist.items()],
                rationale="Pie chart chosen for status proportion comparison",
            ))

        return specs[:4]  # Cap at 4 charts per response

    def _make_preferred(self, preferred: str, records: list[dict], intent: str) -> ChartSpec | None:
        """Attempt to create a chart of the preferred type if data allows."""
        try:
            chart_type = ChartType(preferred.lower())
        except ValueError:
            return None

        return ChartSpec(
            chart_id=str(uuid4())[:8],
            chart_type=chart_type,
            title=f"{chart_type.value.title()} Chart",
            description=f"Officer-requested {chart_type.value} visualization",
            data=records[:30],
            rationale="Preferred chart type requested explicitly",
        )
