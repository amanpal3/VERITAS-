"""
VERITAS - Unit & Regression Tests for Relationship Extraction Layer
Validates all 12 approved relationship types, CDR call mapping, transaction fund flows,
textual semantic extraction, provenance attribution, confidence boundaries,
deterministic ID generation, duplicate suppression, and negative/weak context rejection.
"""
from pathlib import Path
import pytest
from pydantic import ValidationError

from ai.extraction.ner import EntityExtractor
from ai.extraction.relation_extractor import RelationshipExtractor, RelationshipIDGenerator
from ai.ingestion.csv_parser import CDRRecord, TransactionRecord
from ai.ingestion.document_parser import DocumentParser, DocumentRecord
from ai.schemas.entity import Entity, EntityType
from ai.schemas.relationship import Provenance, Relationship, RelationshipType

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DEMO_DIR = ROOT_DIR / "data" / "demo"
FIRS_DIR = DEMO_DIR / "firs"


@pytest.fixture
def extractor():
    return RelationshipExtractor()


# Helper to mock entities
def make_entity(eid: str, label: str, etype: EntityType, aliases=None) -> Entity:
    return Entity(
        id=eid,
        type=etype,
        label=label,
        name=label,
        aliases=aliases or [],
        risk_score=75.0,
    )


# =====================================================================
# 1. CDR -> CALLED
# =====================================================================
def test_cdr_called_extraction(extractor):
    """Verify Phone -> CALLED -> Phone relationship from a CDRRecord."""
    cdr = CDRRecord(
        call_id="CDR1001",
        caller_raw="+919811010001",
        caller_normalized="+919811010001",
        receiver_raw="+919811010002",
        receiver_normalized="+919811010002",
        timestamp_raw="2026-03-01T14:22:10Z",
        normalized_timestamp="2026-03-01T14:22:10Z",
        duration_sec=420,
        call_type="VOICE",
        cell_tower_id="TOWER_CP_01",
        row_index=2,
    )
    p1 = make_entity("PH001", "+919811010001", EntityType.PHONE)
    p2 = make_entity("PH002", "+919811010002", EntityType.PHONE)

    rels = extractor.extract_from_record(cdr, entities=[p1, p2])
    assert len(rels) == 1
    r = rels[0]
    assert r.type == RelationshipType.CALLED
    assert r.source == "PH001"
    assert r.target == "PH002"
    assert r.provenance.source_id == "CDR1001"
    assert r.provenance.source_type == "TELECOM_CDR"
    assert r.provenance.confidence == 1.0


# =====================================================================
# 2. Transaction -> TRANSACTED_WITH
# =====================================================================
def test_transaction_transacted_with(extractor):
    """Verify BankAccount -> TRANSACTED_WITH -> BankAccount from a TransactionRecord."""
    tx = TransactionRecord(
        transaction_id="TX1006",
        sender_account_raw="ACC-ASTRA-7701",
        sender_account_normalized="ACC-ASTRA-7701",
        receiver_account_raw="ACC-SHEIKH-4401",
        receiver_account_normalized="ACC-SHEIKH-4401",
        amount=850000.0,
        currency="INR",
        timestamp_raw="2026-02-25T11:00:00Z",
        normalized_timestamp="2026-02-25T11:00:00Z",
        payment_channel="RTGS",
        reference_note="Settlement",
        row_index=7,
    )
    b1 = make_entity("BA002", "ACC-ASTRA-7701", EntityType.BANK_ACCOUNT)
    b2 = make_entity("BA003", "ACC-SHEIKH-4401", EntityType.BANK_ACCOUNT)

    rels = extractor.extract_from_record(tx, entities=[b1, b2])
    assert len(rels) == 1
    r = rels[0]
    assert r.type == RelationshipType.TRANSACTED_WITH
    assert r.source == "BA002"
    assert r.target == "BA003"
    assert r.weight == 850000.0
    assert r.provenance.source_id == "TX1006"
    assert r.provenance.source_type == "BANK_LEDGER"
    assert r.provenance.confidence == 1.0


# =====================================================================
# 3. USES_PHONE Extraction
# =====================================================================
def test_uses_phone_extraction(extractor):
    """Verify Person -> USES_PHONE -> Phone extraction from document text."""
    text = "Under interrogation, accused Arjun Verma was found in possession of a smartphone (MSISDN: +919811010006)."
    doc = DocumentRecord(
        source_id="FIR-104/2026",
        file_path="firs/FIR_001.txt",
        file_name="FIR_001.txt",
        document_type="POLICE_REPORT",
        title="FIR 104",
        raw_text=text,
    )
    p = make_entity("P006", "Arjun Verma", EntityType.PERSON)
    ph = make_entity("PH006", "+919811010006", EntityType.PHONE)

    rels = extractor.extract_from_record(doc, entities=[p, ph])
    assert any(r.type == RelationshipType.USES_PHONE and r.source == "P006" and r.target == "PH006" for r in rels)


# =====================================================================
# 4. OWNS Extraction
# =====================================================================
def test_owns_vehicle_extraction(extractor):
    """Verify Person -> OWNS -> Vehicle extraction from document text."""
    text = "Surveillance observed the luxury sedan DL-1C-0001 registered to Vikramaditya Singhania."
    doc = DocumentRecord(
        source_id="SURV-031",
        file_path="test.txt",
        file_name="test.txt",
        document_type="SURVEILLANCE",
        title="Surveillance",
        raw_text=text,
    )
    p = make_entity("P001", "Vikramaditya Singhania", EntityType.PERSON)
    v = make_entity("V001", "DL-1C-0001", EntityType.VEHICLE)

    rels = extractor.extract_from_record(doc, entities=[p, v])
    assert any(r.type == RelationshipType.OWNS and r.source == "P001" and r.target == "V001" for r in rels)


# =====================================================================
# 5. OPERATES Extraction
# =====================================================================
def test_operates_vehicle_extraction(extractor):
    """Verify Person -> OPERATES -> Vehicle extraction."""
    text = "Police intercepted commercial transport truck DL-1M-4412 driven by Arjun Verma."
    doc = DocumentRecord(
        source_id="FIR-104",
        file_path="test.txt",
        file_name="test.txt",
        document_type="POLICE_REPORT",
        title="Intercept",
        raw_text=text,
    )
    p = make_entity("P006", "Arjun Verma", EntityType.PERSON)
    v = make_entity("V004", "DL-1M-4412", EntityType.VEHICLE)

    rels = extractor.extract_from_record(doc, entities=[p, v])
    assert any(r.type == RelationshipType.OPERATES and r.source == "P006" and r.target == "V004" for r in rels)


# =====================================================================
# 6. LOCATED_AT Extraction
# =====================================================================
def test_located_at_extraction(extractor):
    """Verify Person -> LOCATED_AT -> Location extraction."""
    text = "Rajesh Kumar was observed present inside the warehouse at Okhla Industrial Area."
    doc = DocumentRecord(
        source_id="SURV-031",
        file_path="test.txt",
        file_name="test.txt",
        document_type="SURVEILLANCE",
        title="Obs",
        raw_text=text,
    )
    p = make_entity("P003", "Rajesh Kumar", EntityType.PERSON)
    loc = make_entity("LOC001", "Okhla Industrial Area", EntityType.LOCATION)

    rels = extractor.extract_from_record(doc, entities=[p, loc])
    assert any(r.type == RelationshipType.LOCATED_AT and r.source == "P003" and r.target == "LOC001" for r in rels)


# =====================================================================
# 7. ASSOCIATED_WITH Extraction
# =====================================================================
def test_associated_with_extraction(extractor):
    """Verify criminal association between suspects."""
    text = "A secret closed-door meeting occurred between Vikramaditya Singhania and Tariq Sheikh behind shuttered glass."
    doc = DocumentRecord(
        source_id="SURV-031",
        file_path="test.txt",
        file_name="test.txt",
        document_type="SURVEILLANCE",
        title="Meeting",
        raw_text=text,
    )
    p1 = make_entity("P001", "Vikramaditya Singhania", EntityType.PERSON)
    p2 = make_entity("P002", "Tariq Sheikh", EntityType.PERSON)

    rels = extractor.extract_from_record(doc, entities=[p1, p2])
    assert any(r.type == RelationshipType.ASSOCIATED_WITH for r in rels)


# =====================================================================
# 8. SUPERVISES Extraction
# =====================================================================
def test_supervises_extraction(extractor):
    """Verify hierarchical handler -> courier relationship."""
    text = "Arjun Verma stated that the cargo was received from immediate handler Rajesh Kumar."
    doc = DocumentRecord(
        source_id="FIR-104",
        file_path="test.txt",
        file_name="test.txt",
        document_type="POLICE_REPORT",
        title="Handler",
        raw_text=text,
    )
    p1 = make_entity("P006", "Arjun Verma", EntityType.PERSON)
    p2 = make_entity("P003", "Rajesh Kumar", EntityType.PERSON)

    rels = extractor.extract_from_record(doc, entities=[p1, p2])
    assert any(r.type == RelationshipType.SUPERVISES and r.source == "P003" and r.target == "P006" for r in rels)


# =====================================================================
# 9. COORDINATES_WITH Extraction
# =====================================================================
def test_coordinates_with_extraction(extractor):
    """Verify operational coordination between cell members."""
    text = "Kabir Mirza maintained frequent phone coordination with logistics coordinator Rajesh Kumar."
    doc = DocumentRecord(
        source_id="INT-409",
        file_path="test.txt",
        file_name="test.txt",
        document_type="SURVEILLANCE",
        title="Coordination",
        raw_text=text,
    )
    p1 = make_entity("P004", "Kabir Mirza", EntityType.PERSON)
    p2 = make_entity("P003", "Rajesh Kumar", EntityType.PERSON)

    rels = extractor.extract_from_record(doc, entities=[p1, p2])
    assert any(r.type == RelationshipType.COORDINATES_WITH for r in rels)


# =====================================================================
# 10. CONTROLS Extraction
# =====================================================================
def test_controls_extraction(extractor):
    """Verify corporate beneficial ownership."""
    text = "Vikramaditya Singhania is the primary beneficial owner who controls Astra Logistics Ltd."
    doc = DocumentRecord(
        source_id="FIN-092",
        file_path="test.txt",
        file_name="test.txt",
        document_type="AUDIT",
        title="Control",
        raw_text=text,
    )
    p = make_entity("P001", "Vikramaditya Singhania", EntityType.PERSON)
    org = make_entity("ORG001", "Astra Logistics Ltd", EntityType.ORGANIZATION)

    rels = extractor.extract_from_record(doc, entities=[p, org])
    assert any(r.type == RelationshipType.CONTROLS and r.source == "P001" and r.target == "ORG001" for r in rels)


# =====================================================================
# 11. MEMBER_OF Extraction
# =====================================================================
def test_member_of_extraction(extractor):
    """Verify corporate directorship / membership."""
    text = "Anita Roy serves as Managing Director of Astra Logistics Ltd holding 70% equity."
    doc = DocumentRecord(
        source_id="FIN-092",
        file_path="test.txt",
        file_name="test.txt",
        document_type="AUDIT",
        title="Director",
        raw_text=text,
    )
    p = make_entity("P005", "Anita Roy", EntityType.PERSON)
    org = make_entity("ORG001", "Astra Logistics Ltd", EntityType.ORGANIZATION)

    rels = extractor.extract_from_record(doc, entities=[p, org])
    assert any(r.type == RelationshipType.MEMBER_OF and r.source == "P005" and r.target == "ORG001" for r in rels)


# =====================================================================
# 12. OWNS_ACCOUNT Extraction
# =====================================================================
def test_owns_account_extraction(extractor):
    """Verify Person or Org -> OWNS_ACCOUNT -> BankAccount extraction."""
    text = "Astra Logistics Ltd maintains corporate bank account ACC-ASTRA-7701 for fund layering."
    doc = DocumentRecord(
        source_id="FIN-092",
        file_path="test.txt",
        file_name="test.txt",
        document_type="AUDIT",
        title="Account",
        raw_text=text,
    )
    org = make_entity("ORG001", "Astra Logistics Ltd", EntityType.ORGANIZATION)
    acc = make_entity("BA002", "ACC-ASTRA-7701", EntityType.BANK_ACCOUNT)

    rels = extractor.extract_from_record(doc, entities=[org, acc])
    assert any(r.type == RelationshipType.OWNS_ACCOUNT and r.source == "ORG001" and r.target == "BA002" for r in rels)


# =====================================================================
# 13. Provenance Integrity
# =====================================================================
def test_relationship_provenance(extractor):
    """Verify all extracted relationships retain source citations and snippets."""
    text = "Under interrogation, accused Arjun Verma was found in possession of smartphone +919811010006."
    doc = DocumentRecord(
        source_id="FIR-104/2026",
        file_path="test.txt",
        file_name="test.txt",
        document_type="POLICE_REPORT",
        title="Test",
        raw_text=text,
    )
    p = make_entity("P006", "Arjun Verma", EntityType.PERSON)
    ph = make_entity("PH006", "+919811010006", EntityType.PHONE)

    rels = extractor.extract_from_record(doc, entities=[p, ph])
    for r in rels:
        assert r.provenance.source_id == "FIR-104/2026"
        assert r.provenance.source_type == "POLICE_REPORT"
        assert "Arjun Verma" in r.provenance.snippet
        assert "+919811010006" in r.provenance.snippet


# =====================================================================
# 14. Confidence Range
# =====================================================================
def test_relationship_confidence_range(extractor):
    """Verify confidence values are strictly within [0.0, 1.0]."""
    text = "Police observed Kabir Mirza driving Mahindra Scorpio DL-4C-9901."
    doc = DocumentRecord(
        source_id="INT-409",
        file_path="test.txt",
        file_name="test.txt",
        document_type="SURVEILLANCE",
        title="Test",
        raw_text=text,
    )
    p = make_entity("P004", "Kabir Mirza", EntityType.PERSON)
    v = make_entity("V003", "DL-4C-9901", EntityType.VEHICLE)

    rels = extractor.extract_from_record(doc, entities=[p, v])
    for r in rels:
        assert 0.0 <= r.provenance.confidence <= 1.0


# =====================================================================
# 15. Deterministic Relationship IDs
# =====================================================================
def test_deterministic_relationship_ids():
    """Verify identical events yield stable IDs."""
    gen1 = RelationshipIDGenerator(start_idx=1)
    id1 = gen1.get_id("FIR-104", "P006", "PH006", RelationshipType.USES_PHONE)
    id2 = gen1.get_id("FIR-104", "P006", "PH006", RelationshipType.USES_PHONE)
    assert id1 == id2 == "R001"

    id3 = gen1.get_id("FIR-104", "P006", "V004", RelationshipType.OPERATES)
    assert id3 == "R002"


# =====================================================================
# 16. Duplicate Suppression Within Single Document
# =====================================================================
def test_duplicate_suppression_within_document(extractor):
    """Verify that multiple mentions of the same relationship in one document emit only 1 edge."""
    text = (
        "Arjun Verma was driving DL-1M-4412.\n"
        "Later that night, the driver Arjun Verma was confirmed driving vehicle DL-1M-4412."
    )
    doc = DocumentRecord(
        source_id="FIR-104",
        file_path="test.txt",
        file_name="test.txt",
        document_type="POLICE_REPORT",
        title="Test",
        raw_text=text,
    )
    p = make_entity("P006", "Arjun Verma", EntityType.PERSON)
    v = make_entity("V004", "DL-1M-4412", EntityType.VEHICLE)

    rels = extractor.extract_from_record(doc, entities=[p, v])
    operates_rels = [r for r in rels if r.type == RelationshipType.OPERATES and r.source == "P006" and r.target == "V004"]
    assert len(operates_rels) == 1


# =====================================================================
# 17. Preservation of Distinct CDR Events
# =====================================================================
def test_preservation_of_distinct_cdr_events(extractor):
    """Verify that separate CDR call records between the same phones are both preserved."""
    cdr1 = CDRRecord(
        call_id="CDR1001",
        caller_raw="+919811010001",
        caller_normalized="+919811010001",
        receiver_raw="+919811010002",
        receiver_normalized="+919811010002",
        timestamp_raw="2026-03-01T14:22:10Z",
        duration_sec=420,
        call_type="VOICE",
        cell_tower_id="T1",
        row_index=2,
    )
    cdr2 = CDRRecord(
        call_id="CDR1002",
        caller_raw="+919811010001",
        caller_normalized="+919811010001",
        receiver_raw="+919811010002",
        receiver_normalized="+919811010002",
        timestamp_raw="2026-03-02T16:45:00Z",
        duration_sec=185,
        call_type="VOICE",
        cell_tower_id="T2",
        row_index=3,
    )
    p1 = make_entity("PH001", "+919811010001", EntityType.PHONE)
    p2 = make_entity("PH002", "+919811010002", EntityType.PHONE)

    rels = extractor.extract([cdr1, cdr2], entities=[p1, p2])
    assert len(rels) == 2
    assert rels[0].id != rels[1].id
    assert rels[0].provenance.source_id == "CDR1001"
    assert rels[1].provenance.source_id == "CDR1002"


# =====================================================================
# 18. Preservation of Distinct Transaction Events
# =====================================================================
def test_preservation_of_distinct_transaction_events(extractor):
    """Verify that separate financial transactions between the same accounts are preserved."""
    tx1 = TransactionRecord(
        transaction_id="TX1001",
        sender_account_raw="ACC-POOL",
        sender_account_normalized="ACC-POOL",
        receiver_account_raw="ACC-ASTRA",
        receiver_account_normalized="ACC-ASTRA",
        amount=195000.0,
        currency="INR",
        timestamp_raw="2026-02-15T11:20:00Z",
        payment_channel="CASH_DEPOSIT",
        reference_note="Tranche 1",
        row_index=2,
    )
    tx2 = TransactionRecord(
        transaction_id="TX1002",
        sender_account_raw="ACC-POOL",
        sender_account_normalized="ACC-POOL",
        receiver_account_raw="ACC-ASTRA",
        receiver_account_normalized="ACC-ASTRA",
        amount=195000.0,
        currency="INR",
        timestamp_raw="2026-02-16T14:10:00Z",
        payment_channel="CASH_DEPOSIT",
        reference_note="Tranche 2",
        row_index=3,
    )
    b1 = make_entity("BA001", "ACC-POOL", EntityType.BANK_ACCOUNT)
    b2 = make_entity("BA002", "ACC-ASTRA", EntityType.BANK_ACCOUNT)

    rels = extractor.extract([tx1, tx2], entities=[b1, b2])
    assert len(rels) == 2
    assert rels[0].id != rels[1].id
    assert rels[0].provenance.source_id == "TX1001"
    assert rels[1].provenance.source_id == "TX1002"


# =====================================================================
# 19. Invalid Relationship Type Rejection
# =====================================================================
def test_invalid_relationship_type_rejection():
    """Verify that unapproved verbs (e.g. WORKS_FOR, PAID, MESSAGED) are rejected."""
    with pytest.raises(ValidationError):
        Relationship(
            id="R999",
            source="P001",
            target="P002",
            type="PAID",  # Disallowed
            provenance=Provenance(source_id="T1", source_type="DOC", snippet="Paid", confidence=0.9),
        )


# =====================================================================
# 20. Weak Textual Evidence Does Not Create Speculative Edges
# =====================================================================
def test_weak_textual_evidence_rejection(extractor):
    """Verify that mere co-occurrence in a sentence without syntactic action creates NO relationship."""
    text = "The weather was cold in Singhu Border while Arjun Verma had tea."
    doc = DocumentRecord(
        source_id="TEST-WEAK",
        file_path="test.txt",
        file_name="test.txt",
        document_type="POLICE_REPORT",
        title="Weak",
        raw_text=text,
    )
    p = make_entity("P006", "Arjun Verma", EntityType.PERSON)
    v = make_entity("V004", "DL-1M-4412", EntityType.VEHICLE)
    org = make_entity("ORG001", "Astra Logistics Ltd", EntityType.ORGANIZATION)

    rels = extractor.extract_from_record(doc, entities=[p, v, org])
    # No operates, owns, or controls should be extracted
    assert len(rels) == 0
