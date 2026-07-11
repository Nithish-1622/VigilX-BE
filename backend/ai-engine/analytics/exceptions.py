class AnalysisError(Exception):
    """Base exception for analytics operations."""
    pass

class QueryExecutionError(AnalysisError):
    """Raised when an analytical Cypher query fails execution."""
    pass
