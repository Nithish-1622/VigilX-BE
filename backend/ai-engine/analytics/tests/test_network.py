import pytest
from unittest.mock import patch, MagicMock

from analytics.network import NetworkAnalyzer
from analytics.exceptions import QueryExecutionError

@pytest.fixture
def analyzer():
    return NetworkAnalyzer()

@patch('analytics.network.graph_manager')
def test_get_co_accused_success(mock_graph_manager, analyzer):
    # Mocking read query result
    mock_graph_manager.execute_read_query.return_value = [
        {"co_accused_id": "ACC_2", "age_group": "30", "shared_cases": ["CASE_1", "CASE_2"], "shared_case_count": 2}
    ]
    
    result = analyzer.get_co_accused("ACC_1")
    
    assert len(result) == 1
    assert result[0]["co_accused_id"] == "ACC_2"
    assert result[0]["shared_case_count"] == 2
    
    args, _ = mock_graph_manager.execute_read_query.call_args
    assert "MATCH (target:Accused {id: $person_id})" in args[0]
    assert args[1]["person_id"] == "ACC_1"

@patch('analytics.network.graph_manager')
def test_find_syndicates_success(mock_graph_manager, analyzer):
    mock_graph_manager.execute_read_query.return_value = [
        {"accused_1": "ACC_1", "accused_2": "ACC_2", "shared_cases": ["CASE_1", "CASE_2", "CASE_3"], "shared_case_count": 3}
    ]
    
    result = analyzer.find_syndicates(min_shared_cases=3)
    
    assert len(result) == 1
    assert result[0]["accused_1"] == "ACC_1"
    assert result[0]["shared_case_count"] == 3
    
    args, _ = mock_graph_manager.execute_read_query.call_args
    assert "WHERE shared_case_count >= $min_shared_cases" in args[0]
    assert args[1]["min_shared_cases"] == 3

@patch('analytics.network.graph_manager')
def test_query_execution_error(mock_graph_manager, analyzer):
    # Simulating a neo4j query failure
    from neo4j.exceptions import GraphQueryError
    mock_graph_manager.execute_read_query.side_effect = GraphQueryError("Syntax Error")
    
    with pytest.raises(QueryExecutionError):
        analyzer.get_co_accused("ACC_1")
