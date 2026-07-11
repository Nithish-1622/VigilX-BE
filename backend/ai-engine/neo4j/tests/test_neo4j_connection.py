import pytest
from unittest.mock import patch, MagicMock

from neo4j.exceptions import GraphConfigurationError, GraphConnectionError
from neo4j.connection import Neo4jConnectionManager
from neo4j.health import check_neo4j_health

# A valid mock settings object
class MockSettings:
    neo4j_uri = "bolt://localhost:7687"
    neo4j_username = "neo4j"
    neo4j_password = "password"
    neo4j_database = "neo4j"

@pytest.fixture
def manager():
    return Neo4jConnectionManager()

@patch('neo4j.connection.get_settings')
@patch('neo4j.connection.GraphDatabase.driver')
def test_manager_initialization_success(mock_driver, mock_get_settings, manager):
    """Test successful initialization of the connection manager."""
    mock_get_settings.return_value = MockSettings()
    
    # Mock the driver instance and its methods
    mock_driver_instance = MagicMock()
    mock_driver.return_value = mock_driver_instance
    
    manager.initialize()
    
    mock_get_settings.assert_called_once()
    mock_driver.assert_called_once_with(
        "bolt://localhost:7687", 
        auth=("neo4j", "password")
    )
    mock_driver_instance.verify_connectivity.assert_called_once()
    assert manager._driver is not None

@patch('neo4j.connection.get_settings')
def test_manager_initialization_missing_config(mock_get_settings, manager):
    """Test initialization fails when config is invalid."""
    # Simulate the validation error raised by get_settings
    mock_get_settings.side_effect = GraphConfigurationError("Invalid config")
    
    with pytest.raises(GraphConfigurationError):
        manager.initialize()

@patch('neo4j.health.graph_manager')
def test_health_check_healthy(mock_graph_manager):
    """Test health check when database is responsive."""
    mock_graph_manager.execute_read_query.return_value = [{"health_check": 1}]
    
    status = check_neo4j_health()
    
    assert status["status"] == "healthy"
    assert status["details"] == "Database is responsive."

@patch('neo4j.health.graph_manager')
def test_health_check_unhealthy(mock_graph_manager):
    """Test health check when database query fails."""
    mock_graph_manager.execute_read_query.side_effect = GraphConnectionError("Connection lost")
    
    status = check_neo4j_health()
    
    assert status["status"] == "unhealthy"
    assert "Connection lost" in status["details"]
