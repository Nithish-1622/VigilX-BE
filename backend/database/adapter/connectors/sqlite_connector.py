from typing import Any, AsyncGenerator, Dict, List, Optional
from ..core.base import BaseConnector
from ..core.models import Record, SearchQuery
from ..registry.registry import ConnectorRegistry
from ..normalization.normalization import NormalizationEngine
from ..utils.observability import track_performance, get_logger
from ..security.security import SecurityManager
import os

try:
    import aiosqlite
except ImportError:
    aiosqlite = None

logger = get_logger(__name__)

@ConnectorRegistry.register("sqlite")
class SQLiteConnector(BaseConnector):
    """Connector for SQLite databases."""
    
    def __init__(self, connection_string: str, **kwargs):
        # sqlite://path/to/db.sqlite
        super().__init__(connection_string, **kwargs)
        self.db_path = self.connection_string.replace("sqlite://", "")
        self.conn = None
        self.default_table = kwargs.get("table_name")

    async def connect(self) -> None:
        if aiosqlite is None:
            raise ImportError("aiosqlite is not installed.")
        if not os.path.exists(self.db_path):
            raise ValueError(f"SQLite DB not found: {self.db_path}")
        self.conn = await aiosqlite.connect(self.db_path)
        self.conn.row_factory = aiosqlite.Row
        self.is_connected = True

    async def disconnect(self) -> None:
        if self.conn:
            await self.conn.close()
            self.is_connected = False

    async def health(self) -> bool:
        if not self.conn: return False
        try:
            async with self.conn.execute("SELECT 1") as cursor:
                await cursor.fetchone()
            return True
        except Exception:
            return False

    @track_performance
    async def discover_schema(self) -> Dict[str, Any]:
        schema = {}
        async with self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'") as cursor:
            tables = [row[0] async for row in cursor]
            
        for t in tables:
            schema[t] = {}
            async with self.conn.execute(f"PRAGMA table_info('{t}')") as c:
                cols = await c.fetchall()
                for col in cols:
                    schema[t][col['name']] = col['type']
        return schema

    @track_performance
    async def discover_metadata(self) -> Dict[str, Any]:
        return {"source_type": "sqlite", "file_size_bytes": os.path.getsize(self.db_path)}

    @track_performance
    async def load(self) -> List[Record]:
        if not self.default_table: raise ValueError("table_name required")
        safe_table = SecurityManager.sanitize_sql(self.default_table)
        async with self.conn.execute(f"SELECT * FROM {safe_table} LIMIT 1000") as cursor:
            rows = await cursor.fetchall()
            return [await self.normalize(dict(row)) for row in rows]

    async def stream(self, batch_size: int = 1000) -> AsyncGenerator[List[Record], None]:
        if not self.default_table: raise ValueError("table_name required")
        safe_table = SecurityManager.sanitize_sql(self.default_table)
        async with self.conn.execute(f"SELECT * FROM {safe_table}") as cursor:
            while True:
                rows = await cursor.fetchmany(batch_size)
                if not rows: break
                yield [await self.normalize(dict(row)) for row in rows]

    async def search(self, query: SearchQuery) -> List[Record]: return []
    async def filter(self, conditions: Dict[str, Any]) -> List[Record]: return []
    async def aggregate(self, group_by: List[str], metrics: Dict[str, str]) -> List[Dict[str, Any]]: return []
    
    async def count(self) -> int:
        if not self.default_table: return 0
        safe_table = SecurityManager.sanitize_sql(self.default_table)
        async with self.conn.execute(f"SELECT count(*) FROM {safe_table}") as cursor:
            res = await cursor.fetchone()
            return res[0]

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
            source_type="sqlite",
            table=self.default_table,
            fields=normalized
        )

    async def close(self) -> None:
        await self.disconnect()
