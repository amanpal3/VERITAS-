"""
VERITAS - Entity Models and Cytoscape Node Schemas
Defines Pydantic representations for Knowledge Graph entities, suspect dossiers,
and Cytoscape.js canvas node elements.
"""
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator


class EntityType(str, Enum):
    PERSON = "Person"
    PHONE = "Phone"
    VEHICLE = "Vehicle"
    ORGANIZATION = "Organization"
    LOCATION = "Location"
    BANK_ACCOUNT = "BankAccount"


class EntityMetrics(BaseModel):
    degree: int = Field(default=0, description="Total in/out connectivity degree")
    betweenness: float = Field(default=0.0, description="Normalized betweenness centrality score")
    pagerank: float = Field(default=0.0, description="PageRank importance score")
    community_id: Optional[int] = Field(default=None, description="Assigned community partition ID")


class CytoscapeNodeData(BaseModel):
    id: str
    label: str
    type: str
    role: Optional[str] = None
    risk_score: float = 0.0
    aliases: List[str] = Field(default_factory=list)
    degree: int = 0
    betweenness: float = 0.0
    pagerank: float = 0.0
    community_id: Optional[int] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)
    source_records: List[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def populate_defaults_and_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Fallback label to name or id
            if "label" not in data or not data["label"]:
                data["label"] = data.get("name") or data.get("id") or "Unknown"
            # Normalize type enum if passed as enum
            if hasattr(data.get("type"), "value"):
                data["type"] = data["type"].value
        return data


class CytoscapeNode(BaseModel):
    data: CytoscapeNodeData


class EntitySummary(BaseModel):
    id: str
    name: str
    type: str
    role: Optional[str] = None
    risk_score: float = 0.0
    aliases: List[str] = Field(default_factory=list)
    community_id: Optional[int] = None

    @model_validator(mode="before")
    @classmethod
    def sync_name_and_label(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "name" not in data or not data["name"]:
                data["name"] = data.get("label") or data.get("id") or "Unknown"
            if hasattr(data.get("type"), "value"):
                data["type"] = data["type"].value
        return data
