import logging
from typing import Optional
from qdrant_client import QdrantClient

from .config import get_settings, QdrantSettings
from .exceptions import VectorConnectionError

logger = logging.getLogger(__name__)

class QdrantConnectionManager:
    """
    Manages the lifecycle of the Qdrant client connection.
    """
    
    def __init__(self):
        self._client: Optional[QdrantClient] = None
        self._settings: Optional[QdrantSettings] = None
        
    def initialize(self) -> None:
        """Initializes the Qdrant client using configuration from environment."""
        if self._client is not None:
            return  # Already initialized
            
        self._settings = get_settings()
        
        try:
            # We assume qdrant_uri could be a url or host/port depending on format
            # Using standard url parsing for simplicity
            self._client = QdrantClient(
                url=self._settings.qdrant_uri,
                api_key=self._settings.qdrant_api_key
            )
            # Verify connectivity by checking collections
            self._client.get_collections()
            logger.info(f"Successfully connected to Qdrant at {self._settings.qdrant_uri}")
        except Exception as e:
            logger.error("Failed to connect to Qdrant.")
            raise VectorConnectionError("Could not connect to Qdrant service.") from e

    def get_client(self) -> QdrantClient:
        """
        Returns the initialized Qdrant client instance.
        """
        if self._client is None:
            self.initialize()
        # QdrantClient is not subscriptable/optional in this block since we just initialized it
        return self._client # type: ignore

    def close(self) -> None:
        """Closes the Qdrant client connection."""
        if self._client is not None:
            self._client.close()
            self._client = None
            logger.info("Qdrant connection closed safely.")

# Global instance for use across the application
vector_manager = QdrantConnectionManager()
