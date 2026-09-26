"""
VERITAS - AI Relationship Schema
Defines canonical Pydantic data structures for extracted multi-relational edges
and evidentiary provenance. Strictly adheres to docs/GRAPH_SCHEMA.md vocabulary.
"""
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class RelationshipType(str, Enum):
    """
    Approved relationship vocabulary strictly defined in docs/GRAPH_SCHEMA.md.
    """
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

    @classmethod
    def _missing_(cls, value: object) -> Optional["RelationshipType"]:
        # Case-insensitive resolution fallback
        if isinstance(value, str):
            val_clean = value.strip().upper()
            for member in cls:
                if member.value == val_clean:
                    return member
        return None


class Provenance(BaseModel):
    """
    Evidentiary provenance payload binding every graph relationship
    to its supporting source record for 100% explainability.
    """
    model_config = ConfigDict(extra="allow")

    source_id: str = Field(..., description="Document ID or batch identifier (e.g. FIR-104/2026, CDR-LOG-2026)")
    source_type: str = Field(..., description="Source medium category (e.g. POLICE_REPORT, SURVEILLANCE, TELECOM_CDR)")
    snippet: str = Field(..., description="Verbatim sentence excerpt or analytical observation summary")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Extraction confidence score strictly bounded between 0.0 and 1.0"
    )

    @field_validator("source_id", "source_type", mode="after")
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Provenance source_id and source_type cannot be empty.")
        return cleaned


class Relationship(BaseModel):
    """
    Canonical Relationship Schema representing semantic and behavioral connections
    between entities in the knowledge graph.
    """
    model_config = ConfigDict(extra="allow")

    id: str = Field(..., description="Unique relationship identifier (e.g. R001)")
    source: str = Field(..., description="Originating entity identifier (e.g. P001)")
    target: str = Field(..., description="Destination entity identifier (e.g. PH001)")
    type: RelationshipType = Field(..., description="Controlled relationship semantic verb")
    directed: bool = Field(default=True, description="Indicates directional semantics")
    weight: float = Field(default=1.0, ge=0.0, description="Normalized strength, frequency, or monetary volume")
    timestamp: Optional[str] = Field(default=None, description="ISO-8601 UTC timestamp of occurrence or extraction")
    provenance: Provenance = Field(..., description="Mandatory ground-truth evidence citation")

    @field_validator("id", "source", "target", mode="after")
    @classmethod
    def validate_endpoints(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Relationship id, source, and target cannot be empty or whitespace.")
        return cleaned

    @model_validator(mode="after")
    def validate_no_self_loops(self) -> "Relationship":
        if self.source == self.target:
            raise ValueError(
                f"Self-referential relationships are invalid: source ('{self.source}') "
                f"cannot equal target ('{self.target}')."
            )
        return self
