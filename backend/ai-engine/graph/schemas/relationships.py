from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class RelationshipType(str, Enum):
    """Approved relationship types for the Crime Knowledge Graph."""
    ACCUSED_IN = "ACCUSED_IN"
    VICTIM_OF = "VICTIM_OF"
    WITNESS_OF = "WITNESS_OF"
    OCCURRED_AT = "OCCURRED_AT"
    REGISTERED_AT = "REGISTERED_AT"
    HAS_CRIME_TYPE = "HAS_CRIME_TYPE"
    USED_MODUS_OPERANDI = "USED_MODUS_OPERANDI"
    INVOLVES_EVIDENCE = "INVOLVES_EVIDENCE"
    USED_VEHICLE = "USED_VEHICLE"
    USES_PHONE = "USES_PHONE"
    OWNS_ACCOUNT = "OWNS_ACCOUNT"
    TRANSFERRED_TO = "TRANSFERRED_TO"
    TRANSFERRED_FROM = "TRANSFERRED_FROM"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    MEMBER_OF = "MEMBER_OF"
    RELATED_TO = "RELATED_TO"
    SIMILAR_TO = "SIMILAR_TO"
    INVESTIGATED_BY = "INVESTIGATED_BY"
    LINKED_TO = "LINKED_TO"
    HAS_INDICATOR = "HAS_INDICATOR"
    PARTICIPATED_IN = "PARTICIPATED_IN"

class BaseRelationship(BaseModel):
    """Base schema for graph relationships/edges."""
    model_config = ConfigDict(extra='allow')
    
    source_type: str = Field(..., description="E.g., 'DJANGO_API', 'MODEL_INFERENCE'")
    generated_at: str = Field(..., description="Timestamp of inference or ingestion.")

class InferredRelationship(BaseRelationship):
    """Schema for AI-inferred relationships with required explainability."""
    source_type: str = Field("MODEL_INFERENCE", frozen=True)
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the inference.")
    evidence_ids: List[str] = Field(..., description="List of node IDs or external IDs supporting the inference.")
    reason: str = Field(..., description="Human-readable explanation of why this relationship was inferred.")
    inference_method: str = Field(..., description="Algorithm or model name used for inference.")
