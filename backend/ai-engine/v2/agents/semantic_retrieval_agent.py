from __future__ import annotations

from rag.retriever import RAGRetriever
from services.rest_gateway import DjangoRestGateway
from v2.schemas.execution_plan import ToolCall, ToolType
from v2.schemas.tool_result import ToolResult
from v2.state import V2WorkflowState


class SemanticRetrievalAgent:
    """
    Agent 9: Semantic Retrieval Agent (RAG)
    Single responsibility: Hybrid semantic + keyword search via Qdrant + Django REST.

    Wraps V1 RAGRetriever exactly as-is. No changes to retrieval logic.
    """

    def __init__(self, rest_gateway: DjangoRestGateway) -> None:
        self._retriever = RAGRetriever(rest_gateway=rest_gateway)

    async def handle(self, tool_call: ToolCall, state: V2WorkflowState) -> ToolResult:
        """Handler registered with ToolRouterAgent for ToolType.RAG."""
        question = state["question"]
        plan = state.get("execution_plan")
        intent = plan.intent if plan else "case_lookup"
        auth_header = state.get("auth_header")
        context_headers = state.get("context_headers", {})

        try:
            context = await self._retriever.retrieve(
                question=question,
                intent=intent,
                auth_header=auth_header,
                context_headers=context_headers,
            )

            records = [
                {"content": c.snippet, "source": c.source, "score": c.score}
                for c in context.citations
            ]

            return ToolResult(
                tool=ToolType.RAG,
                subtask_id=tool_call.subtask_id,
                success=True,
                records=records,
                text=context.evidence_text,
                citations=context.citations,
            )

        except Exception as exc:
            return ToolResult(
                tool=ToolType.RAG,
                subtask_id=tool_call.subtask_id,
                success=False,
                error=f"RAG retrieval failed: {exc}",
            )
