class ProfilingError(Exception):
    """Base exception for all profiling operations."""
    pass

class EntityNotFoundError(ProfilingError):
    """Raised when the target entity (e.g., Accused person) cannot be found in the database."""
    pass
