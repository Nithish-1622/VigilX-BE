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

@ConnectorRegistry.register("excel")
class ExcelConnector(BaseConnector):
    """Connector for Excel files."""
    
    def __init__(self, connection_string: str, **kwargs):
        super().__init__(connection_string, **kwargs)
        if not os.path.exists(self.connection_string):
            raise ValueError(f"Excel file not found: {self.connection_string}")
        self.filename = os.path.basename(self.connection_string)
        self.sheet_name = kwargs.get("sheet_name", 0) # default first sheet

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
        df = pd.read_excel(self.connection_string, sheet_name=self.sheet_name, nrows=100)
        df = PreprocessingEngine.clean_dataframe(df)
        return SchemaEngine.infer_schema_from_records(df.to_dict(orient="records"))

    @track_performance
    async def discover_metadata(self) -> Dict[str, Any]:
        return {
            "source_type": "excel",
            "file_size_bytes": os.path.getsize(self.connection_string),
            "filename": self.filename,
            "sheet": self.sheet_name
        }

    @track_performance
    async def load(self) -> List[Record]:
        if pd is None:
            raise ImportError("pandas is not installed.")
        df = pd.read_excel(self.connection_string, sheet_name=self.sheet_name)
        df = PreprocessingEngine.clean_dataframe(df)
        records = df.to_dict(orient="records")
        return [await self.normalize(r) for r in records]

    async def stream(self, batch_size: int = 1000) -> AsyncGenerator[List[Record], None]:
        if pd is None:
            raise ImportError("pandas is not installed.")
        # Pandas doesn't support chunksize for excel directly, we simulate it
        df = pd.read_excel(self.connection_string, sheet_name=self.sheet_name)
        df = PreprocessingEngine.clean_dataframe(df)
        records = df.to_dict(orient="records")
        for i in range(0, len(records), batch_size):
            yield [await self.normalize(r) for r in records[i:i + batch_size]]

    async def search(self, query: SearchQuery) -> List[Record]: return []
    async def filter(self, conditions: Dict[str, Any]) -> List[Record]: return []
    async def aggregate(self, group_by: List[str], metrics: Dict[str, str]) -> List[Dict[str, Any]]: return []
    
    async def count(self) -> int:
        if pd is None:
            raise ImportError("pandas is not installed.")
        df = pd.read_excel(self.connection_string, sheet_name=self.sheet_name, usecols=[0])
        return len(df)

    async def get_record(self, record_id: str) -> Optional[Record]: return None
    async def get_records(self, record_ids: List[str]) -> List[Record]: return []
    async def insert(self, records: List[Record]) -> bool: return False
    async def update(self, record_ids: List[str], updates: Dict[str, Any]) -> bool: return False
    async def delete(self, record_ids: List[str]) -> bool: return False
    async def semantic_search(self, query: str, limit: int = 10) -> List[Record]: return []
    async def keyword_search(self, query: str, limit: int = 10) -> List[Record]: return []
    async def hybrid_search(self, query: str, limit: int = 10) -> List[Record]: return []
    async def relationships(self, record_id: str) -> List[Dict[str, Any]]: return []
    async def profile(self) -> Dict[str, Any]: return {}
    async def validate(self) -> bool: return True

    async def normalize(self, raw_data: Dict[str, Any]) -> Record:
        cleaned = PreprocessingEngine.clean_dict(raw_data)
        normalized = NormalizationEngine.normalize_record(cleaned)
        return Record(
            source=self.connection_string,
            source_type="excel",
            collection=f"{self.filename}:{self.sheet_name}",
            fields=normalized
        )

    async def close(self) -> None:
        await self.disconnect()
