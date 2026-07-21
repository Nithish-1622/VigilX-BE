from typing import Any, AsyncGenerator, Dict, List, Optional
import json
from ..core.base import BaseConnector
from ..core.models import Record, SearchQuery
from ..core.exceptions import ConnectionError, QueryExecutionError
from ..registry.registry import ConnectorRegistry
from ..normalization.normalization import NormalizationEngine
from ..utils.observability import track_performance, get_logger
from ..security.security import SecurityManager

try:
    import asyncpg
except ImportError:
    asyncpg = None

logger = get_logger(__name__)

@ConnectorRegistry.register("postgresql")
class PostgreSQLConnector(BaseConnector):
    """
    Connector for PostgreSQL databases.
    """
    
    def __init__(self, connection_string: str, **kwargs):
        super().__init__(connection_string, **kwargs)
        self.pool = None
        self.default_table = kwargs.get("table_name")

    async def connect(self) -> None:
        if asyncpg is None:
            raise ConnectionError("asyncpg is not installed. Please install it to use PostgreSQLConnector.")
        try:
            self.pool = await asyncpg.create_pool(dsn=self.connection_string)
            self.is_connected = True
            logger.info("Connected to PostgreSQL")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to PostgreSQL: {e}")

    async def disconnect(self) -> None:
        if self.pool:
            await self.pool.close()
            self.is_connected = False
            logger.info("Disconnected from PostgreSQL")

    async def health(self) -> bool:
        if not self.pool:
            return False
        try:
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
                return True
        except Exception:
            return False

    @track_performance
    async def discover_schema(self) -> Dict[str, Any]:
        query = """
        SELECT table_name, column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'public';
        """
        schema = {}
        async with self.pool.acquire() as conn:
            records = await conn.fetch(query)
            for r in records:
                t = r['table_name']
                if t not in schema:
                    schema[t] = {}
                schema[t][r['column_name']] = r['data_type']
        return schema

    @track_performance
    async def discover_metadata(self) -> Dict[str, Any]:
        # Would fetch counts, index info, etc.
        return {"source_type": "postgresql"}

    @track_performance
    async def load(self) -> List[Record]:
        if not self.default_table:
            raise ValueError("default_table must be provided in config to load().")
        # Sanitize table name
        safe_table = SecurityManager.sanitize_sql(self.default_table)
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(f"SELECT * FROM {safe_table} LIMIT 1000")
            return [await self.normalize(dict(row)) for row in rows]

    async def stream(self, batch_size: int = 1000) -> AsyncGenerator[List[Record], None]:
        if not self.default_table:
            raise ValueError("default_table must be provided.")
        safe_table = SecurityManager.sanitize_sql(self.default_table)
        
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Server-side cursor
                async for record_row in conn.cursor(f"SELECT * FROM {safe_table}"):
                    # In a real implementation we would yield in batches
                    yield [await self.normalize(dict(record_row))]

    @track_performance
    async def search(self, query: SearchQuery) -> List[Record]:
        # Implement SQL search translation here based on SearchQuery.filters
        return []

    async def filter(self, conditions: Dict[str, Any]) -> List[Record]:
        return []

    async def aggregate(self, group_by: List[str], metrics: Dict[str, str]) -> List[Dict[str, Any]]:
        return []

    async def count(self) -> int:
        return 0

    async def get_record(self, record_id: str) -> Optional[Record]:
        return None

    async def get_records(self, record_ids: List[str]) -> List[Record]:
        return []

    async def insert(self, records: List[Record]) -> bool:
        return False

    async def update(self, record_ids: List[str], updates: Dict[str, Any]) -> bool:
        return False

    async def delete(self, record_ids: List[str]) -> bool:
        return False

    async def semantic_search(self, query: str, limit: int = 10) -> List[Record]:
        # Usually requires pgvector
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
        normalized_fields = NormalizationEngine.normalize_record(raw_data)
        
        # Look for primary key (id, uuid, etc)
        record_id = None
        for key in ['id', 'uuid', 'guid', 'pk']:
            if key in normalized_fields:
                record_id = str(normalized_fields.pop(key))
                break
                
        return Record(
            id=record_id if record_id else None,
            source=self.connection_string,
            source_type="postgresql",
            table=self.default_table,
            fields=normalized_fields
        )

    async def close(self) -> None:
        await self.disconnect()
