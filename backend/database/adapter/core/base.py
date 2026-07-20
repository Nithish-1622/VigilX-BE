from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List, Optional
from .models import Record, SearchQuery

class BaseConnector(ABC):
    """
    Abstract base class for all data connectors.
    Every connector must inherit from this and implement the identical interface.
    """
    
    def __init__(self, connection_string: str, **kwargs):
        self.connection_string = connection_string
        self.config = kwargs
        self.is_connected = False
        
    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the data source."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the data source."""
        pass

    @abstractmethod
    async def health(self) -> bool:
        """Check the health of the connection."""
        pass

    @abstractmethod
    async def discover_schema(self) -> Dict[str, Any]:
        """Automatically infer and return the schema of the source."""
        pass

    @abstractmethod
    async def discover_metadata(self) -> Dict[str, Any]:
        """Generate and return metadata about the source."""
        pass

    @abstractmethod
    async def load(self) -> List[Record]:
        """Load all records from the source (use carefully on large datasets)."""
        pass

    @abstractmethod
    async def stream(self, batch_size: int = 1000) -> AsyncGenerator[List[Record], None]:
        """Stream records using an async generator for large datasets."""
        pass

    @abstractmethod
    async def search(self, query: SearchQuery) -> List[Record]:
        """Execute a general search query."""
        pass

    @abstractmethod
    async def filter(self, conditions: Dict[str, Any]) -> List[Record]:
        """Filter records based on precise conditions."""
        pass

    @abstractmethod
    async def aggregate(self, group_by: List[str], metrics: Dict[str, str]) -> List[Dict[str, Any]]:
        """Perform aggregation operations."""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Return the total number of records."""
        pass

    @abstractmethod
    async def get_record(self, record_id: str) -> Optional[Record]:
        """Retrieve a specific record by ID."""
        pass

    @abstractmethod
    async def get_records(self, record_ids: List[str]) -> List[Record]:
        """Retrieve multiple specific records by ID."""
        pass

    @abstractmethod
    async def insert(self, records: List[Record]) -> bool:
        """Insert new records into the source."""
        pass

    @abstractmethod
    async def update(self, record_ids: List[str], updates: Dict[str, Any]) -> bool:
        """Update existing records."""
        pass

    @abstractmethod
    async def delete(self, record_ids: List[str]) -> bool:
        """Delete records from the source."""
        pass

    @abstractmethod
    async def semantic_search(self, query: str, limit: int = 10) -> List[Record]:
        """Perform a vector-based semantic search."""
        pass

    @abstractmethod
    async def keyword_search(self, query: str, limit: int = 10) -> List[Record]:
        """Perform a keyword search (e.g. BM25, Full Text)."""
        pass

    @abstractmethod
    async def hybrid_search(self, query: str, limit: int = 10) -> List[Record]:
        """Perform a hybrid search combining semantic and keyword results."""
        pass

    @abstractmethod
    async def relationships(self, record_id: str) -> List[Dict[str, Any]]:
        """Retrieve relationships for a specific record (graph nodes/edges, foreign keys)."""
        pass

    @abstractmethod
    async def profile(self) -> Dict[str, Any]:
        """Profile the data source (null %, duplicates, types, etc.)."""
        pass

    @abstractmethod
    async def validate(self) -> bool:
        """Validate the source data against the discovered schema."""
        pass

    @abstractmethod
    async def normalize(self, record: Dict[str, Any]) -> Record:
        """Normalize raw source data into a universal Record."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Alias for disconnect to support context managers."""
        pass
        
    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
