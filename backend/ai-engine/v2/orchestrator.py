from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from llm.client import LLMClient
from rag.retriever import RAGRetriever
from schemas.conversation import AskRequest
from services.conversation_service import ConversationService
from services.conversation_summary_service import ConversationSummaryService
from services.evidence_service import EvidenceService
from services.prompt_service import PromptService
from services.rest_gateway import DjangoRestGateway
from services.sql_agent_service import SQLAgentService
from services.sql_query_planner import SQLAgentPlanner
from services.translation_service import TranslationService
from utils.logging import get_logger

from v2.agents.analytics_agent import AnalyticsAgent
from v2.agents.citation_agent import CitationAgent
from v2.agents.context_memory import ContextMemoryAgent
from v2.agents.conversation_manager import ConversationManagerAgent
from v2.agents.cross_validation_agent import CrossValidationAgent
from v2.agents.evidence_fusion_agent import EvidenceFusionAgent
from v2.agents.evidence_ranking_agent import EvidenceRankingAgent
from v2.agents.forecast_agent import ForecastAgent
from v2.agents.graph_agent import GraphIntelligenceAgent
from v2.agents.llm_reasoning_agent import LLMReasoningAgent
from v2.agents.planning_agent import PlanningAgent
from v2.agents.python_tool_agent import PythonToolAgent
from v2.agents.query_decomposition_agent import QueryDecompositionAgent
from v2.agents.recommendation_agent import RecommendationAgent
from v2.agents.response_composer import ResponseComposerAgent
from v2.agents.response_critic_agent import ResponseCriticAgent
from v2.agents.semantic_retrieval_agent import SemanticRetrievalAgent
from v2.agents.sql_tool_agent import SQLToolAgent
from v2.agents.tool_router import ToolRouterAgent
from v2.agents.verification_agent import VerificationAgent
from v2.agents.visualization_agent import VisualizationAgent
from v2.schemas.execution_plan import ToolType
from v2.schemas.investigation_response import InvestigationResponse
from v2.state import V2WorkflowState

logger = get_logger(__name__)

# ── LangGraph availability guard (matches V1 pattern) ────────────────────────
try:
    from langgraph.graph import END, START, StateGraph  # type: ignore
    _LANGGRAPH_AVAILABLE = True
    logger.info("LangGraph available — V2 pipeline will use StateGraph")
except Exception:
    END = "END"
    START = "START"
    StateGraph = None
    _LANGGRAPH_AVAILABLE = False
    logger.warning("LangGraph not available — V2 pipeline will run sequentially")


class V2AIOrchestrator:
    """
    VigilX V2 Multi-Agent Orchestrator.

    Constructs and wires all 20 agents into a LangGraph StateGraph.
    Single entry point: await orchestrator.run(AskRequest, auth_header)

    LLM is invoked ONLY at Agent 16 (LLMReasoningAgent).
    All other agents use deterministic computation, V1 services, or external APIs.

    Pipeline (conditional branch after Agent 15):
      1-5: Conversation → Planning → Decomposition → Tool Routing
      6-11: Tool Agents (parallel where independent)
      12-15: Evidence intelligence layer
      [Gate] verification_passed ?
        TRUE  → 16 LLMReasoning → 17 Critic → 18 Citation → 19 Recommendation → 20 Compose
        FALSE → 20 Compose (clarification mode)
    """

    def __init__(self) -> None:
        # ── Shared V1 infrastructure ──────────────────────────────────────────
        v1_prompt_dir = Path(__file__).resolve().parent.parent / "prompts"
        v2_prompt_dir = Path(__file__).resolve().parent / "prompts"
        v2_prompt_dir.mkdir(exist_ok=True)

        v2_prompt_service = PromptService(prompt_dir=v2_prompt_dir)
        v1_prompt_service = PromptService(prompt_dir=v1_prompt_dir)
        llm_client = LLMClient()
        conversation_service = ConversationService()
        evidence_service = EvidenceService()
        rest_gateway = DjangoRestGateway()
        sql_agent_service = SQLAgentService(rest_gateway=rest_gateway)
        sql_agent_planner = SQLAgentPlanner(llm_client=llm_client)

        # ── Agent 1: Conversation Manager ─────────────────────────────────────
        self._conversation_manager = ConversationManagerAgent(
            conversation_service=conversation_service,
            translation_service=TranslationService(),
        )

        # ── Agent 2: Context Memory ───────────────────────────────────────────
        self._context_memory = ContextMemoryAgent(
            conversation_service=conversation_service,
            summary_service=ConversationSummaryService(
                prompt_service=v1_prompt_service,
                llm_client=llm_client,
            ),
        )

        # ── Agent 3: Planning ─────────────────────────────────────────────────
        self._planning_agent = PlanningAgent(
            prompt_service=v2_prompt_service,
            llm_client=llm_client,
        )

        # ── Agent 4: Query Decomposition ──────────────────────────────────────
        self._decomposition_agent = QueryDecompositionAgent(
            prompt_service=v2_prompt_service,
            llm_client=llm_client,
        )

        # ── Agent 5: Tool Router (event-driven parallel) ──────────────────────
        self._tool_router = ToolRouterAgent()

        # Tool agents (handlers registered with router)
        sql_tool = SQLToolAgent(sql_agent_service, sql_agent_planner, evidence_service)
        python_tool = PythonToolAgent()
        graph_tool = GraphIntelligenceAgent()
        rag_tool = SemanticRetrievalAgent(rest_gateway=rest_gateway)
        analytics_tool = AnalyticsAgent()
        visualization_tool = VisualizationAgent()
        forecast_tool = ForecastAgent()

        self._tool_router.register_handler(ToolType.SQL, sql_tool.handle)
        self._tool_router.register_handler(ToolType.PYTHON, python_tool.handle)
        self._tool_router.register_handler(ToolType.GRAPH, graph_tool.handle)
        self._tool_router.register_handler(ToolType.RAG, rag_tool.handle)
        self._tool_router.register_handler(ToolType.ANALYTICS, analytics_tool.handle)
        self._tool_router.register_handler(ToolType.VISUALIZATION, visualization_tool.handle)
        self._tool_router.register_handler(ToolType.FORECAST, forecast_tool.handle)

        # ── Agents 12–15: Intelligence layer ─────────────────────────────────
        self._evidence_fusion = EvidenceFusionAgent(evidence_service=evidence_service)
        self._evidence_ranking = EvidenceRankingAgent(evidence_service=evidence_service)
        self._cross_validation = CrossValidationAgent()
        self._verification = VerificationAgent()

        # ── Agents 16–20: Output layer ────────────────────────────────────────
        self._llm_reasoning = LLMReasoningAgent(
            prompt_service=v2_prompt_service,
            llm_client=llm_client,
        )
        self._response_critic = ResponseCriticAgent()
        self._citation_agent = CitationAgent()
        self._recommendation_agent = RecommendationAgent()
        self._response_composer = ResponseComposerAgent()

        # ── Build LangGraph ───────────────────────────────────────────────────
        self._graph = self._build_graph()
        logger.info(
            "V2AIOrchestrator ready | LangGraph=%s | 20 agents wired",
            _LANGGRAPH_AVAILABLE,
        )

    # ── Public API ────────────────────────────────────────────────────────────

    async def run(
        self,
        req: AskRequest,
        auth_header: str | None = None,
    ) -> InvestigationResponse:
        correlation_id = str(uuid4())

        initial_state: V2WorkflowState = {
            "user_id": req.user_id,
            "session_id": req.session_id,
            "question": req.question,
            "auth_header": auth_header,
            "correlation_id": correlation_id,
            "tool_results": [],
        }

        logger.info(
            "V2 pipeline start | session=%s user=%s corr=%s",
            req.session_id,
            req.user_id,
            correlation_id,
        )

        if self._graph is not None:
            state: V2WorkflowState = await self._graph.ainvoke(initial_state)
        else:
            state = await self._run_sequential(initial_state)

        response = state.get("final_response")
        if response is None:
            response = InvestigationResponse(
                session_id=req.session_id,
                user_id=req.user_id,
                intent="unknown",
                executive_summary="An internal error occurred. Please try again.",
                clarification_needed=True,
                clarification_question="Could you rephrase your question?",
            )

        # Translate response back to officer's language
        source_lang = state.get("source_lang", "en")
        if source_lang != "en" and response.executive_summary:
            try:
                translator = TranslationService()
                response.executive_summary = translator.translate_from_english(
                    response.executive_summary, source_lang
                )
            except Exception as exc:
                logger.warning("Response translation failed: %s", exc)

        # Persist assistant message in V1 ConversationService (backward compat)
        try:
            ConversationService().add_assistant_message(
                req.user_id, req.session_id, response.executive_summary
            )
        except Exception as exc:
            logger.warning("Assistant message persistence failed: %s", exc)

        logger.info(
            "V2 pipeline complete | intent=%s | confidence=%s | critic_passed=%s",
            response.intent,
            response.confidence_label,
            response.critic_passed,
        )
        return response

    # ── LangGraph graph construction ──────────────────────────────────────────

    def _build_graph(self):
        if not _LANGGRAPH_AVAILABLE or StateGraph is None:
            return None

        graph = StateGraph(V2WorkflowState)

        # Register all agent nodes
        graph.add_node("conversation_manager", self._conversation_manager)
        graph.add_node("context_memory", self._context_memory)
        graph.add_node("planning_agent", self._planning_agent)
        graph.add_node("query_decomposition", self._decomposition_agent)
        graph.add_node("tool_router", self._tool_router)
        graph.add_node("evidence_fusion", self._evidence_fusion)
        graph.add_node("evidence_ranking", self._evidence_ranking)
        graph.add_node("cross_validation", self._cross_validation)
        graph.add_node("verification", self._verification)
        graph.add_node("llm_reasoning", self._llm_reasoning)
        graph.add_node("response_critic", self._response_critic)
        graph.add_node("citation_agent", self._citation_agent)
        graph.add_node("recommendation_agent", self._recommendation_agent)
        graph.add_node("response_composer", self._response_composer)

        # Sequential edges through planning phase
        graph.add_edge(START, "conversation_manager")
        graph.add_edge("conversation_manager", "context_memory")
        graph.add_edge("context_memory", "planning_agent")
        graph.add_edge("planning_agent", "query_decomposition")
        graph.add_edge("query_decomposition", "tool_router")

        # Tool router → intelligence layer (always sequential)
        graph.add_edge("tool_router", "evidence_fusion")
        graph.add_edge("evidence_fusion", "evidence_ranking")
        graph.add_edge("evidence_ranking", "cross_validation")
        graph.add_edge("cross_validation", "verification")

        # Conditional branch: verified → reason, else → compose (clarification)
        graph.add_conditional_edges(
            "verification",
            self._route_after_verification,
            {
                "reason": "llm_reasoning",
                "clarify": "response_composer",
            },
        )

        # Verified path: LLM → Critic → Citation → Recommendation → Compose
        graph.add_edge("llm_reasoning", "response_critic")
        graph.add_edge("response_critic", "citation_agent")
        graph.add_edge("citation_agent", "recommendation_agent")
        graph.add_edge("recommendation_agent", "response_composer")
        graph.add_edge("response_composer", END)

        return graph.compile()

    def _route_after_verification(self, state: V2WorkflowState) -> str:
        return "reason" if state.get("verification_passed", False) else "clarify"

    # ── Sequential fallback ───────────────────────────────────────────────────

    async def _run_sequential(self, state: V2WorkflowState) -> V2WorkflowState:
        """
        Fallback sequential execution when LangGraph is not installed.
        Matches the graph topology exactly.
        """
        state = await self._conversation_manager(state)
        state = await self._context_memory(state)
        state = await self._planning_agent(state)
        state = await self._decomposition_agent(state)
        state = await self._tool_router(state)
        state = await self._evidence_fusion(state)
        state = await self._evidence_ranking(state)
        state = await self._cross_validation(state)
        state = await self._verification(state)

        if state.get("verification_passed", False):
            state = await self._llm_reasoning(state)
            state = await self._response_critic(state)
            state = await self._citation_agent(state)
            state = await self._recommendation_agent(state)

        state = await self._response_composer(state)
        return state
