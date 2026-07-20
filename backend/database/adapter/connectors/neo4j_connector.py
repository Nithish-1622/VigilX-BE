from typing import Any, AsyncGenerator, Dict, List, Optional
from ..core.base import BaseConnector
from ..core.models import Record, SearchQuery
from ..registry.registry import ConnectorRegistry
from ..utils.observability import track_performance, get_logger
from ..security.security import SecurityManager

try:
    from neo4j import AsyncGraphDatabase
except ImportError:
    AsyncGraphDatabase = None

logger = get_logger(__name__)

@ConnectorRegistry.register("neo4j")
class Neo4jConnector(BaseConnector):
    """Connector for Neo4j Graph Database."""
    
    def __init__(self, connection_string: str, **kwargs):
        super().__init__(connection_string, **kwargs)
        self.driver = None
        self.user = kwargs.get("user", "neo4j")
        self.password = kwargs.get("password", "")

    async def connect(self) -> None:
        if AsyncGraphDatabase is None:
            raise ImportError("neo4j is not installed.")
        try:
            self.driver = AsyncGraphDatabase.driver(self.connection_string, auth=(self.user, self.password))
            await self.driver.verify_connectivity()
            self.is_connected = True
            logger.info("Connected to Neo4j")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Neo4j: {e}")

    async def disconnect(self) -> None:
        if self.driver:
            await self.driver.close()
            self.is_connected = False

    async def health(self) -> bool:
        if not self.driver: return False
        try:
            await self.driver.verify_connectivity()
            return True
        except Exception:
            return False

    @track_performance
    async def discover_schema(self) -> Dict[str, Any]:
        schema = {}
        async with self.driver.session() as session:
            # Get node labels and their properties
            result = await session.run("CALL db.schema.nodeTypeProperties()")
            records = await result.data()
            for r in records:
                label = r.get('nodeType', '').strip(":`")
                if label not in schema: schema[label] = {}
                schema[label][r['propertyName']] = r['propertyTypes']
        return schema

    @track_performance
    async def discover_metadata(self) -> Dict[str, Any]:
        return {"source_type": "neo4j"}

    @track_performance
    async def load(self) -> List[Record]:
        async with self.driver.session() as session:
            result = await session.run("MATCH (n) RETURN n LIMIT 100")
            records = await result.data()
            return [await self.normalize(r['n']) for r in records if 'n' in r]

    async def stream(self, batch_size: int = 1000) -> AsyncGenerator[List[Record], None]:
        # Cypher streaming logic
        pass

    async def search(self, query: SearchQuery) -> List[Record]:
        return []

    async def filter(self, conditions: Dict[str, Any]) -> List[Record]:
        return []

    async def aggregate(self, group_by: List[str], metrics: Dict[str, str]) -> List[Dict[str, Any]]:
        return []

    async def count(self) -> int:
        async with self.driver.session() as session:
            res = await session.run("MATCH (n) RETURN count(n) as c")
            record = await res.single()
            return record["c"]

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
        return []

    async def keyword_search(self, query: str, limit: int = 10) -> List[Record]:
        return []

    async def hybrid_search(self, query: str, limit: int = 10) -> List[Record]:
        return []

    async def relationships(self, record_id: str) -> List[Dict[str, Any]]:
        # Retrieve edges for a node
        safe_id = SecurityManager.sanitize_cypher(record_id)
        query = f"MATCH (n)-[r]-(m) WHERE id(n) = {safe_id} RETURN type(r) as rel, labels(m) as target_label, properties(m) as target_props"
        async with self.driver.session() as session:
            res = await session.run(query)
            return await res.data()

    async def profile(self) -> Dict[str, Any]:
        return {}

    async def validate(self) -> bool:
        return True

    async def normalize(self, raw_data: Dict[str, Any]) -> Record:
        # raw_data is a dict of node properties
        from ..normalization.normalization import NormalizationEngine
        normalized = NormalizationEngine.normalize_record(raw_data)
        record_id = normalized.pop('element_id', None) or normalized.pop('id', None)
        
        return Record(
            id=str(record_id) if record_id else None,
            source=self.connection_string,
            source_type="neo4j",
            fields=normalized
        )

    async def close(self) -> None:
        await self.disconnect()
