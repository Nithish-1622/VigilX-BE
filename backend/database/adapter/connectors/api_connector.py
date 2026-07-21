from typing import Any, AsyncGenerator, Dict, List, Optional
try:
    import httpx
except ImportError:
    httpx = None
from ..core.base import BaseConnector
from ..core.models import Record, SearchQuery
from ..registry.registry import ConnectorRegistry
from ..normalization.normalization import NormalizationEngine
from ..schema.schema import SchemaEngine
from ..utils.observability import track_performance, get_logger

logger = get_logger(__name__)

@ConnectorRegistry.register("api")
class APIConnector(BaseConnector):
    """Connector for REST APIs."""
    
    def __init__(self, connection_string: str, **kwargs):
        super().__init__(connection_string, **kwargs)
        self.headers = kwargs.get("headers", {})
        self.params = kwargs.get("params", {})
        self.client = None

    async def connect(self) -> None:
        if httpx is None:
            raise ImportError("httpx is not installed.")
        self.client = httpx.AsyncClient(headers=self.headers, params=self.params, timeout=30.0)
        self.is_connected = True

    async def disconnect(self) -> None:
        if self.client:
            await self.client.aclose()
            self.is_connected = False

    async def health(self) -> bool:
        if not self.client: return False
        try:
            # simple HEAD request to check availability
            res = await self.client.head(self.connection_string)
            return res.status_code < 500
        except Exception:
            return False

    @track_performance
    async def discover_schema(self) -> Dict[str, Any]:
        data = await self._fetch_data()
        records = data if isinstance(data, list) else [data]
        return SchemaEngine.infer_schema_from_records(records[:50])

    @track_performance
    async def discover_metadata(self) -> Dict[str, Any]:
        return {"source_type": "api", "endpoint": self.connection_string}

    async def _fetch_data(self) -> Any:
        res = await self.client.get(self.connection_string)
        res.raise_for_status()
        return res.json()

    @track_performance
    async def load(self) -> List[Record]:
        data = await self._fetch_data()
        records = data if isinstance(data, list) else [data]
        return [await self.normalize(r) for r in records]

    async def stream(self, batch_size: int = 100) -> AsyncGenerator[List[Record], None]:
        # Usually APIs require pagination, simulated here as single block
        records = await self.load()
        for i in range(0, len(records), batch_size):
            yield records[i:i+batch_size]

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
        record_id = normalized.pop('id', None) or normalized.pop('uuid', None)
        return Record(
            id=str(record_id) if record_id else None,
            source=self.connection_string,
            source_type="api",
            fields=normalized
        )

    async def close(self) -> None:
        await self.disconnect()
