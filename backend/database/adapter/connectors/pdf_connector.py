from typing import Any, AsyncGenerator, Dict, List, Optional
import os
from ..core.base import BaseConnector
from ..core.models import Record, SearchQuery
from ..registry.registry import ConnectorRegistry
from ..preprocessing.text_processing import TextProcessingEngine
from ..utils.observability import track_performance, get_logger

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

logger = get_logger(__name__)

@ConnectorRegistry.register("pdf")
class PDFConnector(BaseConnector):
    """
    Connector for PDF files. Extracts text and chunks it for unstructured indexing.
    """
    
    def __init__(self, connection_string: str, **kwargs):
        super().__init__(connection_string, **kwargs)
        if not os.path.exists(self.connection_string):
            raise ValueError(f"PDF file not found: {self.connection_string}")
        self.filename = os.path.basename(self.connection_string)

    async def connect(self) -> None:
        if PyPDF2 is None:
            raise ImportError("PyPDF2 is not installed.")
        self.is_connected = True

    async def disconnect(self) -> None:
        self.is_connected = False

    async def health(self) -> bool:
        return os.path.exists(self.connection_string)

    @track_performance
    async def discover_schema(self) -> Dict[str, Any]:
        return {
            "page_num": "integer",
            "text": "string",
            "chunk_index": "integer"
        }

    @track_performance
    async def discover_metadata(self) -> Dict[str, Any]:
        if not PyPDF2: return {}
        try:
            with open(self.connection_string, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                meta = reader.metadata or {}
                return {
                    "source_type": "pdf",
                    "num_pages": len(reader.pages),
                    "author": meta.get("/Author", ""),
                    "title": meta.get("/Title", ""),
                    "filename": self.filename
                }
        except Exception as e:
            logger.error(f"Failed to read PDF metadata: {e}")
            return {}

    @track_performance
    async def load(self) -> List[Record]:
        records = []
        async for chunk in self.stream(batch_size=10):
            records.extend(chunk)
        return records

    async def stream(self, batch_size: int = 10) -> AsyncGenerator[List[Record], None]:
        if not PyPDF2: return
        
        with open(self.connection_string, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            total_pages = len(reader.pages)
            
            batch = []
            for page_num in range(total_pages):
                page = reader.pages[page_num]
                text = page.extract_text()
                
                if text:
                    chunks = TextProcessingEngine.chunk_text(text)
                    for i, chunk in enumerate(chunks):
                        raw_data = {
                            "page_num": page_num + 1,
                            "chunk_index": i,
                            "text": chunk
                        }
                        batch.append(await self.normalize(raw_data))
                        
                if len(batch) >= batch_size:
                    yield batch
                    batch = []
                    
            if batch:
                yield batch

    async def search(self, query: SearchQuery) -> List[Record]:
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
        # Generate some metadata via text processing
        text = raw_data.get("text", "")
        metadata = TextProcessingEngine.extract_metadata(text)
        
        return Record(
            source=self.connection_string,
            source_type="pdf",
            collection=self.filename,
            fields=raw_data,
            metadata=metadata
        )

    async def close(self) -> None:
        await self.disconnect()
