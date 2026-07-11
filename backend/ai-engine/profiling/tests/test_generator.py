import pytest
from unittest.mock import patch, MagicMock

from profiling.generator import ProfileGenerator
from profiling.exceptions import EntityNotFoundError, ProfilingError

@pytest.fixture
def generator():
    mock_analyzer = MagicMock()
    return ProfileGenerator(analyzer=mock_analyzer)

@patch('profiling.generator.graph_manager')
def test_generate_suspect_profile_success(mock_graph_manager, generator):
    mock_graph_manager.execute_read_query.return_value = [
        {"person_id": "ACC_1", "age_group": "25-30", "cases": ["CASE_1", "CASE_2"]}
    ]
    
    # Mock known associates
    generator.analyzer.get_co_accused.return_value = [
        {"co_accused_id": "ACC_2", "shared_case_count": 2},
        {"co_accused_id": "ACC_3", "shared_case_count": 1}
    ]
    
    profile = generator.generate_suspect_profile("ACC_1")
    
    assert profile["person_id"] == "ACC_1"
    assert profile["total_cases"] == 2
    assert profile["known_associates_count"] == 2
    assert "ACC_2" in profile["known_associates"]
    
    # Risk score logic: 2 cases -> 20 + 15 = 35. 2 associates -> 10. Total 45.
    assert profile["risk_score"] == 45

@patch('profiling.generator.graph_manager')
def test_generate_suspect_profile_not_found(mock_graph_manager, generator):
    mock_graph_manager.execute_read_query.return_value = []
    
    with pytest.raises(EntityNotFoundError):
        generator.generate_suspect_profile("NON_EXISTENT")

def test_calculate_risk_score(generator):
    assert generator.calculate_risk_score(0, 0) == 0
    assert generator.calculate_risk_score(1, 0) == 20
    assert generator.calculate_risk_score(2, 0) == 35
    assert generator.calculate_risk_score(2, 2) == 45
    assert generator.calculate_risk_score(10, 10) == 100 # Should cap at 100
