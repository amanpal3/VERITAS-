"""
VERITAS - AI Schemas Package
Exports canonical entity, relationship, and provenance schemas.
"""
from ai.schemas.entity import Entity, EntityType
from ai.schemas.relationship import Provenance, Relationship, RelationshipType

__all__ = [
    "Entity",
    "EntityType",
    "Relationship",
    "RelationshipType",
    "Provenance",
]
