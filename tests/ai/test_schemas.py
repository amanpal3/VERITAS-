"""
VERITAS - Unit Tests for Member 1 AI Schemas
Covers entity and relationship validation, boundary checks, controlled vocabulary,
provenance verification, and compatibility between 'label' and 'name'.
"""
import os
import json
import pytest
from pydantic import ValidationError

from ai.schemas.entity import Entity, EntityType
from ai.schemas.relationship import Provenance, Relationship, RelationshipType


# 1. Valid Entity Tests
def test_valid_entity():
    """Verify that a properly structured entity validates cleanly with both label and name."""
    entity_data = {
        "id": "P001",
        "type": "Person",
        "label": "Vikramaditya Singhania",
        "role": "Syndicate Mastermind",
        "risk_score": 96.0,
        "aliases": ["Vikram", "The Don"],
        "attributes": {"residence": "Vasant Vihar, New Delhi"},
        "source_records": ["FIR-188/2026", "INT-DEL-2026-409"],
    }
    entity = Entity(**entity_data)

    assert entity.id == "P001"
    assert entity.type == EntityType.PERSON
    assert entity.label == "Vikramaditya Singhania"
    assert entity.name == "Vikramaditya Singhania"
    assert entity.risk_score == 96.0
    assert len(entity.aliases) == 2
    assert "FIR-188/2026" in entity.source_records


def test_entity_name_compatibility():
    """Verify backward compatibility when 'name' is supplied instead of 'label'."""
    entity = Entity(
        id="P002",
        type="Person",
        name="Tariq Sheikh",
        role="Hawala Broker",
        risk_score=88.0,
    )
    assert entity.label == "Tariq Sheikh"
    assert entity.name == "Tariq Sheikh"


def test_invalid_entity_type():
    """Verify that unsupported entity types are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        Entity(
            id="W001",
            type="Weapon",  # Invalid type not in EntityType
            label="Glock 19",
            risk_score=50.0,
        )
    assert "type" in str(exc_info.value)


# 2. Invalid Risk Score Tests
def test_invalid_risk_score_above_100():
    """Verify that a risk_score exceeding 100 raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        Entity(
            id="P001",
            type="Person",
            label="Vikram Singhania",
            risk_score=100.1,
        )
    assert "risk_score" in str(exc_info.value)


def test_invalid_risk_score_negative():
    """Verify that a negative risk_score raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        Entity(
            id="P001",
            type="Person",
            label="Vikram Singhania",
            risk_score=-5.0,
        )
    assert "risk_score" in str(exc_info.value)


# 3. Valid Relationship Tests
def test_valid_relationship():
    """Verify that an approved relationship with provenance validates cleanly."""
    rel_data = {
        "id": "R001",
        "source": "P001",
        "target": "PH001",
        "type": "USES_PHONE",
        "weight": 1.0,
        "timestamp": "2026-03-01T00:00:00Z",
        "provenance": {
            "source_id": "INT-DEL-2026-409",
            "source_type": "SURVEILLANCE",
            "snippet": "Phone registered to Vasant Vihar residence.",
            "confidence": 0.95,
        },
    }
    rel = Relationship(**rel_data)

    assert rel.id == "R001"
    assert rel.source == "P001"
    assert rel.target == "PH001"
    assert rel.type == RelationshipType.USES_PHONE
    assert rel.provenance.confidence == 0.95
    assert rel.provenance.source_id == "INT-DEL-2026-409"


# 4. Invalid Confidence Tests
def test_invalid_confidence_above_one():
    """Verify that confidence exceeding 1.0 raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        Provenance(
            source_id="FIR-104",
            source_type="POLICE_REPORT",
            snippet="Suspect interrogated.",
            confidence=1.05,
        )
    assert "confidence" in str(exc_info.value)


def test_invalid_confidence_negative():
    """Verify that negative confidence raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        Provenance(
            source_id="FIR-104",
            source_type="POLICE_REPORT",
            snippet="Suspect interrogated.",
            confidence=-0.1,
        )
    assert "confidence" in str(exc_info.value)


# 5. Invalid Relationship Type Tests
def test_invalid_relationship_type():
    """Verify that relationship verbs not in GRAPH_SCHEMA.md vocabulary are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        Relationship(
            id="R999",
            source="P001",
            target="P002",
            type="FRIEND_OF",  # Disallowed verb
            provenance=Provenance(
                source_id="INT-001",
                source_type="INTEL",
                snippet="Met at cafe.",
                confidence=0.8,
            ),
        )
    assert "type" in str(exc_info.value)


# 6. Provenance Validation Tests
def test_provenance_empty_source():
    """Verify that empty source_id or source_type in provenance is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        Provenance(
            source_id="",  # Empty source ID
            source_type="POLICE_REPORT",
            snippet="Valid snippet",
            confidence=0.9,
        )
    assert "source_id" in str(exc_info.value)


def test_relationship_invalid_endpoints():
    """Verify that self-referential relationships (source == target) or empty endpoints are rejected."""
    # Self-loop
    with pytest.raises(ValidationError) as exc_info:
        Relationship(
            id="R001",
            source="P001",
            target="P001",
            type="ASSOCIATED_WITH",
            provenance=Provenance(
                source_id="INT-001",
                source_type="INTEL",
                snippet="Self loop.",
                confidence=0.9,
            ),
        )
    assert "Self-referential" in str(exc_info.value)

    # Empty endpoint
    with pytest.raises(ValidationError) as exc_info:
        Relationship(
            id="R001",
            source="   ",
            target="P002",
            type="ASSOCIATED_WITH",
            provenance=Provenance(
                source_id="INT-001",
                source_type="INTEL",
                snippet="Empty source.",
                confidence=0.9,
            ),
        )
    assert "source" in str(exc_info.value)


# 7. Regression Test on Existing Benchmark Demo Fixtures
def test_existing_demo_entities_and_relationships_validate():
    """Verify that all 29 entities and 33 relationships from data/demo/ validate with 0 errors."""
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    entities_path = os.path.join(root_dir, "data", "demo", "entities.json")
    relationships_path = os.path.join(root_dir, "data", "demo", "relationships.json")

    with open(entities_path, "r", encoding="utf-8") as f:
        raw_entities = json.load(f)
    with open(relationships_path, "r", encoding="utf-8") as f:
        raw_relationships = json.load(f)

    validated_entities = [Entity(**e) for e in raw_entities]
    assert len(validated_entities) == 29

    validated_relationships = [Relationship(**r) for r in raw_relationships]
    assert len(validated_relationships) == 33
