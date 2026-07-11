class RecommendationError(Exception):
    """Base exception for recommendation operations."""
    pass

class InvalidCaseError(RecommendationError):
    """Raised when the provided case ID is invalid or not found."""
    pass
