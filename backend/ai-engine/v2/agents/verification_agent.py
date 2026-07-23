from __future__ import annotations

from v2.agents.base_agent import BaseAgent
from v2.schemas.investigation_response import InvestigationResponse
from v2.state import V2WorkflowState

# Minimum confidence score required to proceed to LLM reasoning
_MIN_CONFIDENCE = 0.15


class VerificationAgent(BaseAgent):
    """
    Agent 15: Verification Agent (Evidence Gate)
    Single responsibility: Verify evidence is sufficient BEFORE invoking the LLM.

    This is the most critical agent in the pipeline.
    Its purpose is to prevent LLM hallucination at the root.

    Gate logic:
    1. No evidence bundle → clarification
    2. Evidence threshold not met → clarification
    3. Confidence below minimum → clarification
    4. Hard validation errors (error severity) → clarification
    5. Only warnings → pass through (log but don't block)

    If gate fails: sets verification_passed=False, pre-populates clarification response.
    If gate passes: sets verification_passed=True.
    """

    async def run(self, state: V2WorkflowState) -> V2WorkflowState:
        bundle = state.get("evidence_bundle")
        validation = state.get("validation_report")

        # ── Gate 1: No evidence retrieved ─────────────────────────────────────
        if bundle is None or bundle.evidence_count == 0:
            self._fail(
                state,
                "No evidence was retrieved from available data sources. "
                "Could you provide more specific details such as a FIR number, "
                "accused name, or the approximate date of the incident?",
            )
            self.logger.warning("Verification FAILED: no evidence bundle")
            return state

        # ── Gate 2: Evidence threshold not met ────────────────────────────────
        if not bundle.threshold_met:
            self._fail(
                state,
                f"Retrieved {bundle.evidence_count} evidence item(s), which is below the "
                f"required threshold for a reliable answer. Please provide additional details: "
                f"FIR number, accused name, date range, or district.",
            )
            self.logger.warning(
                "Verification FAILED: threshold not met (count=%d)", bundle.evidence_count
            )
            return state

        # ── Gate 3: Confidence below minimum ──────────────────────────────────
        if bundle.overall_confidence < _MIN_CONFIDENCE:
            self._fail(
                state,
                f"Available evidence has low confidence ({bundle.confidence_label}). "
                "Please narrow your search with a specific FIR number, accused name, or date.",
            )
            self.logger.warning(
                "Verification FAILED: low confidence=%.3f", bundle.overall_confidence
            )
            return state

        # ── Gate 4: Hard validation errors (only errors, not warnings) ─────────
        if validation and not validation.overall_consistent:
            self._fail(
                state,
                "Conflicting information was found across data sources. "
                "Please verify the case details and try again with a more specific query.",
            )
            self.logger.warning("Verification FAILED: cross-source hard inconsistencies")
            return state

        # ── All gates passed ──────────────────────────────────────────────────
        state["verification_passed"] = True
        if validation and validation.inconsistencies:
            self.logger.info(
                "Verification PASSED with %d warning(s) (not blocking)",
                len(validation.inconsistencies),
            )
        else:
            self.logger.info(
                "Verification PASSED: confidence=%.3f (%s)",
                bundle.overall_confidence,
                bundle.confidence_label,
            )
        return state

    def _fail(self, state: V2WorkflowState, clarification_question: str) -> None:
        """Pre-populate the final response in clarification mode."""
        state["verification_passed"] = False

        plan = state.get("execution_plan")
        state["final_response"] = InvestigationResponse(
            session_id=state.get("session_id", ""),
            user_id=state.get("user_id", ""),
            intent=plan.intent if plan else "unknown",
            executive_summary="",
            clarification_needed=True,
            clarification_question=clarification_question,
        )
