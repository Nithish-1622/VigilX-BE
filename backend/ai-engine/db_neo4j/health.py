import logging
from typing import Dict, Any

from .connection import graph_manager
from .exceptions import GraphError

logger = logging.getLogger(__name__)

def check_neo4j_health() -> Dict[str, Any]:
    """
    Executes a basic health check query against the Neo4j database.
    
    Returns:
        A dictionary containing the status and optional details.
    """
    status = {
        "service": "neo4j",
        "status": "unhealthy",
        "details": None
    }
    
    try:
        # A simple query that should always return 1 if the db is responsive
        result = graph_manager.execute_read_query("RETURN 1 AS health_check")
        if result and result[0].get("health_check") == 1:
            status["status"] = "healthy"
            status["details"] = "Database is responsive."
        else:
            status["details"] = "Database connected but returned unexpected result."
            logger.warning("Neo4j health check returned unexpected result.")
            
    except GraphError as e:
        status["details"] = str(e)
        logger.error("Neo4j health check failed due to a graph error.")
    except Exception as e:
        status["details"] = "An unexpected error occurred during health check."
        logger.error("Neo4j health check failed unexpectedly.", exc_info=True)
        
    return status
