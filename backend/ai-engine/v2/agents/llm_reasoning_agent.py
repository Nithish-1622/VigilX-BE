from __future__ import annotations

import re

from llm.client import LLMClient
from services.prompt_service import PromptService
from v2.agents.base_agent import BaseAgent
from v2.state import V2WorkflowState


class LLMReasoningAgent(BaseAgent):
    """
    Agent 16: LLM Reasoning Agent
    THE ONLY AGENT IN THE ENTIRE PIPELINE THAT CALLS THE LLM.

    Single responsibility: Given pre-verified, pre-ranked, cross-validated evidence,
    generate a factual investigative reasoning narrative.

    Contract:
    - ONLY called if verification_passed = True
    - ONLY receives top_evidence_text (not raw records)
    - NEVER queries databases
    - NEVER makes tool calls
    - Falls back to deterministic formatting if LLM is unavailable
    """

    def __init__(self, prompt_service: PromptService, llm_client: LLMClient) -> None:
        super().__init__()
        self._prompt_service = prompt_service
        self._llm_client = llm_client

    async def run(self, state: V2WorkflowState) -> V2WorkflowState:
        # Hard gate: do not invoke LLM if verification failed
        if not state.get("verification_passed", False):
            state["reasoning_output"] = ""
            self.logger.info("LLM skipped — verification_passed=False")
            return state

        bundle = state.get("evidence_bundle")
        evidence_text = bundle.top_evidence_text if bundle else ""

        if not evidence_text.strip():
            state["reasoning_output"] = (
                "Insufficient evidence to provide a factual answer. "
                "Please refine your query with specific case details."
            )
            return state

        question = state["question"]
        summary = state.get("conversation_summary", "No prior conversation context.")
        confidence_label = bundle.confidence_label if bundle else "low"
        source_count = str(bundle.source_diversity if bundle else 0)

        prompt = self._prompt_service.render(
            "reasoning_v2.txt",
            question=question,
            conversation_summary=summary,
            evidence_block=evidence_text,
            confidence_label=confidence_label,
            source_count=source_count,
        )

        self.logger.info(
            "LLM call: %d chars of evidence | confidence=%s | sources=%s",
            len(evidence_text),
            confidence_label,
            source_count,
        )

        response = (await self._llm_client.generate(prompt)).strip()

        if not response:
            response = self._deterministic_format(evidence_text)
            self.logger.warning("LLM returned empty — using deterministic fallback")

        state["reasoning_output"] = response
        self.logger.info("LLM reasoning complete: %d chars", len(response))
        return state

    def _deterministic_format(self, evidence_text: str) -> str:
        """
        Deterministic fallback when LLM is unavailable.
        Formats raw evidence into a structured bullet list.
        Strips source prefixes like '[django_api|EVD-001]'.
        """
        lines = [ln.strip() for ln in evidence_text.split("\n") if ln.strip()]
        formatted: list[str] = ["Based on available records:"]
        seen: set[str] = set()

        for line in lines[:6]:
            # Strip '[source|ref]' prefix
            clean = re.sub(r"^\[.*?\]\s*", "", line)
            # Deduplicate by first 60 chars
            key = clean[:60]
            if key not in seen and clean:
                formatted.append(f"• {clean}")
                seen.add(key)

        return "\n".join(formatted)
