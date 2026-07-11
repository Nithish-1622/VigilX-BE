from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Neo4jSettings(BaseSettings):
    """
    Configuration settings for Neo4j Community Edition connection.
    Values are loaded from environment variables (e.g. NEO4J_URI).
    """
    neo4j_uri: str
    neo4j_username: str = "neo4j"
    neo4j_password: str
    neo4j_database: str = "neo4j"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

def get_settings() -> Neo4jSettings:
    """Retrieves the Neo4j settings from the environment."""
    from .exceptions import GraphConfigurationError
    from pydantic import ValidationError
    try:
        return Neo4jSettings()
    except ValidationError as e:
        raise GraphConfigurationError(f"Invalid or missing Neo4j configuration: {e}") from e
