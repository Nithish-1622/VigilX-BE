from __future__ import annotations

from dataclasses import dataclass

from schemas.common import Citation
from schemas.rest import RestCapability, StructuredQuery
from services.evidence_service import EvidenceService
from services.rest_gateway import DjangoRestGateway
from utils.config import settings

_embedding_model = None

@dataclass
class RetrievedContext:
    evidence_text: str
    citations: list[Citation]


class RAGRetriever:
    def __init__(self, rest_gateway: DjangoRestGateway) -> None:
        self._rest_gateway = rest_gateway
        self._evidence = EvidenceService()

    async def retrieve(
        self,
        question: str,
        intent: str,
        auth_header: str | None = None,
        context_headers: dict[str, str] | None = None,
    ) -> RetrievedContext:
        query = StructuredQuery(
            capability=self._capability_for_intent(intent),
            intent=intent,
            question=question,
            query_text=question,
            context={"mode": "rag"},
        )
        import asyncio
        response = await asyncio.to_thread(
            self._rest_gateway.invoke,
            query,
            auth_header,
            context_headers,
        )

        items = []
        if response.success and isinstance(response.payload, dict):
            raw_items = response.payload.get("results", response.payload.get("items", []))
            if isinstance(raw_items, list):
                items = [item for item in raw_items if isinstance(item, dict)]
                
        # Qdrant Hybrid Search Integration
        try:
            from qdrant_client import QdrantClient
            from fastembed import TextEmbedding
            import os
            
            qdrant_url = os.environ.get("QDRANT_HOST")
            qdrant_api_key = os.environ.get("QDRANT_API_KEY")
            
            if qdrant_url and qdrant_api_key:
                if os.getenv("X_ZOHO_CATALYST_LISTEN_PORT"):
                    raise Exception("Skipping fastembed on Catalyst AppSail to prevent OOM crash")
                    
                def run_qdrant_search():
                    global _embedding_model
                    if _embedding_model is None:
                        _embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
                    
                    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
                    embeddings = list(_embedding_model.embed([question]))
                    return client.search(
                        collection_name="crime_cases",
                        query_vector=embeddings[0].tolist(),
                        limit=3
                    )
                
                search_result = await asyncio.to_thread(run_qdrant_search)
                for point in search_result:
                    items.append({
                        "source": "qdrant_vector_search",
                        "id": point.id,
                        "score": point.score,
                        "content": point.payload.get("brief_facts", "") or point.payload.get("text", "")
                    })
        except Exception as e:
            # Fallback gracefully if Qdrant is unavailable or not configured
            pass

        items = items[: settings.max_context_items]

        citations: list[Citation] = []
        evidence_chunks: list[str] = []

        for item in items:
            snippet = self._evidence.format_row(item)
            source = str(item.get("source", query.capability.value))
            ref_id = item.get("id")
            score = item.get("score")
            if snippet.strip():
                evidence_chunks.append(f"[{source}] {snippet}")
                citations.append(
                    Citation(
                        source=source,
                        reference_id=str(ref_id) if ref_id is not None else None,
                        snippet=snippet,
                        score=float(score) if isinstance(score, (int, float)) else None,
                    )
                )

        return RetrievedContext(
            evidence_text="\n".join(evidence_chunks),
            citations=citations,
        )

    def _capability_for_intent(self, intent: str) -> RestCapability:
        if intent == "case_lookup":
            return RestCapability.CASE_SEARCH
        if intent == "suspect_query":
            return RestCapability.CASE_SEARCH
        if intent == "victim_query":
            return RestCapability.CASE_SEARCH
        if intent == "timeline_query":
            return RestCapability.CASE_SUMMARY
        if intent == "evidence_summary":
            return RestCapability.CASE_SUMMARY
        if intent == "statistics_query":
            return RestCapability.INVESTIGATION_STATUS
        return RestCapability.CRIME_RECORDS
