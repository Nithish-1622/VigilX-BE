from typing import Any, AsyncGenerator, Dict, List, Optional
from urllib.parse import urlparse
from ..core.base import BaseConnector
from ..core.models import Record, SearchQuery
from ..registry.registry import ConnectorRegistry
from ..normalization.normalization import NormalizationEngine
from ..utils.observability import track_performance, get_logger

try:
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError:
    AsyncIOMotorClient = None

logger = get_logger(__name__)

@ConnectorRegistry.register("mongodb")
class MongoDBConnector(BaseConnector):
    """Connector for MongoDB databases."""
    
    def __init__(self, connection_string: str, **kwargs):
        super().__init__(connection_string, **kwargs)
        self.client = None
        self.db = None
        self.collection_name = kwargs.get("collection_name")

    async def connect(self) -> None:
        if AsyncIOMotorClient is None:
            raise ImportError("motor is not installed. Please install it to use MongoDBConnector.")
        try:
            self.client = AsyncIOMotorClient(self.connection_string)
            # Extract DB name from URI
            parsed = urlparse(self.connection_string)
            db_name = parsed.path.lstrip('/') if parsed.path else kwargs.get('db_name', 'default_db')
            self.db = self.client[db_name]
            self.is_connected = True
            logger.info(f"Connected to MongoDB database: {db_name}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {e}")

    async def disconnect(self) -> None:
        if self.client:
            self.client.close()
            self.is_connected = False

    async def health(self) -> bool:
        if not self.client: return False
        try:
            await self.client.admin.command('ping')
            return True
        except Exception:
            return False

    @track_performance
    async def discover_schema(self) -> Dict[str, Any]:
        if not self.collection_name: return {}
        # Sample 50 docs for schema inference
        collection = self.db[self.collection_name]
        docs = await collection.find().limit(50).to_list(length=50)
        from ..schema.schema import SchemaEngine
        return SchemaEngine.infer_schema_from_records(docs)

    @track_performance
    async def discover_metadata(self) -> Dict[str, Any]:
        if not self.collection_name: return {}
        stats = await self.db.command("collstats", self.collection_name)
        return {
            "source_type": "mongodb",
            "count": stats.get("count"),
            "size": stats.get("size")
        }

    @track_performance
    async def load(self) -> List[Record]:
        if not self.collection_name: raise ValueError("collection_name required")
        docs = await self.db[self.collection_name].find().limit(1000).to_list(length=1000)
        return [await self.normalize(doc) for doc in docs]

    async def stream(self, batch_size: int = 1000) -> AsyncGenerator[List[Record], None]:
        if not self.collection_name: raise ValueError("collection_name required")
        cursor = self.db[self.collection_name].find()
        batch = []
        async for doc in cursor:
            batch.append(await self.normalize(doc))
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

    async def search(self, query: SearchQuery) -> List[Record]:
        # MongoDB query translation would go here
        return []

    async def filter(self, conditions: Dict[str, Any]) -> List[Record]:
        if not self.collection_name: return []
        docs = await self.db[self.collection_name].find(conditions).limit(100).to_list(length=100)
        return [await self.normalize(doc) for doc in docs]

    async def aggregate(self, group_by: List[str], metrics: Dict[str, str]) -> List[Dict[str, Any]]:
        return []

    async def count(self) -> int:
        if not self.collection_name: return 0
        return await self.db[self.collection_name].count_documents({})

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
        return []

    async def profile(self) -> Dict[str, Any]:
        return {}

    async def validate(self) -> bool:
        return True

    async def normalize(self, raw_data: Dict[str, Any]) -> Record:
        # handle ObjectId
        if "_id" in raw_data:
            raw_data["_id"] = str(raw_data["_id"])
        
        normalized = NormalizationEngine.normalize_record(raw_data)
        record_id = normalized.pop('_id', None) or normalized.pop('id', None)
        
        return Record(
            id=str(record_id) if record_id else None,
            source=self.connection_string,
            source_type="mongodb",
            collection=self.collection_name,
            fields=normalized
        )

    async def close(self) -> None:
        await self.disconnect()
