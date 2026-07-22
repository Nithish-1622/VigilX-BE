from typing import List, Dict, Any
from ..core.models import Record
from ..utils.observability import track_performance, get_logger

logger = get_logger(__name__)

class HybridSearchEngine:
    """
    Merges results from Vector, Keyword, and SQL/Metadata searches into a single ranked list.
    """
    
    @staticmethod
    def _reciprocal_rank_fusion(results_lists: List[List[Record]], k: int = 60) -> List[Record]:
        """
        Implements Reciprocal Rank Fusion (RRF) to merge and rank results.
        """
        score_map = {}
        record_map = {}
        
        for results in results_lists:
            for rank, record in enumerate(results):
                record_id = record.id
                if not record_id:
                    continue
                    
                if record_id not in score_map:
                    score_map[record_id] = 0.0
                    record_map[record_id] = record
                    
                score_map[record_id] += 1.0 / (k + rank + 1)
                
        # Sort by RRF score descending
        sorted_ids = sorted(score_map.keys(), key=lambda x: score_map[x], reverse=True)
        
        # Assign the final RRF score to the record
        final_results = []
        for rid in sorted_ids:
            rec = record_map[rid]
            rec.score = score_map[rid]
            final_results.append(rec)
            
        return final_results

    @track_performance
    async def merge_results(self, vector_results: List[Record], keyword_results: List[Record], sql_results: List[Record], limit: int = 10) -> List[Record]:
        """
        Merge results from different search methodologies.
        """
        results_lists = [
            res for res in [vector_results, keyword_results, sql_results] if res
        ]
        
        if not results_lists:
            return []
            
        merged = self._reciprocal_rank_fusion(results_lists)
        return merged[:limit]
