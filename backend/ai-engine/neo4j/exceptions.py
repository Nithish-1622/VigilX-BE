class GraphError(Exception):
    """Base exception for all Neo4j graph operations."""
    pass

class GraphConnectionError(GraphError):
    """Raised when unable to establish or maintain a connection to Neo4j."""
    pass

class GraphQueryError(GraphError):
    """Raised when a Cypher query fails to execute."""
    pass

class GraphConfigurationError(GraphError):
    """Raised when Neo4j configuration is missing or invalid."""
    pass
