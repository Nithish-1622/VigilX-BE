import pytest
from unittest.mock import patch, MagicMock

from recommendation.engine import RecommendationEngine
from recommendation.exceptions import InvalidCaseError, RecommendationError

@pytest.fixture
def engine():
    return RecommendationEngine()

@patch('recommendation.engine.graph_manager')
def test_recommend_suspects_success(mock_graph_manager, engine):
    # Mock sequence: 1st call for validation, 2nd call for recommendations
    mock_graph_manager.execute_read_query.side_effect = [
        [{"id": "CASE_1"}],  # Case validation returns true
        [{"recommended_suspect_id": "ACC_3", "age_group": "25-30", "connection_strength": 2, "shared_history": ["CASE_HIST1"]}]
    ]
    
    results = engine.recommend_suspects("CASE_1")
    
    assert len(results) == 1
    assert results[0]["recommended_suspect_id"] == "ACC_3"
    assert results[0]["connection_strength"] == 2

@patch('recommendation.engine.graph_manager')
def test_recommend_suspects_invalid_case(mock_graph_manager, engine):
    # Case validation returns empty
    mock_graph_manager.execute_read_query.return_value = []
    
    with pytest.raises(InvalidCaseError):
        engine.recommend_suspects("INVALID_CASE")

@patch('recommendation.engine.graph_manager')
def test_recommend_suspects_db_error(mock_graph_manager, engine):
    from neo4j.exceptions import GraphQueryError
    mock_graph_manager.execute_read_query.side_effect = GraphQueryError("Syntax error")
    
    with pytest.raises(RecommendationError):
        engine.recommend_suspects("CASE_1")
