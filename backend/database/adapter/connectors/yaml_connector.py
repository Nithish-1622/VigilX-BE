from typing import Any, AsyncGenerator, Dict, List, Optional
import os
try:
    import yaml
except ImportError:
    yaml = None
from ..core.base import BaseConnector
from ..core.models import Record, SearchQuery
from ..registry.registry import ConnectorRegistry
from ..normalization.normalization import NormalizationEngine
from ..schema.schema import SchemaEngine
from ..utils.observability import track_performance, get_logger

logger = get_logger(__name__)

@ConnectorRegistry.register("yaml")
class YAMLConnector(BaseConnector):
    """Connector for YAML files."""
    
    def __init__(self, connection_string: str, **kwargs):
        super().__init__(connection_string, **kwargs)
        if not os.path.exists(self.connection_string):
            raise ValueError(f"YAML file not found: {self.connection_string}")
        self.filename = os.path.basename(self.connection_string)

    async def connect(self) -> None:
        self.is_connected = True

    async def disconnect(self) -> None:
        self.is_connected = False

    async def health(self) -> bool:
        return os.path.exists(self.connection_string)

    @track_performance
    async def discover_schema(self) -> Dict[str, Any]:
        if yaml is None:
            raise ImportError("pyyaml is not installed.")
        with open(self.connection_string, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            records = data if isinstance(data, list) else [data]
            return SchemaEngine.infer_schema_from_records(records[:100])

    @track_performance
    async def discover_metadata(self) -> Dict[str, Any]:
        return {
            "source_type": "yaml",
            "file_size_bytes": os.path.getsize(self.connection_string),
            "filename": self.filename
        }

    @track_performance
    async def load(self) -> List[Record]:
        if yaml is None:
            raise ImportError("pyyaml is not installed.")
        with open(self.connection_string, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            records = data if isinstance(data, list) else [data]
            return [await self.normalize(r) for r in records]

    async def stream(self, batch_size: int = 1000) -> AsyncGenerator[List[Record], None]:
        if yaml is None:
            raise ImportError("pyyaml is not installed.")
        # yaml safe_load reads everything into memory.
        # safe_load_all can yield multiple docs.
        with open(self.connection_string, 'r', encoding='utf-8') as f:
            batch = []
            for doc in yaml.safe_load_all(f):
                if doc:
                    records = doc if isinstance(doc, list) else [doc]
                    for r in records:
                        batch.append(await self.normalize(r))
                        if len(batch) >= batch_size:
                            yield batch
                            batch = []
            if batch:
                yield batch

    async def search(self, query: SearchQuery) -> List[Record]: return []
    async def filter(self, conditions: Dict[str, Any]) -> List[Record]: return []
    async def aggregate(self, group_by: List[str], metrics: Dict[str, str]) -> List[Dict[str, Any]]: return []
    async def count(self) -> int: return 0
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
        normalized = NormalizationEngine.normalize_record(raw_data)
        record_id = normalized.pop('id', None)
        return Record(
            id=str(record_id) if record_id else None,
            source=self.connection_string,
            source_type="yaml",
            collection=self.filename,
            fields=normalized
        )

    async def close(self) -> None:
        await self.disconnect()
