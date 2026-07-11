import logging
from typing import Dict, Any

from .connection import vector_manager
from .exceptions import VectorError

logger = logging.getLogger(__name__)

def check_qdrant_health() -> Dict[str, Any]:
    """
    Executes a basic health check against the Qdrant database.
    
    Returns:
        A dictionary containing the status and optional details.
    """
    status = {
        "service": "qdrant",
        "status": "unhealthy",
        "details": None
    }
    
    try:
        # Check by fetching collections. Will throw an exception if connection fails.
        client = vector_manager.get_client()
        collections = client.get_collections()
        status["status"] = "healthy"
        status["details"] = f"Database is responsive. {len(collections.collections)} collections found."
            
    except VectorError as e:
        status["details"] = str(e)
        logger.error("Qdrant health check failed due to a vector error.")
    except Exception as e:
        status["details"] = "An unexpected error occurred during health check."
        logger.error("Qdrant health check failed unexpectedly.", exc_info=True)
        
    return status
