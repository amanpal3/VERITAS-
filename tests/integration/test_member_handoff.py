"""
VERITAS - Focused Integration Test for Member 1 -> Member 2 Handoff
Verifies that the deterministic handoff fixture passes through IntelligencePipeline,
exercising Ingestion, Hybrid NER, Multi-Relational Extraction, Entity Resolution,
Endpoint Rewriting, Explainable Anomaly Detection, and PipelineResult JSON Serialization.
"""
import json
import pytest

from ai.pipeline import IntelligencePipeline, PipelineResult
from ai.schemas.entity import EntityType
from ai.schemas.relationship import RelationshipType
from tests.fixtures.handoff_fixture import get_all_handoff_records


@pytest.fixture
def pipeline() -> IntelligencePipeline:
    """Deterministic pipeline instance for integration testing."""
    return IntelligencePipeline(use_spacy=False)


def test_member_handoff_full_pipeline(pipeline: IntelligencePipeline):
    """
    Validates end-to-end processing of the canonical Member 1 -> Member 2 handoff fixture:
    1. At least 3 persons, 2 phones, 1 vehicle, 1 location, 1 organization, 2 bank accounts.
    2. Several relationship types extracted.
    3. Structured CDR and Transaction events preserved.
    4. Repeated entity mentions and cross-record co-reference resolution.
    5. Relationship endpoint rewriting to canonical IDs.
    6. Explainable anomaly detection.
    7. JSON and Dict serialization.
    """
    records = get_all_handoff_records()
    assert len(records) == 7, "Fixture must supply exactly 7 input records (2 docs, 2 cdrs, 3 txs)"

    result: PipelineResult = pipeline.run(records=records)

    # -----------------------------------------------------------------
    # 1. Pipeline Execution Diagnostics
    # -----------------------------------------------------------------
    meta = result.pipeline_metadata
    assert meta.status == "SUCCESS"
    assert meta.records_processed == 7
    assert meta.entity_count_raw > meta.entity_count
    assert meta.resolution_merge_count > 0

    # -----------------------------------------------------------------
    # 2. Entity Extraction & Canonical Resolution
    # -----------------------------------------------------------------
    entities = result.entities
    entities_by_type = {}
    for e in entities:
        entities_by_type.setdefault(e.type, []).append(e)

    # At least 3 persons
    persons = entities_by_type.get(EntityType.PERSON, [])
    assert len(persons) >= 3, f"Expected >=3 persons, found {len(persons)}"
    person_labels = {p.label for p in persons}
    assert any("Arjun Verma" in lbl for lbl in person_labels)
    assert any("Vikramaditya Singhania" in lbl for lbl in person_labels)
    assert any("Rajesh Kumar" in lbl for lbl in person_labels)

    # At least 2 phones
    phones = entities_by_type.get(EntityType.PHONE, [])
    assert len(phones) >= 2, f"Expected >=2 phones, found {len(phones)}"
    phone_labels = {p.label for p in phones}
    assert "+919811010006" in phone_labels
    assert "+919811010001" in phone_labels

    # At least 1 vehicle
    vehicles = entities_by_type.get(EntityType.VEHICLE, [])
    assert len(vehicles) >= 1, f"Expected >=1 vehicles, found {len(vehicles)}"
    assert any(v.label == "DL-1M-4412" for v in vehicles)

    # At least 1 location
    locations = entities_by_type.get(EntityType.LOCATION, [])
    assert len(locations) >= 1, f"Expected >=1 locations, found {len(locations)}"
    assert any(l.label == "Okhla Industrial Area" for l in locations)

    # At least 1 organization
    orgs = entities_by_type.get(EntityType.ORGANIZATION, [])
    assert len(orgs) >= 1, f"Expected >=1 organizations, found {len(orgs)}"
    assert any("Astra Logistics" in o.label for o in orgs)

    # At least 2 bank accounts
    accounts = entities_by_type.get(EntityType.BANK_ACCOUNT, [])
    assert len(accounts) >= 2, f"Expected >=2 bank accounts, found {len(accounts)}"
    account_labels = {a.label for a in accounts}
    assert "ACC-ASTRA-7701" in account_labels
    assert "ACC-SINGH-9901" in account_labels

    # -----------------------------------------------------------------
    # 3. Repeated Mentions & Cross-Document Entity Resolution
    # -----------------------------------------------------------------
    # Arjun Verma was present in INT-2026-01 and SURV-2026-02
    arjun_entities = [p for p in persons if p.label == "Arjun Verma"]
    assert len(arjun_entities) == 1, "Expected Arjun Verma to merge into 1 canonical node"
    arjun = arjun_entities[0]
    assert "INT-2026-01" in arjun.source_records
    assert "SURV-2026-02" in arjun.source_records

    # -----------------------------------------------------------------
    # 4. Multi-Relational Extraction & Endpoint Rewriting
    # -----------------------------------------------------------------
    relationships = result.relationships
    assert len(relationships) >= 8, f"Expected >=8 relationships, found {len(relationships)}"

    rel_types = {r.type for r in relationships}
    assert RelationshipType.OPERATES in rel_types
    assert RelationshipType.USES_PHONE in rel_types
    assert RelationshipType.LOCATED_AT in rel_types
    assert RelationshipType.CALLED in rel_types
    assert RelationshipType.TRANSACTED_WITH in rel_types

    # Verify endpoint rewriting for Arjun Verma
    operates_edges = [r for r in relationships if r.type == RelationshipType.OPERATES and r.source == arjun.id]
    assert len(operates_edges) >= 1, "Expected Arjun Verma's OPERATES edge to point to canonical ID"
    assert operates_edges[0].target == "V004"  # DL-1M-4412

    # -----------------------------------------------------------------
    # 5. Structured CDR & Transaction Events Preservation
    # -----------------------------------------------------------------
    called_edges = [r for r in relationships if r.type == RelationshipType.CALLED]
    assert len(called_edges) == 2, "Both CDR events must be preserved as distinct edges"
    assert {c.provenance.source_id for c in called_edges} == {"CDR-HND-001", "CDR-HND-002"}

    tx_edges = [r for r in relationships if r.type == RelationshipType.TRANSACTED_WITH]
    assert len(tx_edges) == 3, "All 3 financial transactions must be preserved as distinct edges"
    assert {t.provenance.source_id for t in tx_edges} == {"TX-HND-001", "TX-HND-002", "TX-HND-003"}
    amounts = sorted([t.weight for t in tx_edges])
    assert amounts == [50000.0, 75000.0, 8500000.0]

    # -----------------------------------------------------------------
    # 6. Referential Integrity & Topology Invariants
    # -----------------------------------------------------------------
    all_entity_ids = {e.id for e in entities}
    for r in relationships:
        assert r.source in all_entity_ids, f"Dangling source endpoint {r.source}"
        assert r.target in all_entity_ids, f"Dangling target endpoint {r.target}"
        assert r.source != r.target, f"Self-loop detected on edge {r.id}"
        assert r.provenance.source_id != ""
        assert 0.0 <= r.provenance.confidence <= 1.0

    # -----------------------------------------------------------------
    # 7. Explainable Anomaly Detection
    # -----------------------------------------------------------------
    anomalies = result.anomalies
    assert len(anomalies) >= 1, "Expected at least 1 anomaly flagged"
    tx_spike = next((a for a in anomalies if a.anomaly_type.value == "HIGH_TRANSACTION_AMOUNT"), None)
    assert tx_spike is not None, "Expected HIGH_TRANSACTION_AMOUNT anomaly"
    assert tx_spike.entity_id == "ACC-SINGH-9901"
    assert tx_spike.severity.value == "HIGH"
    assert "8,500,000.00" in tx_spike.evidence or "8500000" in str(tx_spike.feature_values)

    # -----------------------------------------------------------------
    # 8. PipelineResult Serialization
    # -----------------------------------------------------------------
    json_str = result.to_json(indent=2)
    assert isinstance(json_str, str)
    parsed = json.loads(json_str)
    assert "entities" in parsed
    assert "relationships" in parsed
    assert "anomalies" in parsed
    assert "pipeline_metadata" in parsed
    assert parsed["pipeline_metadata"]["status"] == "SUCCESS"
