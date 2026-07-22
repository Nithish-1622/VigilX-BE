from typing import Any, AsyncGenerator, Dict, List, Optional
import os
from ..core.base import BaseConnector
from ..core.models import Record, SearchQuery
from ..registry.registry import ConnectorRegistry
from ..preprocessing.text_processing import TextProcessingEngine
from ..utils.observability import track_performance, get_logger

logger = get_logger(__name__)

@ConnectorRegistry.register("txt")
class TXTConnector(BaseConnector):
    """Connector for raw TXT files (unstructured text)."""
    
    def __init__(self, connection_string: str, **kwargs):
        super().__init__(connection_string, **kwargs)
        if not os.path.exists(self.connection_string):
            raise ValueError(f"TXT file not found: {self.connection_string}")
        self.filename = os.path.basename(self.connection_string)

    async def connect(self) -> None:
        self.is_connected = True

    async def disconnect(self) -> None:
        self.is_connected = False

    async def health(self) -> bool:
        return os.path.exists(self.connection_string)

    @track_performance
    async def discover_schema(self) -> Dict[str, Any]:
        return {
            "chunk_index": "integer",
            "text": "string"
        }

    @track_performance
    async def discover_metadata(self) -> Dict[str, Any]:
        return {
            "source_type": "txt",
            "file_size_bytes": os.path.getsize(self.connection_string),
            "filename": self.filename
        }

    @track_performance
    async def load(self) -> List[Record]:
        records = []
        async for batch in self.stream(batch_size=50):
            records.extend(batch)
        return records

    async def stream(self, batch_size: int = 50) -> AsyncGenerator[List[Record], None]:
        # For huge txt files, we'll read block by block, but simple chunking works for now
        with open(self.connection_string, 'r', encoding='utf-8', errors='ignore') as f:
            full_text = f.read()
            
        chunks = TextProcessingEngine.chunk_text(full_text)
        batch = []
        for i, chunk in enumerate(chunks):
            raw_data = {"chunk_index": i, "text": chunk}
            batch.append(await self.normalize(raw_data))
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
        text = raw_data.get("text", "")
        metadata = TextProcessingEngine.extract_metadata(text)
        
        return Record(
            source=self.connection_string,
            source_type="txt",
            collection=self.filename,
            fields=raw_data,
            metadata=metadata
        )

    async def close(self) -> None:
        await self.disconnect()
