import httpx
from typing import List, Dict, Any, Optional
try:
    from qdrant_client import AsyncQdrantClient
    from qdrant_client.http.models import PointStruct, VectorParams, Distance
except ImportError:
    AsyncQdrantClient = None
    PointStruct = VectorParams = Distance = None
from ..config.config import settings
from ..utils.observability import track_performance, get_logger

logger = get_logger(__name__)

class EmbeddingEngine:
    """
    Manages embeddings generation (Ollama) and vector storage (Qdrant).
    """
    def __init__(self):
        self.ollama_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_EMBEDDING_MODEL
        
        # We wrap Qdrant in try-except in case the library isn't installed in the env yet
        try:
            if AsyncQdrantClient is None:
                raise ImportError("qdrant_client not installed")
            self.qdrant = AsyncQdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
            self._qdrant_initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {e}")
            self._qdrant_initialized = False

    @track_performance
    async def embed_text(self, text: str) -> List[float]:
        """Generate embeddings using Ollama."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={"model": self.model, "prompt": text},
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("embedding", [])
            except Exception as e:
                logger.error(f"Error generating embeddings from Ollama: {e}")
                return []

    @track_performance
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        # Ollama currently processes one by one, but future versions might support batching.
        # We'll run them sequentially or via asyncio.gather.
        # For large batches, consider a bounded semaphore.
        import asyncio
        tasks = [self.embed_text(text) for text in texts]
        return await asyncio.gather(*tasks)

    @track_performance
    async def store_vectors(self, collection_name: str, vectors: List[List[float]], payloads: List[Dict[str, Any]], ids: List[str]):
        """Store vectors and their metadata payloads in Qdrant."""
        if not self._qdrant_initialized:
            logger.warning("Qdrant not initialized. Skipping vector storage.")
            return

        # Ensure collection exists
        try:
            exists = await self.qdrant.collection_exists(collection_name)
            if not exists:
                # Assuming nomic-embed-text generates 768 or 384 dim, needs config or dynamic check.
                # Nomic typically uses 768.
                dim = len(vectors[0]) if vectors else 768
                await self.qdrant.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
                )
        except Exception as e:
            logger.error(f"Error checking/creating Qdrant collection: {e}")
            return

        points = [
            PointStruct(id=vid, vector=vec, payload=payload)
            for vid, vec, payload in zip(ids, vectors, payloads)
        ]
        
        try:
            await self.qdrant.upsert(collection_name=collection_name, points=points)
        except Exception as e:
            logger.error(f"Error upserting vectors to Qdrant: {e}")

    @track_performance
    async def search_vectors(self, collection_name: str, query_vector: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """Search Qdrant for similar vectors."""
        if not self._qdrant_initialized:
            return []

        try:
            results = await self.qdrant.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit
            )
            return [{"id": hit.id, "score": hit.score, "payload": hit.payload} for hit in results]
        except Exception as e:
            logger.error(f"Error searching Qdrant: {e}")
            return []
