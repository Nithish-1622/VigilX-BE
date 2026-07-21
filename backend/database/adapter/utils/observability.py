import logging
import time
from functools import wraps
from typing import Callable, Any
from ..config.config import settings

# Setup standard structured logging (can be swapped with structlog for JSON logging in production)
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_logger(name: str) -> logging.Logger:
    """Get a structured logger for the given module."""
    return logging.getLogger(name)

logger = get_logger(__name__)

def track_performance(func: Callable) -> Callable:
    """Decorator to track async execution time and report metrics."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not settings.ENABLE_METRICS:
            return await func(*args, **kwargs)

        start_time = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            duration = time.perf_counter() - start_time
            logger.debug(f"METRIC: {func.__name__} executed in {duration:.4f}s")
            # In a full production setup, this would emit to Prometheus/Datadog
            return result
        except Exception as e:
            duration = time.perf_counter() - start_time
            logger.error(f"METRIC: {func.__name__} failed after {duration:.4f}s with error: {str(e)}")
            raise
    return wrapper
