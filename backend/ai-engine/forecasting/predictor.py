import logging
from typing import Dict, Any, List

from neo4j.connection import graph_manager
from neo4j.exceptions import GraphQueryError
from .exceptions import ForecastingError, InsufficientDataError

logger = logging.getLogger(__name__)

class CrimeForecaster:
    """
    Analyzes historical crime data to predict future trends and case volumes.
    """
    
    def __init__(self, min_history_months: int = 3):
        self.min_history_months = min_history_months
        
    def predict_next_month_volume(self) -> Dict[str, Any]:
        """
        Fetches the number of cases per month over the recorded history and
        uses a Simple Moving Average (SMA) to project the next month's volume.
        
        Note: Currently aggregates globally. A district filter can be added later.
        """
        cypher = """
        MATCH (c:Case)
        WHERE c.reported_date IS NOT NULL
        WITH substring(c.reported_date, 0, 7) AS month, count(c) AS volume
        ORDER BY month ASC
        RETURN month, volume
        """
        
        try:
            records = graph_manager.execute_read_query(cypher)
            history = [{"month": record["month"], "volume": record["volume"]} for record in records]
            
            if len(history) < self.min_history_months:
                raise InsufficientDataError(
                    f"Requires at least {self.min_history_months} months of data, but found {len(history)}."
                )
                
            # Compute Simple Moving Average over the last `min_history_months`
            recent_volumes = [item["volume"] for item in history[-self.min_history_months:]]
            prediction = sum(recent_volumes) / self.min_history_months
            
            # Predict next logical month (for simplicity, we just return the value)
            return {
                "historical_data": history,
                "moving_average_window": self.min_history_months,
                "predicted_volume_next_month": round(prediction, 2)
            }
            
        except InsufficientDataError:
            raise
        except GraphQueryError as e:
            logger.error("Graph query failed during forecasting.")
            raise ForecastingError(f"Failed to fetch historical data: {e}") from e
        except Exception as e:
            logger.error("Unexpected error during forecasting.", exc_info=True)
            raise ForecastingError(f"Unexpected forecasting error: {e}") from e
