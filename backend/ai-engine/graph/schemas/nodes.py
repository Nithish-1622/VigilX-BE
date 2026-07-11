from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class NodeType(str, Enum):
    """Approved node labels for the Crime Knowledge Graph."""
    CASE = "Case"
    FIR = "FIR"
    ACCUSED = "Accused"
    VICTIM = "Victim"
    WITNESS = "Witness"
    LOCATION = "Location"
    POLICE_STATION = "PoliceStation"
    CRIME_TYPE = "CrimeType"
    MODUS_OPERANDI = "ModusOperandi"
    EVIDENCE = "Evidence"
    VEHICLE = "Vehicle"
    PHONE_NUMBER = "PhoneNumber"
    FINANCIAL_ACCOUNT = "FinancialAccount"
    TRANSACTION = "Transaction"
    ORGANIZATION = "Organization"
    INVESTIGATION = "Investigation"
    OFFICER = "Officer"
    SOCIO_ECONOMIC_INDICATOR = "SocioEconomicIndicator"

class BaseNode(BaseModel):
    """Base schema for all graph nodes."""
    model_config = ConfigDict(extra='allow')
    
    id: str = Field(..., description="Stable external identifier.")
    source_system: str = Field("DJANGO_API", description="Origin of the data.")
    created_at: str = Field(..., description="Timestamp of ingestion.")

class PersonNode(BaseNode):
    """Schema for person entities (Accused, Victim, Witness)."""
    name_hash: Optional[str] = None # Never use name as unique ID
    age_group: Optional[str] = None
    gender: Optional[str] = None
    # Add behavioral and aggregated profiling indicators below

class CaseNode(BaseNode):
    """Schema for a Case."""
    case_number: str
    status: str
    reported_date: str
