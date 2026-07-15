class ForecastingError(Exception):
    """Base exception for forecasting and predictive operations."""
    pass

class InsufficientDataError(ForecastingError):
    """Raised when there is not enough historical data to generate a reliable forecast."""
    pass
