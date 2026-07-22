from typing import Dict, Type, Any
from ..core.base import BaseConnector
from ..core.exceptions import InvalidSourceError
from .detector import SourceDetector
from ..utils.observability import get_logger

logger = get_logger(__name__)

class ConnectorRegistry:
    """
    Dynamic registry for all data connectors.
    Follows the Plugin architecture.
    """
    _registry: Dict[str, Type[BaseConnector]] = {}

    @classmethod
    def register(cls, source_type: str):
        """Decorator to register a connector class."""
        def wrapper(connector_class: Type[BaseConnector]):
            if not issubclass(connector_class, BaseConnector):
                raise TypeError(f"{connector_class.__name__} must inherit from BaseConnector.")
            cls._registry[source_type.lower()] = connector_class
            logger.info(f"Registered connector plugin: {source_type.lower()}")
            return connector_class
        return wrapper

    @classmethod
    def get_connector_class(cls, source_type: str) -> Type[BaseConnector]:
        """Retrieve a connector class by source type."""
        source_type = source_type.lower()
        if source_type not in cls._registry:
            raise InvalidSourceError(f"No connector registered for source type: {source_type}")
        return cls._registry[source_type]

    @classmethod
    def create_connector(cls, connection_string: str, **kwargs) -> BaseConnector:
        """
        Auto-detect the source type and instantiate the appropriate connector.
        """
        source_type = SourceDetector.detect_source_type(connection_string)
        connector_class = cls.get_connector_class(source_type)
        return connector_class(connection_string=connection_string, **kwargs)

    @classmethod
    def list_connectors(cls) -> Dict[str, Type[BaseConnector]]:
        """List all registered connectors."""
        return cls._registry.copy()
