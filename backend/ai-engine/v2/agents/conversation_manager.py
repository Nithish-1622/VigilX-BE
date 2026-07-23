from __future__ import annotations

from uuid import uuid4

from services.conversation_service import ConversationService
from services.translation_service import TranslationService
from v2.agents.base_agent import BaseAgent
from v2.state import V2WorkflowState


class ConversationManagerAgent(BaseAgent):
    """
    Agent 1: Conversation Manager
    Single responsibility: Session lifecycle, message persistence, language detection.

    Wraps V1 ConversationService + TranslationService exactly as-is.
    No new logic added — only wired into the V2 state contract.
    """

    def __init__(
        self,
        conversation_service: ConversationService,
        translation_service: TranslationService,
    ) -> None:
        super().__init__()
        self._conversation = conversation_service
        self._translator = translation_service

    async def run(self, state: V2WorkflowState) -> V2WorkflowState:
        user_id = state["user_id"]
        session_id = state["session_id"]
        raw_question = state["question"]

        # Store original before any mutation
        state["original_question"] = raw_question

        # Translate to English for all downstream processing
        english_question, source_lang = self._translator.translate_to_english(raw_question)
        state["question"] = english_question
        state["source_lang"] = source_lang

        # Persist in V1 ConversationService (full backward compat)
        self._conversation.add_user_message(user_id, session_id, english_question)

        # Build request context headers for downstream REST calls
        correlation_id = state.get("correlation_id") or str(uuid4())
        state["correlation_id"] = correlation_id
        state["context_headers"] = {
            "x-session-id": session_id,
            "x-user-id": user_id,
            "x-correlation-id": correlation_id,
        }

        self.logger.info(
            "Session[%s] User[%s] Lang[%s] | Question: %.80s",
            session_id,
            user_id,
            source_lang,
            english_question,
        )
        return state
