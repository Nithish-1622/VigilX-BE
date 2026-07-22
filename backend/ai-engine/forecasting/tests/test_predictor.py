import pytest
from unittest.mock import patch, MagicMock

from forecasting.predictor import CrimeForecaster
from forecasting.exceptions import InsufficientDataError, ForecastingError

@pytest.fixture
def forecaster():
    return CrimeForecaster(min_history_months=3)

@patch('forecasting.predictor.graph_manager')
def test_predict_next_month_volume_success(mock_graph_manager, forecaster):
    mock_graph_manager.execute_read_query.return_value = [
        {"month": "2026-01", "volume": 10},
        {"month": "2026-02", "volume": 20},
        {"month": "2026-03", "volume": 30}
    ]
    
    result = forecaster.predict_next_month_volume()
    
    assert len(result["historical_data"]) == 3
    assert result["moving_average_window"] == 3
    # Average of 10, 20, 30 is 20.0
    assert result["predicted_volume_next_month"] == 20.0

@patch('forecasting.predictor.graph_manager')
def test_predict_next_month_volume_insufficient_data(mock_graph_manager, forecaster):
    mock_graph_manager.execute_read_query.return_value = [
        {"month": "2026-01", "volume": 10},
        {"month": "2026-02", "volume": 20}
    ]
    
    with pytest.raises(InsufficientDataError):
        forecaster.predict_next_month_volume()

@patch('forecasting.predictor.graph_manager')
def test_predict_next_month_volume_db_error(mock_graph_manager, forecaster):
    from db_neo4j.exceptions import GraphQueryError
    mock_graph_manager.execute_read_query.side_effect = GraphQueryError("Timeout")
    
    with pytest.raises(ForecastingError):
        forecaster.predict_next_month_volume()
