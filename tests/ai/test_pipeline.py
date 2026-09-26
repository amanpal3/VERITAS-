"""
VERITAS - Tests for Master IntelligencePipeline Orchestrator
Tests end-to-end integration, FIR/CDR/Transaction pipelines, multi-source ingestion,
entity resolution rewriting, anomaly integration, provenance preservation,
determinism, malformed input handling, and JSON serialization.
"""
import json
import pytest
from datetime import datetime, timezone, timedelta
from typing import List

from ai.pipeline import IntelligencePipeline, PipelineResult, PipelineMetadata
from ai.ingestion.csv_parser import CDRRecord, TransactionRecord
from ai.ingestion.document_parser import DocumentRecord
from ai.schemas.entity import Entity, EntityType
from ai.schemas.relationship import Provenance, Relationship, RelationshipType


@pytest.fixture
def pipeline() -> IntelligencePipeline:
    return IntelligencePipeline(use_spacy=False)


# ---------------------------------------------------------------------
# 1. Empty Input Handled Safely
# ---------------------------------------------------------------------
def test_pipeline_empty_input(pipeline: IntelligencePipeline):
    res1 = pipeline.run([])
    assert isinstance(res1, PipelineResult)
    assert len(res1.entities) == 0
    assert len(res1.relationships) == 0
    assert len(res1.anomalies) == 0
    assert res1.pipeline_metadata.records_processed == 0
    assert res1.pipeline_metadata.status == "SUCCESS"

    res2 = pipeline.run(records=None, raw_data_path=None)
    assert len(res2.entities) == 0


# ---------------------------------------------------------------------
# 2. FIR / Document Narrative Pipeline
# ---------------------------------------------------------------------
def test_pipeline_fir_document(pipeline: IntelligencePipeline):
    raw_fir = (
        "CONFIDENTIAL POLICE REPORT // CRIME NO: 104/2026\n"
        "Accused identified as Arjun Verma S/o Ramesh Verma was intercepted driving truck DL-1M-4412.\n"
        "Verma was found in possession of phone +919811010006.\n"
        "Suspect stated the contraband was received from Rajesh Kumar at Okhla Industrial Area."
    )
    result = pipeline.run(records=[raw_fir])

    assert len(result.entities) >= 3
    labels = {e.label for e in result.entities}
    assert "Arjun Verma" in labels
    assert "+919811010006" in labels
    assert "DL-1M-4412" in labels

    # Relationships extracted (OPERATES, USES_PHONE, etc.)
    assert len(result.relationships) >= 1
    rel_types = {r.type.value for r in result.relationships}
    assert "USES_PHONE" in rel_types or "OPERATES" in rel_types


# ---------------------------------------------------------------------
# 3. CDR Pipeline
# ---------------------------------------------------------------------
def test_pipeline_cdr_records(pipeline: IntelligencePipeline):
    cdrs = [
        CDRRecord(
            call_id="CDR001",
            caller_raw="+919811010001",
            caller_normalized="+919811010001",
            receiver_raw="+919811010002",
            receiver_normalized="+919811010002",
            timestamp_raw="2026-03-01T12:00:00Z",
            duration_sec=300,
            call_type="VOICE",
            cell_tower_id="TOWER_01",
            row_index=1,
        ),
        CDRRecord(
            call_id="CDR002",
            caller_raw="+919811010002",
            caller_normalized="+919811010002",
            receiver_raw="+919811010003",
            receiver_normalized="+919811010003",
            timestamp_raw="2026-03-01T14:30:00Z",
            duration_sec=150,
            call_type="VOICE",
            cell_tower_id="TOWER_02",
            row_index=2,
        ),
    ]
    result = pipeline.run(records=cdrs)

    assert len(result.entities) >= 3
    phone_types = {e.type for e in result.entities}
    assert phone_types == {EntityType.PHONE}

    assert len(result.relationships) == 2
    for r in result.relationships:
        assert r.type == RelationshipType.CALLED
        assert r.provenance.source_type == "TELECOM_CDR"


# ---------------------------------------------------------------------
# 4. Financial Transaction Pipeline
# ---------------------------------------------------------------------
def test_pipeline_transaction_records(pipeline: IntelligencePipeline):
    txs = [
        TransactionRecord(
            transaction_id="TX001",
            sender_account_raw="ACC-ASTRA-7701",
            sender_account_normalized="ACC-ASTRA-7701",
            receiver_account_raw="ACC-SHEIKH-4401",
            receiver_account_normalized="ACC-SHEIKH-4401",
            amount=850000.0,
            currency="INR",
            timestamp_raw="2026-03-01T10:00:00Z",
            payment_channel="RTGS",
            row_index=1,
        )
    ]
    result = pipeline.run(records=txs)

    assert len(result.entities) == 2
    for e in result.entities:
        assert e.type == EntityType.BANK_ACCOUNT

    assert len(result.relationships) == 1
    rel = result.relationships[0]
    assert rel.type == RelationshipType.TRANSACTED_WITH
    assert rel.weight == 850000.0
    assert rel.provenance.source_id == "TX001"


# ---------------------------------------------------------------------
# 5. Mixed Multi-Source Pipeline
# ---------------------------------------------------------------------
def test_pipeline_mixed_multi_source(pipeline: IntelligencePipeline):
    fir_text = (
        "Police Report: Operations overseen by Vikramaditya Singhania S/o Ramesh Singhania with primary line +919811010001."
    )
    cdr = CDRRecord(
        call_id="CDR1001",
        caller_raw="+919811010001",
        caller_normalized="+919811010001",
        receiver_raw="+919811010002",
        receiver_normalized="+919811010002",
        timestamp_raw="2026-03-01T12:00:00Z",
        duration_sec=200,
        call_type="VOICE",
        cell_tower_id="TOWER_CP",
        row_index=1,
    )
    tx = TransactionRecord(
        transaction_id="TX1001",
        sender_account_raw="ACC-SINGH-9901",
        sender_account_normalized="ACC-SINGH-9901",
        receiver_account_raw="ACC-ASTRA-7701",
        receiver_account_normalized="ACC-ASTRA-7701",
        amount=1500000.0,
        currency="INR",
        timestamp_raw="2026-03-01T15:00:00Z",
        payment_channel="RTGS",
        row_index=1,
    )

    result = pipeline.run(records=[fir_text, cdr, tx])
    assert result.pipeline_metadata.records_processed == 3

    types = {e.type for e in result.entities}
    assert EntityType.PERSON in types
    assert EntityType.PHONE in types
    assert EntityType.BANK_ACCOUNT in types


# ---------------------------------------------------------------------
# 6. Entity Extraction Reaches Final Output
# ---------------------------------------------------------------------
def test_entity_extraction_reaches_final_output(pipeline: IntelligencePipeline):
    doc = DocumentRecord(
        source_id="INT-001",
        document_type="SURVEILLANCE",
        raw_text="Observed truck DL-4C-9901 parked outside warehouse at Okhla Industrial Area.",
        file_path="inline_document",
        file_name="surveillance.txt",
    )
    result = pipeline.run(records=[doc])
    entity_labels = {e.label for e in result.entities}
    assert "DL-4C-9901" in entity_labels
    assert "Okhla Industrial Area" in entity_labels


# ---------------------------------------------------------------------
# 7. Relationship Extraction Reaches Final Output
# ---------------------------------------------------------------------
def test_relationship_extraction_reaches_final_output(pipeline: IntelligencePipeline):
    doc = DocumentRecord(
        source_id="FIR-001",
        document_type="POLICE_REPORT",
        raw_text="Accused identified as Sameer Khan S/o Ahmed Khan was found in possession of phone +919811010007.",
        file_path="inline_document",
        file_name="fir_001.txt",
    )
    result = pipeline.run(records=[doc])
    assert any(r.type == RelationshipType.USES_PHONE for r in result.relationships)


# ---------------------------------------------------------------------
# 8. Entity Resolution Changes Endpoints Correctly
# ---------------------------------------------------------------------
def test_entity_resolution_endpoint_rewriting(pipeline: IntelligencePipeline):
    # Two documents referencing Arjun Verma across different incidents
    doc1 = DocumentRecord(
        source_id="FIR-A",
        document_type="POLICE_REPORT",
        raw_text="Accused identified as Arjun Verma S/o Ramesh Verma was observed using phone +919811010006.",
        file_path="inline_document",
        file_name="fir_a.txt",
    )
    doc2 = DocumentRecord(
        source_id="FIR-B",
        document_type="POLICE_REPORT",
        raw_text="Accused identified as Arjun Verma S/o Ramesh Verma was intercepted driving truck DL-1M-4412.",
        file_path="inline_document",
        file_name="fir_b.txt",
    )

    result = pipeline.run(records=[doc1, doc2])
    arjun_entities = [e for e in result.entities if e.label == "Arjun Verma" and e.type == EntityType.PERSON]
    assert len(arjun_entities) == 1
    canonical_person = arjun_entities[0]
    assert "FIR-A" in canonical_person.source_records
    assert "FIR-B" in canonical_person.source_records

    # Verify that relationship uses canonical person ID
    uses_phone_rel = [r for r in result.relationships if r.type == RelationshipType.USES_PHONE and r.source == canonical_person.id][0]
    operates_rel = [r for r in result.relationships if r.type == RelationshipType.OPERATES and r.source == canonical_person.id][0]
    assert uses_phone_rel.source == operates_rel.source == canonical_person.id


# ---------------------------------------------------------------------
# 9. Anomalies Reach Final Output
# ---------------------------------------------------------------------
def test_anomalies_reach_final_output(pipeline: IntelligencePipeline):
    # Create an extreme transaction spike
    txs = [
        TransactionRecord(
            transaction_id=f"TX_{i}",
            sender_account_raw="ACC-NORM",
            sender_account_normalized="ACC-NORM",
            receiver_account_raw="ACC-RCV",
            receiver_account_normalized="ACC-RCV",
            amount=50000.0,
            currency="INR",
            timestamp_raw="2026-03-01T10:00:00Z",
            payment_channel="NEFT",
            row_index=i + 1,
        )
        for i in range(10)
    ]
    spike = TransactionRecord(
        transaction_id="TX_SPIKE",
        sender_account_raw="ACC-SPIKE",
        sender_account_normalized="ACC-SPIKE",
        receiver_account_raw="ACC-RCV",
        receiver_account_normalized="ACC-RCV",
        amount=10000000.0,
        currency="INR",
        timestamp_raw="2026-03-02T10:00:00Z",
        payment_channel="RTGS",
        row_index=11,
    )
    result = pipeline.run(records=txs + [spike])
    assert len(result.anomalies) >= 1
    assert any(a.anomaly_type.value == "HIGH_TRANSACTION_AMOUNT" for a in result.anomalies)


# ---------------------------------------------------------------------
# 10. Provenance Survives All Stages
# ---------------------------------------------------------------------
def test_provenance_survives_all_stages(pipeline: IntelligencePipeline):
    cdr = CDRRecord(
        call_id="CDR-PROV-999",
        caller_raw="+919811010001",
        caller_normalized="+919811010001",
        receiver_raw="+919811010002",
        receiver_normalized="+919811010002",
        timestamp_raw="2026-03-01T12:00:00Z",
        duration_sec=120,
        call_type="VOICE",
        cell_tower_id="TOWER_PROV",
        row_index=1,
    )
    result = pipeline.run(records=[cdr])
    assert len(result.relationships) == 1
    rel = result.relationships[0]
    assert rel.provenance.source_id == "CDR-PROV-999"
    assert rel.provenance.source_type == "TELECOM_CDR"
    assert rel.provenance.confidence == 1.0


# ---------------------------------------------------------------------
# 11. Deterministic Repeated Execution
# ---------------------------------------------------------------------
def test_deterministic_repeated_execution(pipeline: IntelligencePipeline):
    text = "Suspect Arjun Verma operated truck DL-1M-4412 with phone +919811010006."
    res1 = pipeline.run(records=[text])
    res2 = pipeline.run(records=[text])

    assert len(res1.entities) == len(res2.entities)
    for e1, e2 in zip(res1.entities, res2.entities):
        assert e1.id == e2.id
        assert e1.label == e2.label
        assert e1.type == e2.type

    assert len(res1.relationships) == len(res2.relationships)
    for r1, r2 in zip(res1.relationships, res2.relationships):
        assert r1.id == r2.id
        assert r1.source == r2.source
        assert r1.target == r2.target


# ---------------------------------------------------------------------
# 12. Malformed Record Handling
# ---------------------------------------------------------------------
def test_malformed_record_handling(pipeline: IntelligencePipeline):
    # Pass mixed valid and malformed dict records
    valid_tx = {
        "transaction_id": "TX_VALID",
        "sender_account": "ACC-VALID",
        "receiver_account": "ACC-RCV",
        "amount": 250000.0,
        "payment_channel": "RTGS",
    }
    malformed_record = {"completely": "unrecognized", "junk": 12345}

    result = pipeline.run(records=[valid_tx, malformed_record])
    assert result.pipeline_metadata.status == "PARTIAL"
    assert len(result.entities) >= 1


# ---------------------------------------------------------------------
# 13. Missing spaCy Does Not Break Pipeline
# ---------------------------------------------------------------------
def test_missing_spacy_fallback(pipeline: IntelligencePipeline):
    # Explicitly verify use_spacy=False works seamlessly
    p_fallback = IntelligencePipeline(use_spacy=False)
    text = "Suspect identified as Tariq Sheikh S/o Abdul Sheikh was apprehended at Chandni Chowk."
    res = p_fallback.run(records=[text])
    assert len(res.entities) >= 1
    assert any(e.label == "Tariq Sheikh" for e in res.entities)


# ---------------------------------------------------------------------
# 14. JSON Serialization
# ---------------------------------------------------------------------
def test_json_serialization(pipeline: IntelligencePipeline):
    text = "Arjun Verma drove truck DL-1M-4412."
    result = pipeline.run(records=[text])

    json_str = result.to_json()
    assert isinstance(json_str, str)
    parsed = json.loads(json_str)
    assert "entities" in parsed
    assert "relationships" in parsed
    assert "anomalies" in parsed
    assert "pipeline_metadata" in parsed


# ---------------------------------------------------------------------
# 15. Final Output Satisfies Canonical Schemas
# ---------------------------------------------------------------------
def test_output_satisfies_canonical_schemas(pipeline: IntelligencePipeline):
    fir = "Suspect Vikramaditya Singhania operates Astra Logistics Ltd with phone +919811010001."
    res = pipeline.run(records=[fir])

    for e in res.entities:
        assert isinstance(e, Entity)
        assert 0.0 <= e.risk_score <= 100.0
        assert e.id.strip() != ""
        assert e.label.strip() != ""

    for r in res.relationships:
        assert isinstance(r, Relationship)
        assert r.source != r.target
        assert 0.0 <= r.provenance.confidence <= 1.0


# ---------------------------------------------------------------------
# 16. Full End-to-End Integration Test (FIR + CDR + TX)
# ---------------------------------------------------------------------
def test_full_chain_integration(pipeline: IntelligencePipeline):
    # 1. FIR Police Narrative
    fir_text = (
        "Police Report FIR-101/2026:\n"
        "Suspect Rajesh Kumar managed dispatch operations for Astra Logistics Ltd.\n"
        "Kumar was observed communicating with handler Tariq Sheikh using phone +919811010003."
    )

    # 2. CDR Telecom Record
    cdr = CDRRecord(
        call_id="CDR-INT-101",
        caller_raw="+919811010003",
        caller_normalized="+919811010003",
        receiver_raw="+919811010002",
        receiver_normalized="+919811010002",
        timestamp_raw="2026-03-01T14:00:00Z",
        duration_sec=320,
        call_type="VOICE",
        cell_tower_id="TOWER_OKHLA",
        row_index=1,
    )

    # 3. Financial Transaction Records
    txs = [
        TransactionRecord(
            transaction_id=f"TX_INT_{i}",
            sender_account_raw="ACC-ASTRA-7701",
            sender_account_normalized="ACC-ASTRA-7701",
            receiver_account_raw=f"ACC-RCV-{i}",
            receiver_account_normalized=f"ACC-RCV-{i}",
            amount=100000.0 * (i + 1),
            currency="INR",
            timestamp_raw="2026-03-01T10:00:00Z",
            payment_channel="RTGS",
            row_index=i + 1,
        )
        for i in range(5)
    ]
    spike_tx = TransactionRecord(
        transaction_id="TX_INT_OUTLIER",
        sender_account_raw="ACC-ASTRA-7701",
        sender_account_normalized="ACC-ASTRA-7701",
        receiver_account_raw="ACC-SHEIKH-4401",
        receiver_account_normalized="ACC-SHEIKH-4401",
        amount=8500000.0,
        currency="INR",
        timestamp_raw="2026-03-02T16:00:00Z",
        payment_channel="RTGS",
        row_index=6,
    )

    result = pipeline.run(records=[fir_text, cdr] + txs + [spike_tx])

    # Assert complete chain executed
    assert result.pipeline_metadata.records_processed == 8
    assert len(result.entities) >= 5
    assert len(result.relationships) >= 3
    assert len(result.anomalies) >= 1
    assert result.pipeline_metadata.status == "SUCCESS"

    # Verify provenance preserved throughout
    for r in result.relationships:
        assert r.provenance.source_id != ""
        assert r.provenance.snippet != ""
