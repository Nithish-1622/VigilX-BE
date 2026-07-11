class GraphBuilderError(Exception):
    """Base exception for graph builder operations."""
    pass

class SchemaValidationError(GraphBuilderError):
    """Raised when provided node or relationship fails schema-level expectations before query generation."""
    pass

class QueryExecutionError(GraphBuilderError):
    """Raised when a generated Cypher query fails execution."""
    pass
