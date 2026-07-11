class ExplainabilityError(Exception):
    """Base exception for explainability operations."""
    pass

class InvalidProfileError(ExplainabilityError):
    """Raised when the provided profile format is invalid or missing required fields."""
    pass
