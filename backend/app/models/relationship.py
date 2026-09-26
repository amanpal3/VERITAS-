"""
VERITAS - Relationship Models and Cytoscape Edge Schemas
Defines Pydantic representations for Knowledge Graph edges, evidentiary provenance,
and Cytoscape.js canvas edge elements.
"""
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, model_validator


class RelationshipType(str, Enum):
    USES_PHONE = "USES_PHONE"
    CALLED = "CALLED"
    OWNS = "OWNS"
    OPERATES = "OPERATES"
    LOCATED_AT = "LOCATED_AT"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    SUPERVISES = "SUPERVISES"
    COORDINATES_WITH = "COORDINATES_WITH"
    CONTROLS = "CONTROLS"
    MEMBER_OF = "MEMBER_OF"
    OWNS_ACCOUNT = "OWNS_ACCOUNT"
    TRANSACTED_WITH = "TRANSACTED_WITH"


class Provenance(BaseModel):
    source_id: str = Field(default="UNKNOWN_SOURCE", description="Originating document or record ID")
    source_type: str = Field(default="POLICE_REPORT", description="POLICE_REPORT, SURVEILLANCE, TELECOM_CDR, BANK_LEDGER")
    snippet: Optional[str] = Field(default=None, description="Verbatim text excerpt or transaction citation")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Evidentiary confidence score")

    @model_validator(mode="before")
    @classmethod
    def normalize_defaults(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "source_id" not in data or not data["source_id"]:
                data["source_id"] = "REF-RECORD-001"
            if "source_type" not in data or not data["source_type"]:
                data["source_type"] = "POLICE_REPORT"
            if "confidence" not in data or data["confidence"] is None:
                data["confidence"] = 1.0
        return data


class CytoscapeEdgeData(BaseModel):
    id: str
    source: str
    target: str
    type: str
    weight: float = 1.0
    timestamp: Optional[str] = None
    provenance: Provenance = Field(default_factory=Provenance)
    attributes: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def parse_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if hasattr(data.get("type"), "value"):
                data["type"] = data["type"].value
            # Ensure provenance is structured dict/model
            if "provenance" not in data or data["provenance"] is None:
                data["provenance"] = {}
        return data


class CytoscapeEdge(BaseModel):
    data: CytoscapeEdgeData


class ConnectionDetail(BaseModel):
    relationship_id: str
    type: str
    target_id: str
    target_name: str
    target_type: str
    provenance: Provenance
    weight: float = 1.0
    timestamp: Optional[str] = None
