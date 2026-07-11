class MLError(Exception):
    """Base exception for all machine learning and predictive intelligence operations."""
    pass

class RetrievalError(MLError):
    """Raised when a vector search or retrieval operation fails."""
    pass

class IndexingError(MLError):
    """Raised when indexing a vector representation into the database fails."""
    pass
