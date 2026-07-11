import pytest
from unittest.mock import patch, MagicMock

from ml.qdrant.exceptions import VectorConfigurationError, VectorConnectionError
from ml.qdrant.connection import QdrantConnectionManager
from ml.qdrant.health import check_qdrant_health

# A valid mock settings object
class MockSettings:
    qdrant_uri = "http://localhost:6333"
    qdrant_api_key = "secret"

@pytest.fixture
def manager():
    return QdrantConnectionManager()

@patch('ml.qdrant.connection.get_settings')
@patch('ml.qdrant.connection.QdrantClient')
def test_manager_initialization_success(mock_qdrant_client, mock_get_settings, manager):
    """Test successful initialization of the Qdrant connection manager."""
    mock_get_settings.return_value = MockSettings()
    
    mock_client_instance = MagicMock()
    mock_qdrant_client.return_value = mock_client_instance
    
    manager.initialize()
    
    mock_get_settings.assert_called_once()
    mock_qdrant_client.assert_called_once_with(
        url="http://localhost:6333",
        api_key="secret"
    )
    mock_client_instance.get_collections.assert_called_once()
    assert manager._client is not None

@patch('ml.qdrant.connection.get_settings')
def test_manager_initialization_missing_config(mock_get_settings, manager):
    """Test initialization fails when config is invalid."""
    mock_get_settings.side_effect = VectorConfigurationError("Invalid config")
    
    with pytest.raises(VectorConfigurationError):
        manager.initialize()

@patch('ml.qdrant.health.vector_manager')
def test_health_check_healthy(mock_vector_manager):
    """Test health check when database is responsive."""
    mock_client = MagicMock()
    mock_collections = MagicMock()
    mock_collections.collections = ["collection1", "collection2"]
    mock_client.get_collections.return_value = mock_collections
    
    mock_vector_manager.get_client.return_value = mock_client
    
    status = check_qdrant_health()
    
    assert status["status"] == "healthy"
    assert "2 collections found" in status["details"]

@patch('ml.qdrant.health.vector_manager')
def test_health_check_unhealthy(mock_vector_manager):
    """Test health check when database query fails."""
    mock_client = MagicMock()
    mock_client.get_collections.side_effect = Exception("Connection lost")
    mock_vector_manager.get_client.return_value = mock_client
    
    status = check_qdrant_health()
    
    assert status["status"] == "unhealthy"
    assert "An unexpected error occurred" in status["details"]
