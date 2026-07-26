from __future__ import annotations

from services.conversation_service import ConversationService
from services.conversation_summary_service import ConversationSummaryService
from utils.config import settings
from v2.agents.base_agent import BaseAgent
from v2.state import V2WorkflowState


class ContextMemoryAgent(BaseAgent):
    """
    Agent 2: Context Memory
    Single responsibility: Retrieve conversation history and produce a compressed summary.

    Wraps V1 ConversationService + ConversationSummaryService exactly.
    Compression is triggered when history exceeds settings.summarize_history_trigger_items.
    """

    def __init__(
        self,
        conversation_service: ConversationService,
        summary_service: ConversationSummaryService,
    ) -> None:
        super().__init__()
        self._conversation = conversation_service
        self._summary_service = summary_service

    async def run(self, state: V2WorkflowState) -> V2WorkflowState:
        user_id = state["user_id"]
        session_id = state["session_id"]

        history = self._conversation.get_history(user_id, session_id)
        state["history_count"] = len(history)

        # Compress with LLM summary when history is long enough
        if len(history) >= settings.summarize_history_trigger_items:
            summary = await self._summary_service.summarize(history)
        else:
            # V1 lightweight inline summary for short histories
            summary = self._conversation.summarize(user_id, session_id)

        state["conversation_summary"] = summary or "No prior conversation context."
        self.logger.info(
            "History[%d items] | Summary length: %d chars",
            len(history),
            len(state["conversation_summary"]),
        )
        return state
