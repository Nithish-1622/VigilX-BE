class VectorError(Exception):
    """Base exception for all vector database operations."""
    pass

class VectorConnectionError(VectorError):
    """Raised when unable to establish or maintain a connection to Qdrant."""
    pass

class VectorQueryError(VectorError):
    """Raised when a vector search or ingestion query fails."""
    pass

class VectorConfigurationError(VectorError):
    """Raised when vector database configuration is missing or invalid."""
    pass
