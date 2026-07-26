from __future__ import annotations

import re

from v2.agents.base_agent import BaseAgent
from v2.state import V2WorkflowState

# Phrases that indicate LLM speculation (not evidence-grounded)
_HALLUCINATION_SIGNALS = [
    r"\bI believe\b",
    r"\bI think\b",
    r"\bprobably\b",
    r"\blikely\b",
    r"\bpossibly\b",
    r"\bI assume\b",
    r"\bI suspect\b",
    r"\bIt is possible\b",
    r"\bcould be\b",
    r"\bmight be\b",
    r"\bI would guess\b",
    r"\bseems like\b",
    r"\bappears to be\b",
]

# FIR pattern for detecting fabricated case references
_FIR_PATTERN = re.compile(r"\bFIR-\d{4}-\d+\b", re.IGNORECASE)


class ResponseCriticAgent(BaseAgent):
    """
    Agent 17: Response Critic Agent
    Single responsibility: Self-audit the LLM output BEFORE composing the final response.

    Checks performed:
    1. Hallucination language signals (speculation phrases)
    2. FIR number fabrication (response cites FIRs not in evidence)
    3. Bare claim density (long responses with zero grounding)

    On critical issues: patches the reasoning_output to remove unsupported claims.
    All findings recorded as critic_warnings for transparency in the final response.
    """

    async def run(self, state: V2WorkflowState) -> V2WorkflowState:
        reasoning = state.get("reasoning_output", "")
        bundle = state.get("evidence_bundle")
        warnings: list[str] = []

        if not reasoning.strip():
            state["critic_warnings"] = warnings
            return state

        evidence_text = bundle.top_evidence_text if bundle else ""

        # ── Check 1: Hallucination language ───────────────────────────────────
        for signal in _HALLUCINATION_SIGNALS:
            match = re.search(signal, reasoning, re.IGNORECASE)
            if match:
                warnings.append(
                    f"Speculative language detected: '{match.group()}' — "
                    "LLM may be guessing beyond available evidence"
                )

        # ── Check 2: Fabricated FIR numbers ───────────────────────────────────
        response_firs: set[str] = {m.upper() for m in _FIR_PATTERN.findall(reasoning)}
        evidence_firs: set[str] = {m.upper() for m in _FIR_PATTERN.findall(evidence_text)}

        fabricated_firs = response_firs - evidence_firs
        if fabricated_firs:
            warnings.append(
                f"Potentially fabricated FIR reference(s) not in evidence: "
                f"{sorted(fabricated_firs)}"
            )
            # Sanitise: replace unsupported FIR references
            for fir in fabricated_firs:
                reasoning = re.sub(
                    re.escape(fir), "[UNVERIFIED-REF]", reasoning, flags=re.IGNORECASE
                )
            state["reasoning_output"] = reasoning
            self.logger.warning(
                "Critic patched %d fabricated FIR(s): %s",
                len(fabricated_firs),
                fabricated_firs,
            )

        # ── Check 3: Long response with no evidence anchor ────────────────────
        if len(reasoning) > 600 and not evidence_text.strip():
            warnings.append(
                "Response is lengthy but no verified evidence was provided to LLM — "
                "high hallucination risk"
            )

        # ── Summarise ─────────────────────────────────────────────────────────
        if warnings:
            self.logger.warning(
                "Critic Agent: %d warning(s) flagged in LLM response", len(warnings)
            )
            for w in warnings:
                self.logger.warning("  ⚑ %s", w)
        else:
            self.logger.info("Critic Agent: response passed all checks ✓")

        state["critic_warnings"] = warnings
        return state
