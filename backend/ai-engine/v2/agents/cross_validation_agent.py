from __future__ import annotations

from v2.agents.base_agent import BaseAgent
from v2.schemas.execution_plan import ToolType
from v2.schemas.validation_result import CrossCheckReport, Inconsistency
from v2.state import V2WorkflowState


class CrossValidationAgent(BaseAgent):
    """
    Agent 14: Cross Validation Agent
    Single responsibility: Compare SQL, Graph, and RAG outputs for the same entities.
    Flag factual inconsistencies. Produce a CrossCheckReport.

    Warning-severity inconsistencies do NOT block LLM reasoning.
    Error-severity inconsistencies (only for critical contradictions) may block.
    """

    async def run(self, state: V2WorkflowState) -> V2WorkflowState:
        tool_results = state.get("tool_results", [])

        sql_records = next(
            (tr.records for tr in tool_results if tr.tool == ToolType.SQL and tr.success), []
        )
        graph_records = next(
            (tr.records for tr in tool_results if tr.tool == ToolType.GRAPH and tr.success), []
        )
        rag_records = next(
            (tr.records for tr in tool_results if tr.tool == ToolType.RAG and tr.success), []
        )

        inconsistencies: list[Inconsistency] = []

        # ── Check 1: Person name overlap between SQL and Graph ────────────────
        sql_names = {
            str(r.get("name", "")).lower().strip()
            for r in sql_records
            if r.get("name")
        }
        graph_names = {
            str(r.get("name", "") or r.get("accused_1", "")).lower().strip()
            for r in graph_records
            if r.get("name") or r.get("accused_1")
        }
        sql_only_names = sql_names - graph_names - {""}
        graph_only_names = graph_names - sql_names - {""}
        if sql_only_names or graph_only_names:
            inconsistencies.append(
                Inconsistency(
                    field="person_names",
                    value_from_sql=", ".join(sorted(sql_only_names)[:5]) or None,
                    value_from_graph=", ".join(sorted(graph_only_names)[:5]) or None,
                    severity="warning",
                )
            )

        # ── Check 2: FIR number consistency ──────────────────────────────────
        import re
        fir_pattern = re.compile(r"\b(FIR-\d{4}-\d+)\b", re.IGNORECASE)

        def extract_firs(records: list[dict]) -> set[str]:
            found: set[str] = set()
            for r in records:
                text = " ".join(str(v) for v in r.values() if v)
                found.update(m.upper() for m in fir_pattern.findall(text))
            return found

        sql_firs = extract_firs(sql_records)
        graph_firs = extract_firs(graph_records)
        rag_firs = extract_firs(rag_records)

        all_firs = sql_firs | graph_firs | rag_firs
        if len(all_firs) > 0:
            # Flag if RAG mentions FIR not in SQL (potential hallucination risk)
            rag_only_firs = rag_firs - sql_firs - graph_firs
            if rag_only_firs:
                inconsistencies.append(
                    Inconsistency(
                        field="fir_numbers",
                        value_from_sql=", ".join(sorted(sql_firs)) or "none",
                        value_from_rag=", ".join(sorted(rag_only_firs)),
                        severity="warning",
                    )
                )

        # ── Determine overall consistency ─────────────────────────────────────
        error_count = sum(1 for i in inconsistencies if i.severity == "error")
        overall_consistent = error_count == 0  # Warnings alone don't fail consistency

        report = CrossCheckReport(
            checked=True,
            inconsistencies=inconsistencies,
            sql_graph_agreement=len([i for i in inconsistencies if i.field == "person_names"]) == 0,
            sql_rag_agreement=len([i for i in inconsistencies if i.field == "fir_numbers"]) == 0,
            overall_consistent=overall_consistent,
            validation_notes=(
                f"Validated {len(sql_records)} SQL + {len(graph_records)} Graph + {len(rag_records)} RAG records. "
                f"{len(inconsistencies)} inconsistencies detected."
            ),
        )

        state["validation_report"] = report
        self.logger.info(
            "Cross-validation: %d inconsistencies (consistent=%s)",
            len(inconsistencies),
            overall_consistent,
        )
        return state
