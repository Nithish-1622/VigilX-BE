from __future__ import annotations

from pathlib import Path
from typing import Any, TypedDict
from uuid import uuid4

from utils.logging import get_logger

logger = get_logger(__name__)

from llm.client import LLMClient
from rag.retriever import RAGRetriever
from schemas.case_summary import CaseSummary
from schemas.common import Citation, ResponseMetadata, StandardResponse
from schemas.conversation import AskData, AskRequest
from schemas.rest import StructuredQuery
from services.conversation_service import ConversationService
from services.case_summary_service import CaseSummaryService
from services.conversation_summary_service import ConversationSummaryService
from services.evidence_service import EvidenceService
from services.intent_service import IntentService
from services.prompt_service import PromptService
from services.reasoning_service import ReasoningService
from services.sql_query_planner import SQLAgentPlanner
from services.rest_gateway import DjangoRestGateway
from services.sql_agent_service import SQLAgentService
from utils.config import settings

try:
    from langgraph.graph import END, START, StateGraph

    _LANGGRAPH_AVAILABLE = True
except Exception:  # noqa: BLE001
    END = "END"
    START = "START"
    StateGraph = None
    _LANGGRAPH_AVAILABLE = False


class WorkflowState(TypedDict, total=False):
    user_id: str
    session_id: str
    question: str
    auth_header: str | None
    correlation_id: str
    history_count: int
    conversation_summary: str
    intent: str
    query_plan: str | None
    structured_query: StructuredQuery | None
    rag_evidence_text: str
    rag_citations: list[Citation]
    sql_records: list[dict]
    sql_citations: list[Citation]
    merged_evidence_text: str
    merged_citations: list[Citation]
    context_headers: dict[str, str]
    evidence_required: int
    confidence: str
    threshold_met: bool
    answer: str
    case_summary: dict[str, Any] | None


from services.translation_service import TranslationService

class AIOrchestrator:
    def __init__(self) -> None:
        prompt_service = PromptService(prompt_dir=Path(__file__).resolve().parent.parent / "prompts")
        llm_client = LLMClient()

        self._conversation = ConversationService()
        self._conversation_summary = ConversationSummaryService(
            prompt_service=prompt_service,
            llm_client=llm_client,
        )
        self._case_summary = CaseSummaryService(
            prompt_service=prompt_service,
            llm_client=llm_client,
        )
        self._intent = IntentService(prompt_service=prompt_service, llm_client=llm_client)
        self._rest_gateway = DjangoRestGateway()
        self._retriever = RAGRetriever(rest_gateway=self._rest_gateway)
        self._planner = SQLAgentPlanner(llm_client=llm_client)
        self._sql_agent = SQLAgentService(rest_gateway=self._rest_gateway)
        self._evidence = EvidenceService()
        self._reasoning = ReasoningService(
            prompt_service=prompt_service,
            llm_client=llm_client,
        )
        self._translator = TranslationService()
        self._graph = self._build_graph()

    async def run(self, req: AskRequest, auth_header: str | None = None) -> StandardResponse:
        correlation_id = str(uuid4())
        
        # 1. Translate question to English for internal processing
        english_question, source_lang = self._translator.translate_to_english(req.question)
        
        initial_state: WorkflowState = {
            "user_id": req.user_id,
            "session_id": req.session_id,
            "question": english_question,
            "auth_header": auth_header,
            "correlation_id": correlation_id,
        }

        if self._graph is not None:
            state = await self._graph.ainvoke(initial_state)
        else:
            state = await self._run_without_langgraph(initial_state)

        answer = state.get("answer", self._reasoning.insufficient_data_message())
        
        # 2. Translate answer back to user's native language if needed
        if source_lang != 'en':
            answer = self._translator.translate_from_english(answer, source_lang)

        self._conversation.add_assistant_message(req.user_id, req.session_id, answer)

        merged_citations = state.get("merged_citations", [])
        rag_citations = state.get("rag_citations", [])
        sql_citations = state.get("sql_citations", [])
        sql_records = state.get("sql_records", [])
        intent = state.get("intent", "unknown")
        summary = state.get("conversation_summary", "No prior conversation context.")
        case_summary = state.get("case_summary")
        query_plan = state.get("query_plan")
        correlation_id = state.get("correlation_id", correlation_id)
        threshold_met = state.get("threshold_met", False)
        confidence = state.get("confidence", "low")
        evidence_required = state.get("evidence_required", 1)
        evidence_source_breakdown = self._evidence.source_breakdown(merged_citations)

        data = AskData(
            answer=answer,
            intent=intent,
            summary=summary,
            case_summary=case_summary,
            evidence_used=len(merged_citations),
        )

        return StandardResponse(
            success=True,
            message="ok",
            data=data.model_dump(),
            metadata=ResponseMetadata(
                intent=intent,
                query_plan=query_plan,
                evidence_sources=len(merged_citations),
                api_records=len(sql_records),
                langgraph_enabled=self._graph is not None,
                correlation_id=correlation_id,
                confidence=confidence,
                evidence_threshold_met=threshold_met,
                evidence_required=evidence_required,
                rag_citations=len(rag_citations),
                sql_citations=len(sql_citations),
                evidence_source_breakdown=evidence_source_breakdown,
                persistence_enabled=True,
                conversation_store_path=settings.conversation_store_path,
            ),
            citations=merged_citations,
            errors=None,
        )

    def _build_graph(self):
        if not _LANGGRAPH_AVAILABLE or StateGraph is None:
            return None

        graph = StateGraph(WorkflowState)
        graph.add_node("conversation", self._node_conversation)
        graph.add_node("intent", self._node_intent)
        graph.add_node("retrieve", self._node_retrieve)
        graph.add_node("sql", self._node_sql)
        graph.add_node("graph", self._node_graph)
        graph.add_node("reason", self._node_reason)

        graph.add_edge(START, "conversation")
        graph.add_edge("conversation", "intent")
        graph.add_edge("intent", "retrieve")
        graph.add_edge("retrieve", "sql")
        graph.add_edge("sql", "graph")
        graph.add_edge("graph", "reason")
        graph.add_edge("reason", END)
        return graph.compile()

    async def _run_without_langgraph(self, state: WorkflowState) -> WorkflowState:
        state = await self._node_conversation(state)
        state = await self._node_intent(state)
        state = await self._node_retrieve(state)
        state = await self._node_sql(state)
        state = await self._node_graph(state)
        state = await self._node_reason(state)
        return state

    async def _node_conversation(self, state: WorkflowState) -> WorkflowState:
        user_id = state["user_id"]
        session_id = state["session_id"]
        question = state["question"]

        self._conversation.add_user_message(user_id, session_id, question)
        history = self._conversation.get_history(user_id, session_id)
        if len(history) >= settings.summarize_history_trigger_items:
            summary = await self._conversation_summary.summarize(history)
        else:
            summary = self._conversation.summarize(user_id, session_id)

        state["history_count"] = len(history)
        state["conversation_summary"] = summary
        state["context_headers"] = {
            "x-session-id": session_id,
            "x-user-id": user_id,
            "x-correlation-id": state.get("correlation_id", str(uuid4())),
        }
        return state

    async def _node_intent(self, state: WorkflowState) -> WorkflowState:
        user_id = state["user_id"]
        session_id = state["session_id"]
        question = state["question"]
        history = self._conversation.get_history(user_id, session_id)

        intent = await self._intent.detect(question, history)
        structured_query = await self._planner.make_plan(intent, question)
        
        logger.info("Resolved Entity - Question: '%s', History size: %d", question, len(history))
        
        state["intent"] = intent
        state["structured_query"] = structured_query
        state["query_plan"] = structured_query.model_dump_json()
        return state

    async def _node_retrieve(self, state: WorkflowState) -> WorkflowState:
        question = state["question"]
        intent = state.get("intent", "unknown")
        auth_header = state.get("auth_header")
        context_headers = state.get("context_headers", {})
        retrieved = await self._retriever.retrieve(
            question,
            intent,
            auth_header=auth_header,
            context_headers=context_headers,
        )
        state["rag_evidence_text"] = retrieved.evidence_text
        state["rag_citations"] = retrieved.citations
        return state

    async def _node_sql(self, state: WorkflowState) -> WorkflowState:
        import re
        from schemas.rest import RestCapability
        
        structured_query = state.get("structured_query")
        auth_header = state.get("auth_header")
        context_headers = state.get("context_headers", {})
        # -----------------------------------------------------------------
        # Automatic metadata persistence for the universal adapter
        # -----------------------------------------------------------------
        import os
        from database.adapter import ConnectorRegistry
        metadata_url = os.getenv("POSTGRES_METADATA_URL") or os.getenv("DATABASE_URL")
        if metadata_url:
            try:
                async with ConnectorRegistry.create_connector(
                    connection_string=metadata_url,
                    table_name="metadata_sync"
                ) as meta_connector:
                    await meta_connector.sync_metadata()
            except Exception as e:
                logger.warning("Metadata sync failed for %s: %s", metadata_url, e)
        # Execute SQL plan using the universal adapter
        sql_result = await self._sql_agent.execute_plan(
            structured_query,
            auth_header=auth_header,
            context_headers=context_headers,
        )
        sql_records = sql_result.records
        sql_citations = self._evidence.records_to_citations(sql_records)

        rag_citations = state.get("rag_citations", [])
        rag_text = state.get("rag_evidence_text", "")
        sql_text = self._evidence.records_to_text(sql_records)

        # Dynamic Case Mapping: If accused/victim records are retrieved but no case record,
        # fetch the matching case details dynamically from /api/cases/ to provide the context linking
        # the case UUID to the case number (e.g. mapping 0000...0065 to FIR-2026-101).
        extra_citations = []
        extra_texts = []
        
        fir_ids = set()
        for record in sql_records:
            fir_id = record.get("fir")
            if fir_id:
                fir_ids.add(fir_id)
                
        for c in rag_citations:
            fir_match = re.search(r'\bfir=([a-f0-9-]{36})\b', c.snippet, re.IGNORECASE)
            if fir_match:
                fir_ids.add(fir_match.group(1))

        if fir_ids:
            for f_id in fir_ids:
                case_query = StructuredQuery(
                    capability=RestCapability.CASE_SEARCH,
                    intent="case_lookup",
                    question=state["question"],
                    query_text=state["question"],
                    filters={"fir_id": f_id}
                )
                try:
                    case_res = self._rest_gateway.invoke(
                        case_query,
                        auth_header=auth_header,
                        context_headers=context_headers
                    )
                    if case_res.success:
                        case_items = case_res.payload.get("items", [])
                        if isinstance(case_items, list):
                            for item in case_items:
                                extra_texts.append(self._evidence.format_row(item))
                                extra_citations.append(
                                    Citation(
                                        source="case_lookup",
                                        reference_id=item.get("id"),
                                        snippet=self._evidence.format_row(item),
                                        score=None
                                    )
                                )
                except Exception as ex:
                    logger.warning("Failed to fetch dynamic case mapping for %s: %s", f_id, ex)

        extra_text_block = "\n".join(extra_texts)
        merged_evidence = "\n".join(part for part in [rag_text, sql_text, extra_text_block] if part)
        merged_citations = [*rag_citations, *sql_citations, *extra_citations]

        logger.info("Retrieved REST payload: %s", sql_records)
        logger.info("Parsed evidence: %s", merged_evidence)

        state["sql_records"] = sql_records
        state["sql_citations"] = sql_citations
        state["merged_evidence_text"] = merged_evidence
        state["merged_citations"] = merged_citations
        if state.get("intent") in {"case_lookup", "timeline_query", "evidence_summary"}:
            case_summary = await self._case_summary.generate(
                question=state["question"],
                conversation_summary=state.get("conversation_summary", "No prior conversation context."),
                evidence_block=merged_evidence,
                citations=merged_citations,
            )
            state["case_summary"] = case_summary.model_dump()
        return state

    async def _node_graph(self, state: WorkflowState) -> WorkflowState:
        # 3.10 Knowledge Graph + LLM Synthesis
        # Inject ProfileGenerator/NetworkAnalyzer graph output into the context.
        intent = state.get("intent")
        
        # We only bother querying the graph if it's a person/suspect search 
        # or community search to save latency.
        if intent in ["case_lookup", "criminal_network", "investigation_status"]:
            try:
                import os
                from neo4j import GraphDatabase
                uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
                driver = GraphDatabase.driver(uri, auth=(os.environ.get("NEO4J_USER"), os.environ.get("NEO4J_PASSWORD")))
                
                # Fetch a basic summary of the central suspect's network or active community.
                # Since we don't have a specific ID, we just ask for a general insight if applicable,
                # or in a real system we'd extract the suspect ID from `state["structured_query"]`.
                
                query = """
                MATCH (a:Accused)-[r:INVOLVED_IN]->(c:Case)
                RETURN a.name AS suspect, count(c) AS cases LIMIT 3
                """
                results = []
                with driver.session() as session:
                    for record in session.run(query):
                        results.append(f"{record['suspect']} is linked to {record['cases']} cases.")
                driver.close()
                
                if results:
                    graph_insight = "Graph Network Insight:\n" + "\n".join(results)
                    # We append this to the SQL records or evidence text so the LLM sees it.
                    current_evidence = state.get("rag_evidence_text", "")
                    state["rag_evidence_text"] = current_evidence + "\n" + graph_insight
            except Exception as e:
                logger.warning(f"Graph synthesis failed or Neo4j unavailable: {e}")
                
        return state

    async def _node_reason(self, state: WorkflowState) -> WorkflowState:
        question = state["question"]
        summary = state.get("conversation_summary", "No prior conversation context.")
        merged_evidence = state.get("merged_evidence_text", "")
        merged_citations = state.get("merged_citations", [])
        intent = state.get("intent", "unknown")

        evidence_required = self._evidence.required_citations_for_intent(intent)
        threshold_met = self._evidence.has_minimum_evidence(
            merged_citations,
            merged_evidence,
            intent,
        )
        confidence = self._evidence.confidence_level(merged_citations, intent)

        state["evidence_required"] = evidence_required
        state["threshold_met"] = threshold_met
        state["confidence"] = confidence

        if not threshold_met:
            state["answer"] = self._reasoning.insufficient_data_message()
            return state

        answer = await self._reasoning.answer(
            question=question,
            conversation_summary=summary,
            evidence_block=merged_evidence,
        )
        state["answer"] = answer
        return state
