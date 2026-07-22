from typing import List, Dict, Any, Optional
from ..core.models import Record, SearchQuery
from ..registry.registry import ConnectorRegistry
from .hybrid import HybridSearchEngine
from ..embeddings.embeddings import EmbeddingEngine
from ..cache.cache import cache_manager
from ..utils.observability import track_performance, get_logger

logger = get_logger(__name__)

class QueryPlanner:
    """
    Orchestrates the querying process across single or multiple data sources.
    Determines if SQL, Vector, Keyword, or Hybrid search is required.
    """
    def __init__(self):
        self.hybrid_engine = HybridSearchEngine()
        self.embedding_engine = EmbeddingEngine()

    @track_performance
    async def query_source(self, connection_string: str, query: SearchQuery, **kwargs) -> List[Record]:
        """
        Executes a query against a specific source using the auto-detected connector.
        """
        cache_key = f"query:{connection_string}:{query.model_dump_json()}"
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            logger.info("Query cache hit.")
            # Convert dicts back to Records
            return [Record(**r) for r in cached_result]

        logger.info(f"Executing query on source: {connection_string}")
        
        async with ConnectorRegistry.create_connector(connection_string, **kwargs) as connector:
            results = []
            
            if query.hybrid:
                # Example: If hybrid is requested, we would theoretically trigger all three 
                # (vector, keyword, exact match) if the connector supports it, and merge.
                # Since connector implementations vary, we will simulate a call to hybrid_search.
                if query.query_text:
                    results = await connector.hybrid_search(query.query_text, limit=query.limit)
            elif query.query_text and query.include_embeddings:
                results = await connector.semantic_search(query.query_text, limit=query.limit)
            elif query.query_text:
                results = await connector.keyword_search(query.query_text, limit=query.limit)
            else:
                # Exact filtering
                results = await connector.filter(query.filters)

        # Cache the results
        await cache_manager.set(cache_key, [r.model_dump() for r in results])
        return results

    @track_performance
    async def query_multiple(self, connection_strings: List[str], query: SearchQuery, **kwargs) -> List[Record]:
        """
        Executes a query across multiple sources concurrently and merges the results.
        """
        import asyncio
        tasks = [
            self.query_source(conn_str, query, **kwargs) 
            for conn_str in connection_strings
        ]
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = []
        for i, res in enumerate(results_lists):
            if isinstance(res, Exception):
                logger.error(f"Error querying source {connection_strings[i]}: {res}")
            else:
                valid_results.append(res)
                
        # Merge results across sources using RRF
        return await self.hybrid_engine.merge_results(*valid_results, limit=query.limit) if valid_results else []
