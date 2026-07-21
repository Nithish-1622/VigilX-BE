from typing import Any, AsyncGenerator, Dict, List, Optional
from urllib.parse import urlparse
from ..core.base import BaseConnector
from ..core.models import Record, SearchQuery
from ..registry.registry import ConnectorRegistry
from ..normalization.normalization import NormalizationEngine
from ..utils.observability import track_performance, get_logger
from ..security.security import SecurityManager

try:
    import aiomysql
except ImportError:
    aiomysql = None

logger = get_logger(__name__)

@ConnectorRegistry.register("mysql")
class MySQLConnector(BaseConnector):
    """Connector for MySQL databases."""
    
    def __init__(self, connection_string: str, **kwargs):
        super().__init__(connection_string, **kwargs)
        self.pool = None
        self.default_table = kwargs.get("table_name")

    async def connect(self) -> None:
        if aiomysql is None:
            raise ImportError("aiomysql is not installed.")
        parsed = urlparse(self.connection_string)
        self.pool = await aiomysql.create_pool(
            host=parsed.hostname,
            port=parsed.port or 3306,
            user=parsed.username,
            password=parsed.password,
            db=parsed.path.lstrip('/'),
            autocommit=True
        )
        self.is_connected = True

    async def disconnect(self) -> None:
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.is_connected = False

    async def health(self) -> bool:
        if not self.pool: return False
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1")
            return True
        except Exception:
            return False

    @track_performance
    async def discover_schema(self) -> Dict[str, Any]:
        schema = {}
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute("SHOW TABLES")
                tables = [list(r.values())[0] for r in await cur.fetchall()]
                for t in tables:
                    schema[t] = {}
                    await cur.execute(f"DESCRIBE {t}")
                    for col in await cur.fetchall():
                        schema[t][col['Field']] = col['Type']
        return schema

    @track_performance
    async def discover_metadata(self) -> Dict[str, Any]:
        return {"source_type": "mysql"}

    @track_performance
    async def load(self) -> List[Record]:
        if not self.default_table: raise ValueError("table_name required")
        safe_table = SecurityManager.sanitize_sql(self.default_table)
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(f"SELECT * FROM {safe_table} LIMIT 1000")
                rows = await cur.fetchall()
                return [await self.normalize(dict(row)) for row in rows]

    async def stream(self, batch_size: int = 1000) -> AsyncGenerator[List[Record], None]:
        if not self.default_table: raise ValueError("table_name required")
        safe_table = SecurityManager.sanitize_sql(self.default_table)
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(f"SELECT * FROM {safe_table}")
                while True:
                    rows = await cur.fetchmany(batch_size)
                    if not rows: break
                    yield [await self.normalize(dict(row)) for row in rows]

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
            source_type="mysql",
            table=self.default_table,
            fields=normalized
        )

    async def close(self) -> None:
        await self.disconnect()
