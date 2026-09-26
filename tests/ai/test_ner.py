"""
VERITAS - Unit & Regression Tests for Hybrid Named Entity Recognition (NER) Layer
Covers all 6 entity types, deterministic regex extraction, spaCy fallback behavior,
provenance preservation, confidence scoring, stable ID generation, duplicate suppression,
and numeric false-positive rejection.
"""
from pathlib import Path
import pytest

from ai.extraction.ner import EntityExtractor, EntityIDGenerator
from ai.ingestion.csv_parser import CDRRecord, TransactionRecord
from ai.ingestion.document_parser import DocumentParser, DocumentRecord
from ai.schemas.entity import Entity, EntityType

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DEMO_DIR = ROOT_DIR / "data" / "demo"
FIRS_DIR = DEMO_DIR / "firs"


@pytest.fixture
def extractor():
    """Provides an EntityExtractor instance with fallback capability."""
    return EntityExtractor(use_spacy=True)


# =====================================================================
# 1. Person Extraction Tests
# =====================================================================
def test_person_extraction(extractor):
    """Verify extraction of suspect names and aliases from police reports."""
    doc = DocumentParser.parse_file(FIRS_DIR / "FIR_001_Smuggling_Bust.txt")
    entities = extractor.extract_from_record(doc)

    persons = [e for e in entities if e.type == EntityType.PERSON]
    assert len(persons) >= 2

    person_names = {p.label for p in persons}
    assert "Arjun Verma" in person_names
    assert "Rajesh Kumar" in person_names

    # Verify alias capture for Rajesh Kumar ("Raju Swift")
    rajesh = next(p for p in persons if p.label == "Rajesh Kumar")
    assert "Raju Swift" in rajesh.aliases


# =====================================================================
# 2. Location Extraction Tests
# =====================================================================
def test_location_extraction(extractor):
    """Verify extraction of transit hubs, checkpoints, and safehouses."""
    doc = DocumentParser.parse_file(FIRS_DIR / "FIR_001_Smuggling_Bust.txt")
    entities = extractor.extract_from_record(doc)

    locations = [e for e in entities if e.type == EntityType.LOCATION]
    loc_names = {l.label for l in locations}

    assert "Singhu Border" in loc_names
    assert "Okhla Industrial Area" in loc_names


# =====================================================================
# 3. Organization Extraction Tests
# =====================================================================
def test_organization_extraction(extractor):
    """Verify extraction of shell companies, front entities, and agencies."""
    doc = DocumentParser.parse_file(FIRS_DIR / "FIR_002_Hawala_Raid.txt")
    entities = extractor.extract_from_record(doc)

    orgs = [e for e in entities if e.type == EntityType.ORGANIZATION]
    org_names = {o.label for o in orgs}

    assert "Sheikh Trading Enterprises" in org_names
    assert "Astra Logistics Ltd" in org_names


# =====================================================================
# 4. Phone Extraction Tests
# =====================================================================
def test_phone_extraction(extractor):
    """Verify deterministic phone extraction with E.164 normalization."""
    doc = DocumentParser.parse_file(FIRS_DIR / "FIR_001_Smuggling_Bust.txt")
    entities = extractor.extract_from_record(doc)

    phones = [e for e in entities if e.type == EntityType.PHONE]
    phone_numbers = {p.label for p in phones}

    assert "+919811010003" in phone_numbers
    assert "+919811010006" in phone_numbers


# =====================================================================
# 5. Vehicle Extraction Tests
# =====================================================================
def test_vehicle_extraction(extractor):
    """Verify deterministic vehicle registration extraction."""
    doc = DocumentParser.parse_file(FIRS_DIR / "FIR_001_Smuggling_Bust.txt")
    entities = extractor.extract_from_record(doc)

    vehicles = [e for e in entities if e.type == EntityType.VEHICLE]
    assert len(vehicles) >= 1

    truck = next(v for v in vehicles if "DL-1M-4412" in v.label)
    assert truck.type == EntityType.VEHICLE
    assert truck.attributes.get("source_id") == "FIR-104/2026"


# =====================================================================
# 6. Bank Account Extraction Tests
# =====================================================================
def test_bank_account_extraction(extractor):
    """Verify deterministic account identifier extraction."""
    doc = DocumentParser.parse_file(FIRS_DIR / "FIR_002_Hawala_Raid.txt")
    entities = extractor.extract_from_record(doc)

    accounts = [e for e in entities if e.type == EntityType.BANK_ACCOUNT]
    acc_labels = {a.label for a in accounts}

    assert "ACC-ASTRA-7701" in acc_labels
    assert "ACC-SINGH-9901" in acc_labels


# =====================================================================
# 7. Normalization Integration Tests
# =====================================================================
def test_normalization_integration(extractor):
    """Verify extracted entities pass through deterministic normalizers."""
    text = "Suspect phone 09811010003 with vehicle dl 1m 4412 and account acc_astra_7701"
    entities = extractor.extract_from_text(text, source_id="TEST-01")

    p = next(e for e in entities if e.type == EntityType.PHONE)
    assert p.label == "+919811010003"

    v = next(e for e in entities if e.type == EntityType.VEHICLE)
    assert v.label == "DL-1M-4412"

    a = next(e for e in entities if e.type == EntityType.BANK_ACCOUNT)
    assert a.label == "ACC-ASTRA-7701"


# =====================================================================
# 8. Stable Entity ID Tests
# =====================================================================
def test_stable_ids(extractor):
    """Verify predictable and stable IDs across repeated extractions."""
    id_gen = EntityIDGenerator()
    id1 = id_gen.get_id(EntityType.PERSON, "Vikramaditya Singhania")
    id2 = id_gen.get_id(EntityType.PERSON, "Vikramaditya Singhania")
    assert id1 == id2 == "P001"

    id3 = id_gen.get_id(EntityType.PHONE, "+919811010001")
    assert id3 == "PH001"

    # Distinct entity gets distinct predictable ID
    id4 = id_gen.get_id(EntityType.PERSON, "Unknown Suspect X")
    assert id4 != id1
    assert id4.startswith("P")


# =====================================================================
# 9. Provenance Tests
# =====================================================================
def test_provenance(extractor):
    """Verify all entities retain source citations, original values, and sentence snippets."""
    doc = DocumentParser.parse_file(FIRS_DIR / "FIR_001_Smuggling_Bust.txt")
    entities = extractor.extract_from_record(doc)

    for ent in entities:
        assert ent.source_records == ["FIR-104/2026"]
        attrs = ent.attributes
        assert attrs.get("source_id") == "FIR-104/2026"
        assert attrs.get("source_type") == "POLICE_REPORT"
        assert "original_value" in attrs
        assert "snippet" in attrs
        assert len(attrs["snippet"]) > 0


# =====================================================================
# 10. Confidence Range Tests
# =====================================================================
def test_confidence_range(extractor):
    """Verify that confidence is strictly bounded between 0.0 and 1.0."""
    doc = DocumentParser.parse_file(FIRS_DIR / "FIR_001_Smuggling_Bust.txt")
    entities = extractor.extract_from_record(doc)

    for ent in entities:
        conf = ent.attributes.get("confidence")
        assert conf is not None
        assert 0.0 <= conf <= 1.0


# =====================================================================
# 11. Duplicate Suppression Within One Document
# =====================================================================
def test_duplicate_suppression_within_document(extractor):
    """Verify that multiple mentions in a single document produce only 1 Entity with merged occurrences."""
    doc = DocumentParser.parse_file(FIRS_DIR / "FIR_001_Smuggling_Bust.txt")
    entities = extractor.extract_from_record(doc)

    # Count occurrences of Rajesh Kumar
    rajesh_entities = [e for e in entities if e.label == "Rajesh Kumar"]
    assert len(rajesh_entities) == 1
    assert rajesh_entities[0].attributes.get("occurrences", 1) >= 2


# =====================================================================
# 12. Graceful Operation Without spaCy
# =====================================================================
def test_graceful_spacy_fallback():
    """Verify that extractor operates cleanly when spaCy is completely disabled."""
    fallback_extractor = EntityExtractor(use_spacy=False)
    doc = DocumentParser.parse_file(FIRS_DIR / "FIR_001_Smuggling_Bust.txt")
    entities = fallback_extractor.extract_from_record(doc)

    assert len(entities) > 0
    types = {e.type for e in entities}
    assert EntityType.PERSON in types
    assert EntityType.PHONE in types
    assert EntityType.VEHICLE in types
    assert EntityType.LOCATION in types


# =====================================================================
# 13. False-Positive Numeric Rejection Tests
# =====================================================================
def test_false_positive_numeric_rejection(extractor):
    """Verify that standard numbers (weights, amounts, ages) are not misidentified as phones or accounts."""
    text = "Seized 14 kg contraband. Accused Age 28. Paid INR 50,000 cash. Confiscated INR 48,00,000 across 12.4 Crores."
    entities = extractor.extract_from_text(text, source_id="TEST-NUM")

    phones = [e for e in entities if e.type == EntityType.PHONE]
    accounts = [e for e in entities if e.type == EntityType.BANK_ACCOUNT]

    assert len(phones) == 0
    assert len(accounts) == 0


# =====================================================================
# 14. Structured Record Extraction Tests (CDRs & Transactions)
# =====================================================================
def test_extract_from_cdr_record(extractor):
    """Verify phone entity extraction from CDR records."""
    cdr = CDRRecord(
        call_id="CDR1001",
        caller_raw="+91 98110 10001",
        caller_normalized="+919811010001",
        receiver_raw="9811010002",
        receiver_normalized="+919811010002",
        timestamp_raw="2026-03-01T14:22:10Z",
        normalized_timestamp="2026-03-01T14:22:10Z",
        duration_sec=420,
        call_type="VOICE",
        cell_tower_id="TOWER_CP_01",
        row_index=2,
    )
    entities = extractor.extract_from_record(cdr)
    assert len(entities) == 2
    assert all(e.type == EntityType.PHONE for e in entities)
    assert {e.label for e in entities} == {"+919811010001", "+919811010002"}


def test_extract_from_transaction_record(extractor):
    """Verify bank account entity extraction from Transaction records."""
    tx = TransactionRecord(
        transaction_id="TX1001",
        sender_account_raw="ACC-CASH-POOL",
        sender_account_normalized="ACC-CASH-POOL",
        receiver_account_raw="acc_astra_7701",
        receiver_account_normalized="ACC-ASTRA-7701",
        amount=195000.0,
        currency="INR",
        timestamp_raw="2026-02-15T11:20:00Z",
        normalized_timestamp="2026-02-15T11:20:00Z",
        payment_channel="CASH_DEPOSIT",
        reference_note="Advance",
        row_index=2,
    )
    entities = extractor.extract_from_record(tx)
    assert len(entities) == 2
    assert all(e.type == EntityType.BANK_ACCOUNT for e in entities)
    assert {e.label for e in entities} == {"ACC-CASH-POOL", "ACC-ASTRA-7701"}
