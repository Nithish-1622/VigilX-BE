from __future__ import annotations

from typing import Any, TypedDict

from v2.schemas.execution_plan import ExecutionPlan
from v2.schemas.investigation_response import InvestigationResponse
from v2.schemas.ranked_evidence import EvidenceBundle
from v2.schemas.tool_result import AggregatedEvidence, ToolResult
from v2.schemas.validation_result import CrossCheckReport


class V2WorkflowState(TypedDict, total=False):
    """
    Full state object passed through the 20-agent LangGraph pipeline.

    Backward-compatible: all V1 field names preserved.
    V2 adds fields without touching existing ones.
    """

    # ── Inherited from V1 (kept identical for compatibility) ──────────────────
    user_id: str
    session_id: str
    question: str                         # Always English after Agent 1 translation
    auth_header: str | None
    correlation_id: str

    # ── Agent 1: ConversationManager additions ─────────────────────────────────
    original_question: str               # Raw input before translation
    source_lang: str                     # ISO-639 language code (e.g. "kn", "hi")
    context_headers: dict[str, str]      # x-session-id, x-user-id, x-correlation-id

    # ── Agent 2: ContextMemory additions ──────────────────────────────────────
    history_count: int
    conversation_summary: str

    # ── Agent 3: Planning additions ────────────────────────────────────────────
    available_tool_names: list[str]      # From ToolCapabilityRegistry
    execution_plan: ExecutionPlan | None

    # ── Agent 4: QueryDecomposition additions ─────────────────────────────────
    decomposed_subtasks: list[dict[str, Any]]

    # ── Agent 5: ToolRouter additions ─────────────────────────────────────────
    tool_results: list[ToolResult]
    aggregated_evidence: AggregatedEvidence | None

    # ── Agent 12: EvidenceFusion (refines aggregated_evidence) ────────────────
    # (no new fields — refines aggregated_evidence in place)

    # ── Agent 13: EvidenceRanking additions ───────────────────────────────────
    evidence_bundle: EvidenceBundle | None

    # ── Agent 14: CrossValidation additions ───────────────────────────────────
    validation_report: CrossCheckReport | None

    # ── Agent 15: Verification additions ──────────────────────────────────────
    verification_passed: bool

    # ── Agent 16: LLMReasoning additions ──────────────────────────────────────
    reasoning_output: str

    # ── Agent 17: ResponseCritic additions ────────────────────────────────────
    critic_warnings: list[str]

    # ── Agent 19: Recommendation staging ──────────────────────────────────────
    _recommendations: list[str]          # Staging field; consumed by ResponseComposer

    # ── Agent 20: ResponseComposer output ─────────────────────────────────────
    final_response: InvestigationResponse | None
