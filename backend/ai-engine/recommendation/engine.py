import logging
from typing import Dict, Any, List

from neo4j.connection import graph_manager
from neo4j.exceptions import GraphQueryError
from .exceptions import RecommendationError, InvalidCaseError

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """
    Generates investigative leads and proactive intelligence by traversing 
    2nd-degree connections in the Crime Knowledge Graph.
    """
    
    def recommend_suspects(self, case_id: str) -> List[Dict[str, Any]]:
        """
        Finds individuals who are closely associated with persons already accused 
        in a given case, but who have not yet been booked for this case.
        
        Args:
            case_id: The target Case ID to find leads for.
            
        Returns:
            A list of recommended suspects ranked by the strength of their association.
        """
        # First verify the case exists
        check_cypher = "MATCH (c:Case {id: $case_id}) RETURN c.id AS id"
        try:
            case_check = graph_manager.execute_read_query(check_cypher, {"case_id": case_id})
            if not case_check:
                raise InvalidCaseError(f"Case {case_id} not found in the graph.")
        except GraphQueryError as e:
            raise RecommendationError(f"Failed to validate case: {e}") from e

        # Query to find 2nd degree associates who are NOT already accused in THIS case
        cypher = """
        MATCH (target_case:Case {id: $case_id})<-[:ACCUSED_IN]-(known_accused:Accused)
        MATCH (known_accused)-[:ACCUSED_IN]->(historical_case:Case)<-[:ACCUSED_IN]-(associate:Accused)
        WHERE NOT (associate)-[:ACCUSED_IN]->(target_case)
        WITH associate, count(historical_case) AS connection_strength, collect(historical_case.id) AS shared_history
        RETURN associate.id AS recommended_suspect_id, 
               associate.age_group AS age_group,
               connection_strength,
               shared_history
        ORDER BY connection_strength DESC
        """
        
        try:
            records = graph_manager.execute_read_query(cypher, {"case_id": case_id})
            return [dict(record) for record in records]
        except GraphQueryError as e:
            logger.error(f"Failed to generate suspect recommendations for {case_id}")
            raise RecommendationError(f"Recommendation generation failed: {e}") from e
