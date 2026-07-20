import logging
from typing import List, Dict, Any

from db_neo4j.connection import graph_manager
from db_neo4j.exceptions import GraphQueryError
from .exceptions import QueryExecutionError

logger = logging.getLogger(__name__)

class NetworkAnalyzer:
    """
    Provides analytical queries against the Crime Knowledge Graph
    to uncover criminal networks and syndicates.
    """

    def get_co_accused(self, person_id: str) -> List[Dict[str, Any]]:
        """
        Finds all other Accused individuals who have participated in the same cases
        as the target individual.
        
        Args:
            person_id: The ID of the target Accused.
            
        Returns:
            A list of dictionaries representing co-accused profiles and the shared cases.
        """
        cypher = """
        MATCH (target:Accused {id: $person_id})-[:ACCUSED_IN]->(c:Case)<-[:ACCUSED_IN]-(co_accused:Accused)
        RETURN co_accused.id AS co_accused_id, 
               co_accused.age_group AS age_group,
               collect(c.id) AS shared_cases,
               count(c) AS shared_case_count
        ORDER BY shared_case_count DESC
        """
        
        try:
            records = graph_manager.execute_read_query(cypher, {"person_id": person_id})
            return [dict(record) for record in records]
        except GraphQueryError as e:
            logger.error(f"Failed to fetch co-accused for {person_id}")
            raise QueryExecutionError(f"Cypher execution failed: {e}") from e

    def find_syndicates(self, min_shared_cases: int = 2) -> List[Dict[str, Any]]:
        """
        Identifies pairs of Accused who repeatedly appear together across multiple FIRs,
        flagging them as potential organized syndicates.
        
        Args:
            min_shared_cases: Minimum number of shared cases to be considered a syndicate pair.
            
        Returns:
            A list of dictionaries representing the syndicate pairs.
        """
        # Ensure we only count each pair once by ordering their IDs
        cypher = """
        MATCH (a1:Accused)-[:ACCUSED_IN]->(c:Case)<-[:ACCUSED_IN]-(a2:Accused)
        WHERE id(a1) < id(a2)
        WITH a1, a2, collect(c.id) AS shared_cases, count(c) AS shared_case_count
        WHERE shared_case_count >= $min_shared_cases
        RETURN a1.id AS accused_1, 
               a2.id AS accused_2, 
               shared_cases, 
               shared_case_count
        ORDER BY shared_case_count DESC
        """
        
        try:
            records = graph_manager.execute_read_query(cypher, {"min_shared_cases": min_shared_cases})
            return [dict(record) for record in records]
        except GraphQueryError as e:
            logger.error("Failed to fetch criminal syndicates.")
            raise QueryExecutionError(f"Cypher execution failed: {e}") from e
