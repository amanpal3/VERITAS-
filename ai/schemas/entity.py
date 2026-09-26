"""
VERITAS - AI Entity Schema
Defines canonical Pydantic data structures for extracted investigative entities.
Conforms strictly to docs/DATA_SCHEMA.md while preserving dual compatibility
for label and name fields used across the graph builder and API contract.
"""
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class EntityType(str, Enum):
    """
    Controlled vocabulary of entity types as defined in docs/DATA_SCHEMA.md.
    """
    PERSON = "Person"
    PHONE = "Phone"
    VEHICLE = "Vehicle"
    LOCATION = "Location"
    ORGANIZATION = "Organization"
    BANK_ACCOUNT = "BankAccount"

    @classmethod
    def _missing_(cls, value: object) -> Optional["EntityType"]:
        # Case-insensitive resolution fallback
        if isinstance(value, str):
            val_clean = value.strip().lower()
            for member in cls:
                if member.value.lower() == val_clean:
                    return member
        return None


class Entity(BaseModel):
    """
    Canonical Entity Schema representing suspects, communication devices,
    vehicles, locations, shell companies, and financial accounts.
    """
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: str = Field(..., description="Unique, immutable entity identifier (e.g. P001, PH001)")
    type: EntityType = Field(..., description="Controlled entity category")
    label: str = Field(..., description="Canonical display name or title")
    name: Optional[str] = Field(default=None, description="Compatibility alias for label")
    role: Optional[str] = Field(default=None, description="Investigative role or descriptor")
    risk_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Analytical risk score strictly bounded between 0 and 100"
    )
    aliases: List[str] = Field(default_factory=list, description="Known aliases, callsigns, or street monikers")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Domain-specific key-value attributes")
    source_records: List[str] = Field(default_factory=list, description="IDs of source reports mentioning this entity")

    # Optional graph metric annotations (populated by backend analytics)
    degree: Optional[int] = Field(default=None, description="Node degree centrality rank/count")
    betweenness: Optional[float] = Field(default=None, description="Betweenness centrality score")
    pagerank: Optional[float] = Field(default=None, description="PageRank structural authority score")
    community_id: Optional[int] = Field(default=None, description="Louvain modularity gang cluster assignment")

    @model_validator(mode="before")
    @classmethod
    def sync_label_and_name(cls, data: Any) -> Any:
        """
        Guarantees two-way compatibility between 'label' (DATA_SCHEMA.md / graph.json)
        and 'name' (entities.json / seed_demo.py / API_CONTRACT.md).
        """
        if isinstance(data, dict):
            label = data.get("label")
            name = data.get("name")
            if label is not None and name is None:
                data["name"] = str(label)
            elif name is not None and label is None:
                data["label"] = str(name)
        return data

    @field_validator("id", mode="after")
    @classmethod
    def validate_id(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Entity ID must be a non-empty string.")
        return cleaned

    @field_validator("label", mode="after")
    @classmethod
    def validate_label(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Entity label cannot be empty or whitespace.")
        return cleaned

    @model_validator(mode="after")
    def ensure_name_synced(self) -> "Entity":
        if self.name is None and self.label is not None:
            self.name = self.label
        return self
