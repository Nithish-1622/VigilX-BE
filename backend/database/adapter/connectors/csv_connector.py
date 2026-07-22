from typing import Any, AsyncGenerator, Dict, List, Optional
import os
try:
    import pandas as pd
except ImportError:
    pd = None
from ..core.base import BaseConnector
from ..core.models import Record, SearchQuery
from ..registry.registry import ConnectorRegistry
from ..normalization.normalization import NormalizationEngine
from ..preprocessing.preprocessing import PreprocessingEngine
from ..schema.schema import SchemaEngine
from ..utils.observability import track_performance, get_logger

logger = get_logger(__name__)

@ConnectorRegistry.register("csv")
class CSVConnector(BaseConnector):
    """
    Connector for CSV files.
    """
    
    def __init__(self, connection_string: str, **kwargs):
        super().__init__(connection_string, **kwargs)
        if not os.path.exists(self.connection_string):
            raise ValueError(f"CSV file not found: {self.connection_string}")
        self.filename = os.path.basename(self.connection_string)

    async def connect(self) -> None:
        self.is_connected = True

    async def disconnect(self) -> None:
        self.is_connected = False

    async def health(self) -> bool:
        return os.path.exists(self.connection_string)

    @track_performance
    async def discover_schema(self) -> Dict[str, Any]:
        if pd is None:
            raise ImportError("pandas is not installed.")
        # Read just a few rows to infer schema
        df = pd.read_csv(self.connection_string, nrows=100)
        df = PreprocessingEngine.clean_dataframe(df)
        records = df.to_dict(orient="records")
        return SchemaEngine.infer_schema_from_records(records)

    @track_performance
    async def discover_metadata(self) -> Dict[str, Any]:
        file_size = os.path.getsize(self.connection_string)
        return {
            "source_type": "csv",
            "file_size_bytes": file_size,
            "filename": self.filename
        }

    @track_performance
    async def load(self) -> List[Record]:
        if pd is None:
            raise ImportError("pandas is not installed.")
        df = pd.read_csv(self.connection_string)
        df = PreprocessingEngine.clean_dataframe(df)
        records = df.to_dict(orient="records")
        return [await self.normalize(r) for r in records]

    async def stream(self, batch_size: int = 1000) -> AsyncGenerator[List[Record], None]:
        if pd is None:
            raise ImportError("pandas is not installed.")
        for chunk in pd.read_csv(self.connection_string, chunksize=batch_size):
            chunk = PreprocessingEngine.clean_dataframe(chunk)
            records = chunk.to_dict(orient="records")
            normalized = [await self.normalize(r) for r in records]
            yield normalized

    async def search(self, query: SearchQuery) -> List[Record]:
        return []

    async def filter(self, conditions: Dict[str, Any]) -> List[Record]:
        return []

    async def aggregate(self, group_by: List[str], metrics: Dict[str, str]) -> List[Dict[str, Any]]:
        return []

    async def count(self) -> int:
        with open(self.connection_string, 'r', encoding='utf-8') as f:
            return sum(1 for line in f) - 1 # minus header

    async def get_record(self, record_id: str) -> Optional[Record]:
        return None

    async def get_records(self, record_ids: List[str]) -> List[Record]:
        return []

    async def insert(self, records: List[Record]) -> bool:
        # Appending to CSV
        return False

    async def update(self, record_ids: List[str], updates: Dict[str, Any]) -> bool:
        return False

    async def delete(self, record_ids: List[str]) -> bool:
        return False

    async def semantic_search(self, query: str, limit: int = 10) -> List[Record]:
        # Requires embedding the CSV rows first
        return []

    async def keyword_search(self, query: str, limit: int = 10) -> List[Record]:
        return []

    async def hybrid_search(self, query: str, limit: int = 10) -> List[Record]:
        return []

    async def relationships(self, record_id: str) -> List[Dict[str, Any]]:
        return []

    async def profile(self) -> Dict[str, Any]:
        return {}

    async def validate(self) -> bool:
        return True

    async def normalize(self, raw_data: Dict[str, Any]) -> Record:
        cleaned = PreprocessingEngine.clean_dict(raw_data)
        normalized = NormalizationEngine.normalize_record(cleaned)
        
        return Record(
            source=self.connection_string,
            source_type="csv",
            collection=self.filename,
            fields=normalized
        )

    async def close(self) -> None:
        await self.disconnect()
