import logging
from typing import List, Dict, Any, Optional

from qdrant_client.models import PointStruct, SearchRequest
from ml.qdrant.connection import vector_manager
from ml.qdrant.exceptions import VectorError
from ml.exceptions import RetrievalError, IndexingError

logger = logging.getLogger(__name__)

class CaseRetriever:
    """
    Handles similarity search and indexing of criminal cases within the vector database.
    Accepts raw floating-point vectors to maintain strict boundaries with the 
    upstream NLP/Embedding services.
    """
    
    def __init__(self, collection_name: str = "crime_cases"):
        self.collection_name = collection_name

    def index_case(self, case_id: str, vector: List[float], payload: Optional[Dict[str, Any]] = None) -> None:
        """
        Upserts a case's vector representation into Qdrant.
        
        Args:
            case_id: Unique identifier for the case (e.g., from the Knowledge Graph).
            vector: The dense embedding vector representing the case.
            payload: Optional metadata to store alongside the vector.
        """
        try:
            client = vector_manager.get_client()
            
            # Using point_id derived from the case_id. Qdrant requires UUID or Unsigned Int.
            # Assuming case_id might be a UUID string or integer string. We'll let Qdrant handle validation,
            # or we could hash it. For simplicity, we assume case_id is a valid UUID string or int.
            point = PointStruct(
                id=case_id,
                vector=vector,
                payload=payload or {}
            )
            
            client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            logger.info(f"Successfully indexed case {case_id} into {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to index case {case_id} into {self.collection_name}", exc_info=True)
            raise IndexingError(f"Vector indexing failed: {e}") from e

    def search_similar_cases(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Searches for cases with similar vectors (e.g., Modus Operandi).
        
        Args:
            query_vector: The dense embedding vector to search with.
            limit: Maximum number of results to return.
            
        Returns:
            A list of dictionaries containing the case_id, similarity score, and metadata payload.
        """
        try:
            client = vector_manager.get_client()
            
            search_result = client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
            
            results = []
            for hit in search_result:
                results.append({
                    "case_id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload
                })
                
            return results
            
        except Exception as e:
            logger.error(f"Failed to search similar cases in {self.collection_name}", exc_info=True)
            raise RetrievalError(f"Vector search failed: {e}") from e
