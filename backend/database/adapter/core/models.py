from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class Record(BaseModel):
    """
    Universal data model. Every source produces this identical structure.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str
    source_type: str
    collection: Optional[str] = None
    table: Optional[str] = None
    fields: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    relationships: List[Dict[str, Any]] = Field(default_factory=list)
    embeddings: Optional[List[float]] = None
    score: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SearchQuery(BaseModel):
    """
    Universal search query model.
    """
    query_text: Optional[str] = None
    filters: Dict[str, Any] = Field(default_factory=dict)
    limit: int = 10
    offset: int = 0
    include_embeddings: bool = False
    hybrid: bool = False
