import logging
from typing import Dict, Any

from db_neo4j.connection import graph_manager
from db_neo4j.exceptions import GraphQueryError
from analytics.network import NetworkAnalyzer
from analytics.exceptions import QueryExecutionError
from .exceptions import ProfilingError, EntityNotFoundError

logger = logging.getLogger(__name__)

class ProfileGenerator:
    """
    Generates behavioral profiles and risk assessments for individuals 
    based on their history in the Crime Knowledge Graph.
    """
    
    def __init__(self, analyzer: NetworkAnalyzer = None):
        self.analyzer = analyzer or NetworkAnalyzer()
        
    def generate_suspect_profile(self, person_id: str) -> Dict[str, Any]:
        """
        Builds a comprehensive profile for a suspect, including known associates,
        case history, and a computed risk score.
        """
        try:
            # 1. Fetch direct case history
            cypher = """
            MATCH (a:Accused {id: $person_id})-[:ACCUSED_IN]->(c:Case)
            RETURN a.id AS person_id, a.age_group AS age_group, collect(c.id) AS cases
            """
            records = graph_manager.execute_read_query(cypher, {"person_id": person_id})
            
            if not records:
                raise EntityNotFoundError(f"Accused individual {person_id} not found or has no case history.")
            
            base_data = dict(records[0])
            cases = base_data.get("cases", [])
            
            # 2. Fetch known associates
            try:
                associates = self.analyzer.get_co_accused(person_id)
            except QueryExecutionError:
                associates = []
                
            # 3. Calculate Risk Score
            risk_score = self.calculate_risk_score(len(cases), len(associates))
            
            profile = {
                "person_id": base_data.get("person_id"),
                "age_group": base_data.get("age_group"),
                "total_cases": len(cases),
                "case_history": cases,
                "known_associates_count": len(associates),
                "known_associates": [assoc["co_accused_id"] for assoc in associates],
                "risk_score": risk_score
            }
            
            return profile
            
        except EntityNotFoundError:
            raise
        except GraphQueryError as e:
            logger.error(f"Graph query failed while profiling {person_id}")
            raise ProfilingError(f"Failed to fetch profile: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error while profiling {person_id}", exc_info=True)
            raise ProfilingError(f"Unexpected error: {e}") from e

    def calculate_risk_score(self, case_count: int, associate_count: int) -> int:
        """
        Computes a heuristic risk score (0-100).
        Base score increases significantly with multiple cases, and marginally with more associates.
        """
        score = 0
        if case_count > 0:
            score += 20
        if case_count > 1:
            score += (case_count - 1) * 15
            
        score += associate_count * 5
        
        return min(score, 100)
