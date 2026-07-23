from __future__ import annotations

from v2.registry.tool_capability import ToolCapability, ToolInputSchema
from v2.schemas.execution_plan import DependencyType, ToolType


class ToolCapabilityRegistry:
    """
    Singleton registry of all available tool agents.

    The PlanningAgent queries this at runtime — no hardcoded tool lists anywhere.
    New tools are added by calling `registry.register(ToolCapability(...))`.
    Tool capabilities are injected into the planning prompt verbatim.

    Usage:
        from v2.registry.tool_registry import tool_registry
        tools = tool_registry.all_enabled()
        prompt_block = tool_registry.names_for_prompt()
    """

    _instance: ToolCapabilityRegistry | None = None
    _capabilities: dict[ToolType, ToolCapability]

    def __new__(cls) -> ToolCapabilityRegistry:
        if cls._instance is None:
            obj = super().__new__(cls)
            obj._capabilities = {}
            obj._register_defaults()
            cls._instance = obj
        return cls._instance

    # ─── Public API ───────────────────────────────────────────────────────────

    def register(self, capability: ToolCapability) -> None:
        """Register or overwrite a tool capability."""
        self._capabilities[capability.tool_type] = capability

    def get(self, tool_type: ToolType) -> ToolCapability | None:
        return self._capabilities.get(tool_type)

    def all_enabled(self) -> list[ToolCapability]:
        """Return all tools that are currently enabled (including optional ones)."""
        return [c for c in self._capabilities.values() if c.enabled]

    def core_tools(self) -> list[ToolCapability]:
        """Return only non-optional enabled tools (for the core pipeline)."""
        return [c for c in self.all_enabled() if not c.is_optional]

    def optional_tools(self) -> list[ToolCapability]:
        """Return optional tools (e.g. Forecast) excluded from the core pipeline."""
        return [c for c in self.all_enabled() if c.is_optional]

    def names_for_prompt(self) -> str:
        """
        Returns a formatted string of all tools for injection into the planning prompt.
        Optional tools are marked [OPTIONAL] so the planner knows to use them sparingly.
        """
        lines: list[str] = []
        for cap in self.all_enabled():
            tag = " [OPTIONAL — only for prediction queries]" if cap.is_optional else ""
            dep = f" (dependency: {cap.default_dependency.value})" if cap.default_dependency != DependencyType.INDEPENDENT else ""
            lines.append(f"- {cap.name}{tag}: {cap.description}{dep}")
            if cap.input_schema.example:
                lines.append(f"  Example params: {cap.input_schema.example}")
        return "\n".join(lines)

    def for_intent(self, intent: str) -> list[ToolCapability]:
        """Return tools that support a given intent (empty supported_intents = supports all)."""
        return [
            c for c in self.all_enabled()
            if not c.supported_intents or intent in c.supported_intents
        ]

    def disable(self, tool_type: ToolType) -> None:
        """Disable a tool without unregistering it."""
        if cap := self._capabilities.get(tool_type):
            cap.enabled = False

    # ─── Default registrations ────────────────────────────────────────────────

    def _register_defaults(self) -> None:
        defaults: list[ToolCapability] = [
            ToolCapability(
                tool_type=ToolType.SQL,
                name="sql_tool",
                description="Query structured case, accused, victim, and investigation records from PostgreSQL via the Django REST API. Best for FIR lookups, suspect details, and structured filtering.",
                input_schema=ToolInputSchema(
                    required=[],
                    optional=["fir_id", "name", "crime_type", "status", "date_start", "date_end", "district"],
                    example={"fir_id": "FIR-2026-001", "crime_type": "ROBBERY"},
                ),
                output_description="List of structured records (FIRs, Accused, Victims, Investigation logs)",
                supported_intents=["case_lookup", "suspect_query", "victim_query", "evidence_summary", "timeline_query", "investigation_status"],
                default_dependency=DependencyType.INDEPENDENT,
                average_latency_ms=300,
            ),
            ToolCapability(
                tool_type=ToolType.GRAPH,
                name="graph_tool",
                description="Traverse Neo4j criminal network graphs. Find suspect relationships, community clusters, centrality scores, shortest paths, and hidden link analysis.",
                input_schema=ToolInputSchema(
                    optional=["suspect_id", "fir_id", "source_id", "target_id", "operation"],
                    example={"suspect_id": "ACC_301", "operation": "hidden_links"},
                ),
                output_description="Graph nodes, edges, network insights, community clusters",
                supported_intents=["criminal_network", "case_lookup", "suspect_query", "investigation_status"],
                default_dependency=DependencyType.INDEPENDENT,
                average_latency_ms=400,
            ),
            ToolCapability(
                tool_type=ToolType.RAG,
                name="rag_tool",
                description="Hybrid semantic + keyword vector search across case documents and briefs stored in Qdrant. Best for finding similar cases, unstructured content, and conceptual queries.",
                input_schema=ToolInputSchema(
                    required=["query"],
                    optional=["limit", "collection"],
                    example={"query": "bank robbery with weapon", "limit": 5},
                ),
                output_description="Semantically similar documents, case briefs, evidence snippets",
                supported_intents=["evidence_summary", "case_lookup", "follow_up"],
                default_dependency=DependencyType.INDEPENDENT,
                average_latency_ms=600,
            ),
            ToolCapability(
                tool_type=ToolType.PYTHON,
                name="python_tool",
                description="Deterministic computation engine: date math, statistical aggregations, financial calculations, regex pattern extraction. Use for ANY computable operation — never LLM.",
                input_schema=ToolInputSchema(
                    required=["operation"],
                    optional=["data", "params", "field"],
                    example={"operation": "count_by", "field": "crime_type"},
                ),
                output_description="Computed results: numbers, dates, statistics, extracted patterns",
                supported_intents=["statistics_query", "timeline_query"],
                default_dependency=DependencyType.INDEPENDENT,
                average_latency_ms=50,
            ),
            ToolCapability(
                tool_type=ToolType.ANALYTICS,
                name="analytics_tool",
                description="Generate timelines, crime trend breakdowns, demographic analysis, and spatio-temporal patterns from already-retrieved SQL/Graph records. Runs after SQL.",
                input_schema=ToolInputSchema(
                    optional=["operation", "group_by", "date_field"],
                    example={"operation": "crime_trends", "group_by": "district"},
                ),
                output_description="Timelines, trend tables, demographic breakdowns, location clusters",
                supported_intents=["statistics_query", "timeline_query", "evidence_summary"],
                default_dependency=DependencyType.AFTER_SQL,
                average_latency_ms=200,
            ),
            ToolCapability(
                tool_type=ToolType.VISUALIZATION,
                name="visualization_tool",
                description="Generate frontend-consumable chart specification JSON (not images). Produces timeline, bar, pie, network, geo, heatmap specs based on available evidence data.",
                input_schema=ToolInputSchema(
                    optional=["preferred_type"],
                    example={"preferred_type": "timeline"},
                ),
                output_description="ChartSpec JSON objects for frontend rendering (Recharts/D3/Leaflet)",
                supported_intents=["statistics_query", "timeline_query", "criminal_network", "evidence_summary"],
                default_dependency=DependencyType.AFTER_ALL,
                average_latency_ms=100,
            ),
            ToolCapability(
                tool_type=ToolType.FORECAST,
                name="forecast_tool",
                description="Statistical crime forecasting using historical data trends and moving averages. NO LLM used. Only invoke for explicit prediction/forecast queries.",
                input_schema=ToolInputSchema(
                    required=[],
                    optional=["horizon_days", "method"],
                    example={"horizon_days": 30, "method": "moving_average"},
                ),
                output_description="Predicted crime occurrence rates, trend confidence, risk indicators",
                supported_intents=["statistics_query"],
                is_optional=True,           # NOT in core pipeline
                default_dependency=DependencyType.AFTER_SQL,
                average_latency_ms=800,
            ),
        ]
        for cap in defaults:
            self.register(cap)


# ─── Module-level singleton ───────────────────────────────────────────────────
# Import this everywhere: from v2.registry.tool_registry import tool_registry
tool_registry = ToolCapabilityRegistry()
