from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class QdrantSettings(BaseSettings):
    """
    Configuration settings for Qdrant connection.
    Values are loaded from environment variables (e.g. QDRANT_URI).
    """
    qdrant_uri: str
    qdrant_api_key: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

def get_settings() -> QdrantSettings:
    """Retrieves the Qdrant settings from the environment."""
    from .exceptions import VectorConfigurationError
    from pydantic import ValidationError
    try:
        return QdrantSettings()
    except ValidationError as e:
        raise VectorConfigurationError(f"Invalid or missing Qdrant configuration: {e}") from e
