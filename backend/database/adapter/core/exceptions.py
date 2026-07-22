class AdapterException(Exception):
    """Base exception for all Universal Database Adapter errors."""
    pass

class ConnectionError(AdapterException):
    """Raised when a connector fails to establish a connection."""
    pass

class QueryExecutionError(AdapterException):
    """Raised when a query fails to execute."""
    pass

class SchemaDiscoveryError(AdapterException):
    """Raised when schema discovery fails."""
    pass

class InvalidSourceError(AdapterException):
    """Raised when an invalid source or connection string is provided."""
    pass

class AuthenticationError(AdapterException):
    """Raised when authentication to the source fails."""
    pass

class ResourceNotFoundError(AdapterException):
    """Raised when the requested resource (e.g., table, collection, file) is not found."""
    pass

class ParsingError(AdapterException):
    """Raised when unstructured or semi-structured data cannot be parsed."""
    pass
