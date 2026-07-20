import os
from pydantic_settings import BaseSettings

class AdapterSettings(BaseSettings):
    """
    Configuration settings for the Universal Database Adapter.
    Pulls from environment variables automatically.
    """
    # Caching Layer
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_DEFAULT_TTL: int = int(os.getenv("CACHE_DEFAULT_TTL", "3600"))
    USE_IN_MEMORY_FALLBACK: bool = os.getenv("USE_IN_MEMORY_FALLBACK", "True").lower() in ("true", "1", "yes")

    # Embeddings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_EMBEDDING_MODEL: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

    # Vector Store (Qdrant)
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")

    # Application
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "True").lower() in ("true", "1", "yes")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = AdapterSettings()
