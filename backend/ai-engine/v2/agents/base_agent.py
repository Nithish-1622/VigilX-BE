from __future__ import annotations

from abc import ABC, abstractmethod

from utils.logging import get_logger
from v2.state import V2WorkflowState


class BaseAgent(ABC):
    """
    Abstract base class for all V2 agents.

    CONTRACT:
    - Each agent has EXACTLY ONE responsibility.
    - Each agent receives V2WorkflowState and returns an updated V2WorkflowState.
    - No agent may call the LLM except LLMReasoningAgent (Agent 16).
    - No agent may call external databases except designated Tool Agents (6–11).
    - All agents must be independently testable.
    """

    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    async def run(self, state: V2WorkflowState) -> V2WorkflowState:
        """Execute the agent's single responsibility and return updated state."""
        ...

    async def __call__(self, state: V2WorkflowState) -> V2WorkflowState:
        """
        LangGraph-compatible callable interface.
        All agents are registered as graph nodes via this method.
        """
        self.logger.debug("Agent %s starting", self.__class__.__name__)
        try:
            result = await self.run(state)
            self.logger.debug("Agent %s complete", self.__class__.__name__)
            return result
        except Exception as exc:
            self.logger.exception("Agent %s raised unhandled exception: %s", self.__class__.__name__, exc)
            raise
