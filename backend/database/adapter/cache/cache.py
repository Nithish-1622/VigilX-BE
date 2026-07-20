import json
from typing import Any, Optional
try:
    from cachetools import LRUCache
except ImportError:
    LRUCache = None

try:
    import redis.asyncio as redis
except ImportError:
    redis = None
from ..config.config import settings
from ..utils.observability import get_logger, track_performance

logger = get_logger(__name__)

class CacheManager:
    """
    Manages caching for the Universal Database Adapter.
    Uses Redis as the primary layer, with an LRU cache fallback.
    """
    def __init__(self):
        self.redis_client = None
        if settings.REDIS_URL and not settings.USE_IN_MEMORY_FALLBACK:
            try:
                self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
                logger.info("Initialized Redis cache layer.")
            except Exception as e:
                logger.error(f"Failed to initialize Redis: {e}")
                self._init_fallback()
        else:
            self._init_fallback()

    def _init_fallback(self):
        logger.info("Using in-memory LRU fallback cache.")
        if LRUCache:
            self.lru_cache = LRUCache(maxsize=10000)
        else:
            logger.warning("cachetools not installed. Using simple dict fallback.")
            self.lru_cache = {}

    @track_performance
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the cache."""
        try:
            if self.redis_client:
                val = await self.redis_client.get(key)
                return json.loads(val) if val else None
            else:
                return self.lru_cache.get(key)
        except Exception as e:
            logger.warning(f"Cache get error for {key}: {e}")
            return None

    @track_performance
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set a value in the cache with an optional TTL."""
        ttl = ttl or settings.CACHE_DEFAULT_TTL
        try:
            if self.redis_client:
                await self.redis_client.setex(key, ttl, json.dumps(value))
                return True
            else:
                self.lru_cache[key] = value
                # Note: cachetools LRU doesn't support TTL natively, 
                # a TTLCache could be used instead, but LRU + maxsize suffices for the fallback.
                return True
        except Exception as e:
            logger.warning(f"Cache set error for {key}: {e}")
            return False

    async def invalidate(self, key: str) -> bool:
        """Remove a key from the cache."""
        try:
            if self.redis_client:
                await self.redis_client.delete(key)
                return True
            else:
                self.lru_cache.pop(key, None)
                return True
        except Exception as e:
            logger.warning(f"Cache invalidate error for {key}: {e}")
            return False

    async def close(self):
        if self.redis_client:
            await self.redis_client.close()

# Singleton cache manager instance
cache_manager = CacheManager()
