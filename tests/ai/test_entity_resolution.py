"""
VERITAS - Tests for AI Entity Resolution Layer
Validates multi-signal matching, conservative merging, canonical ID selection,
alias & provenance preservation, relationship rewriting, and rejection of false positives.
"""
import pytest
from typing import List

from ai.resolution.entity_resolver import EntityResolver, MatchDecision, ResolutionEvidence
from ai.resolution.similarity import (
    jaro_winkler_similarity,
    levenshtein_similarity,
    phonetic_match,
    soundex,
)
from ai.schemas.entity import Entity, EntityType
from ai.schemas.relationship import Provenance, Relationship, RelationshipType


@pytest.fixture
def resolver() -> EntityResolver:
    return EntityResolver()


# ---------------------------------------------------------------------
# 1. Exact Phone Matching
# ---------------------------------------------------------------------
def test_exact_phone_matching(resolver: EntityResolver):
    phone1 = Entity(
        id="PH001",
        type=EntityType.PHONE,
        label="+919811010001",
        risk_score=80.0,
        source_records=["FIR_001"],
    )
    phone2 = Entity(
        id="PH099",
        type=EntityType.PHONE,
        label="09811010001",  # Unnormalized / 0-prefixed version
        risk_score=75.0,
        source_records=["CDR1001"],
    )
    evidence = resolver.compare_candidates(phone1, phone2)
    assert evidence.decision == MatchDecision.MATCH
    assert evidence.score == 1.0
    assert any("phone number match" in r.lower() for r in evidence.reasons)


# ---------------------------------------------------------------------
# 2. Distinct Phone Rejection (No fuzzy matching)
# ---------------------------------------------------------------------
def test_distinct_phone_rejection(resolver: EntityResolver):
    phone1 = Entity(
        id="PH001",
        type=EntityType.PHONE,
        label="+919811010001",
        risk_score=80.0,
        source_records=["FIR_001"],
    )
    phone2 = Entity(
        id="PH002",
        type=EntityType.PHONE,
        label="+919811010002",  # Only 1 digit difference!
        risk_score=80.0,
        source_records=["CDR1002"],
    )
    evidence = resolver.compare_candidates(phone1, phone2)
    assert evidence.decision == MatchDecision.NO_MATCH
    assert evidence.score == 0.0


# ---------------------------------------------------------------------
# 3. Exact Vehicle Plate Matching
# ---------------------------------------------------------------------
def test_exact_vehicle_matching(resolver: EntityResolver):
    veh1 = Entity(
        id="V001",
        type=EntityType.VEHICLE,
        label="DL-1C-0001",
        risk_score=75.0,
        source_records=["FIR_001"],
    )
    veh2 = Entity(
        id="V099",
        type=EntityType.VEHICLE,
        label="DL 1C 0001 (BMW 7-Series)",
        risk_score=70.0,
        source_records=["SURV_LOG"],
    )
    evidence = resolver.compare_candidates(veh1, veh2)
    assert evidence.decision == MatchDecision.MATCH
    assert evidence.score == 1.0


# ---------------------------------------------------------------------
# 4. Distinct Vehicle Plate Rejection
# ---------------------------------------------------------------------
def test_distinct_vehicle_rejection(resolver: EntityResolver):
    veh1 = Entity(
        id="V001",
        type=EntityType.VEHICLE,
        label="DL-1C-0001",
        risk_score=75.0,
        source_records=["FIR_001"],
    )
    veh2 = Entity(
        id="V002",
        type=EntityType.VEHICLE,
        label="DL-3C-1234",
        risk_score=75.0,
        source_records=["SURV_LOG"],
    )
    evidence = resolver.compare_candidates(veh1, veh2)
    assert evidence.decision == MatchDecision.NO_MATCH
    assert evidence.score == 0.0


# ---------------------------------------------------------------------
# 5. Exact Bank Account Matching
# ---------------------------------------------------------------------
def test_exact_bank_account_matching(resolver: EntityResolver):
    acc1 = Entity(
        id="BA001",
        type=EntityType.BANK_ACCOUNT,
        label="ACC-SINGH-9901",
        risk_score=85.0,
        source_records=["TX_001"],
    )
    acc2 = Entity(
        id="BA099",
        type=EntityType.BANK_ACCOUNT,
        label="acc_singh_9901",  # Underscore & lowercase
        risk_score=80.0,
        source_records=["FIR_002"],
    )
    evidence = resolver.compare_candidates(acc1, acc2)
    assert evidence.decision == MatchDecision.MATCH
    assert evidence.score == 1.0


# ---------------------------------------------------------------------
# 6. Distinct Bank Account Rejection
# ---------------------------------------------------------------------
def test_distinct_bank_account_rejection(resolver: EntityResolver):
    acc1 = Entity(
        id="BA001",
        type=EntityType.BANK_ACCOUNT,
        label="ACC-SINGH-9901",
        risk_score=85.0,
        source_records=["TX_001"],
    )
    acc2 = Entity(
        id="BA002",
        type=EntityType.BANK_ACCOUNT,
        label="ACC-ASTRA-7701",
        risk_score=85.0,
        source_records=["TX_002"],
    )
    evidence = resolver.compare_candidates(acc1, acc2)
    assert evidence.decision == MatchDecision.NO_MATCH
    assert evidence.score == 0.0


# ---------------------------------------------------------------------
# 7. Exact Name Matching for Person
# ---------------------------------------------------------------------
def test_exact_person_name_matching(resolver: EntityResolver):
    p1 = Entity(
        id="P001",
        type=EntityType.PERSON,
        label="Vikramaditya Singhania",
        risk_score=95.0,
        source_records=["FIR_001"],
    )
    p2 = Entity(
        id="P099",
        type=EntityType.PERSON,
        label="vikramaditya singhania",
        risk_score=90.0,
        source_records=["FIR_002"],
    )
    evidence = resolver.compare_candidates(p1, p2)
    assert evidence.decision == MatchDecision.MATCH
    assert evidence.score == 1.0


# ---------------------------------------------------------------------
# 8. Person Alias Matching
# ---------------------------------------------------------------------
def test_person_alias_matching(resolver: EntityResolver):
    p1 = Entity(
        id="P001",
        type=EntityType.PERSON,
        label="Vikramaditya Singhania",
        aliases=["The Don", "Vikram"],
        risk_score=95.0,
        source_records=["FIR_001"],
    )
    p2 = Entity(
        id="P099",
        type=EntityType.PERSON,
        label="The Don",
        aliases=[],
        risk_score=85.0,
        source_records=["SURV_LOG"],
    )
    evidence = resolver.compare_candidates(p1, p2)
    assert evidence.decision == MatchDecision.MATCH
    assert evidence.score >= 0.90
    assert any("alias" in r.lower() for r in evidence.reasons)


# ---------------------------------------------------------------------
# 9. Conservative Matching: Surnames Only Non-Merge
# ---------------------------------------------------------------------
def test_conservative_person_surname_non_merge(resolver: EntityResolver):
    p1 = Entity(
        id="P003",
        type=EntityType.PERSON,
        label="Rajesh Kumar",
        risk_score=80.0,
        source_records=["FIR_001"],
    )
    p2 = Entity(
        id="P099",
        type=EntityType.PERSON,
        label="Rakesh Kumar",  # Same surname, different first name
        risk_score=75.0,
        source_records=["FIR_002"],
    )
    evidence = resolver.compare_candidates(p1, p2)
    # Must NOT merge without corroborating identifiers
    assert evidence.decision == MatchDecision.NO_MATCH
    assert any("distinct first names" in r.lower() for r in evidence.reasons)


# ---------------------------------------------------------------------
# 10. Generic Location Non-Merge
# ---------------------------------------------------------------------
def test_generic_location_non_merge(resolver: EntityResolver):
    loc1 = Entity(
        id="LOC001",
        type=EntityType.LOCATION,
        label="New Delhi",
        risk_score=70.0,
        source_records=["FIR_001"],
    )
    loc2 = Entity(
        id="LOC002",
        type=EntityType.LOCATION,
        label="Noida",
        risk_score=70.0,
        source_records=["FIR_002"],
    )
    evidence = resolver.compare_candidates(loc1, loc2)
    assert evidence.decision == MatchDecision.NO_MATCH
    assert any("distinct regional jurisdictions" in r.lower() for r in evidence.reasons)


# ---------------------------------------------------------------------
# 11. Organization Corporate Suffix Consolidation
# ---------------------------------------------------------------------
def test_organization_corporate_suffix_matching(resolver: EntityResolver):
    org1 = Entity(
        id="ORG001",
        type=EntityType.ORGANIZATION,
        label="Astra Logistics Ltd",
        risk_score=85.0,
        source_records=["FIR_001"],
    )
    org2 = Entity(
        id="ORG099",
        type=EntityType.ORGANIZATION,
        label="Astra Logistics",
        risk_score=80.0,
        source_records=["BANK_TX"],
    )
    evidence = resolver.compare_candidates(org1, org2)
    assert evidence.decision == MatchDecision.MATCH
    assert evidence.score >= 0.90


# ---------------------------------------------------------------------
# 12. Uncertain Candidate Flagging
# ---------------------------------------------------------------------
def test_uncertain_candidate_flagging(resolver: EntityResolver):
    p1 = Entity(
        id="P007",
        type=EntityType.PERSON,
        label="Sameer Khan",
        risk_score=75.0,
        source_records=["FIR_001"],
    )
    p2 = Entity(
        id="P099",
        type=EntityType.PERSON,
        label="Samir Khan",  # Phonetic variation / typo
        risk_score=70.0,
        source_records=["INT_REPORT"],
    )
    evidence = resolver.compare_candidates(p1, p2)
    # High phonetic and string similarity without shared phone -> UNCERTAIN or MATCH
    assert evidence.decision in {MatchDecision.UNCERTAIN, MatchDecision.MATCH}
    assert evidence.score >= resolver.uncertain_threshold


# ---------------------------------------------------------------------
# 13. Canonical ID Selection & Alias/Provenance Preservation
# ---------------------------------------------------------------------
def test_merge_cluster_canonical_id_and_provenance_preservation(resolver: EntityResolver):
    e1 = Entity(
        id="P001",
        type=EntityType.PERSON,
        label="Vikramaditya Singhania",
        role="Syndicate Mastermind",
        risk_score=95.0,
        aliases=["Vikram"],
        source_records=["FIR_001"],
    )
    e2 = Entity(
        id="P099",
        type=EntityType.PERSON,
        label="Vikram Singhania",
        role="Suspect",
        risk_score=80.0,
        aliases=["The Don"],
        source_records=["FIR_002", "SURV_001"],
    )
    # Add shared primary phone to force confident MATCH
    e1.attributes["primary_line"] = "+919811010001"
    e2.attributes["primary_line"] = "+919811010001"

    resolved, evidence, id_map = resolver.resolve([e1, e2])

    assert len(resolved) == 1
    merged = resolved[0]

    # Canonical ID must be P001 (lower ID)
    assert merged.id == "P001"
    assert id_map["P099"] == "P001"
    assert id_map["P001"] == "P001"

    # Maximum risk score preserved
    assert merged.risk_score == 95.0

    # Aliases fully united (including alternative label)
    assert "Vikram" in merged.aliases
    assert "The Don" in merged.aliases
    assert "Vikram Singhania" in merged.aliases

    # Source records unioned with zero loss
    assert set(merged.source_records) == {"FIR_001", "FIR_002", "SURV_001"}


# ---------------------------------------------------------------------
# 14. Relationship Endpoint Rewriting
# ---------------------------------------------------------------------
def test_relationship_endpoint_rewriting(resolver: EntityResolver):
    p1 = Entity(
        id="P001",
        type=EntityType.PERSON,
        label="Vikramaditya Singhania",
        aliases=["The Don"],
        risk_score=95.0,
        source_records=["FIR_001"],
    )
    p_dup = Entity(
        id="P099",
        type=EntityType.PERSON,
        label="The Don",
        risk_score=85.0,
        source_records=["SURV_001"],
    )
    phone = Entity(
        id="PH001",
        type=EntityType.PHONE,
        label="+919811010001",
        risk_score=80.0,
        source_records=["FIR_001"],
    )

    # Edge points to P099 (which will be merged into P001)
    rel = Relationship(
        id="R001",
        source="P099",
        target="PH001",
        type=RelationshipType.USES_PHONE,
        directed=True,
        weight=1.0,
        provenance=Provenance(
            source_id="SURV_001",
            source_type="POLICE_REPORT",
            snippet="The Don observed using phone +919811010001",
            confidence=0.95,
        ),
    )

    resolved_entities, rewritten_rels, _ = resolver.resolve_with_relationships(
        [p1, p_dup, phone],
        [rel]
    )

    assert len(rewritten_rels) == 1
    # Endpoint must now point to canonical P001 instead of P099
    assert rewritten_rels[0].source == "P001"
    assert rewritten_rels[0].target == "PH001"


# ---------------------------------------------------------------------
# 15. Duplicate Relationship Suppression
# ---------------------------------------------------------------------
def test_duplicate_relationship_suppression(resolver: EntityResolver):
    p1 = Entity(id="P001", type=EntityType.PERSON, label="Vikramaditya Singhania")
    p2 = Entity(id="P099", type=EntityType.PERSON, label="Vikramaditya Singhania")  # will merge to P001
    ph = Entity(id="PH001", type=EntityType.PHONE, label="+919811010001")

    # Two identical narrative relationships in the same document
    rel1 = Relationship(
        id="R001",
        source="P001",
        target="PH001",
        type=RelationshipType.USES_PHONE,
        provenance=Provenance(
            source_id="FIR_001",
            source_type="POLICE_REPORT",
            snippet="Vikram uses phone",
            confidence=0.95,
        ),
    )
    rel2 = Relationship(
        id="R002",
        source="P099",
        target="PH001",
        type=RelationshipType.USES_PHONE,
        provenance=Provenance(
            source_id="FIR_001",
            source_type="POLICE_REPORT",
            snippet="Vikram uses phone again",
            confidence=0.95,
        ),
    )

    _, rewritten_rels, _ = resolver.resolve_with_relationships([p1, p2, ph], [rel1, rel2])
    # Narrative duplicate collapsed into 1 canonical edge
    assert len(rewritten_rels) == 1
    assert rewritten_rels[0].source == "P001"


# ---------------------------------------------------------------------
# 16. Preservation of Distinct Structured Events (CDRs & Transactions)
# ---------------------------------------------------------------------
def test_preservation_of_distinct_cdr_and_tx_events(resolver: EntityResolver):
    ph1 = Entity(id="PH001", type=EntityType.PHONE, label="+919811010001")
    ph2 = Entity(id="PH002", type=EntityType.PHONE, label="+919811010002")

    # Two distinct CDR calls between same phones
    call1 = Relationship(
        id="R101",
        source="PH001",
        target="PH002",
        type=RelationshipType.CALLED,
        provenance=Provenance(
            source_id="CDR1001",
            source_type="TELECOM_CDR",
            snippet="Call 1",
            confidence=1.0,
        ),
    )
    call2 = Relationship(
        id="R102",
        source="PH001",
        target="PH002",
        type=RelationshipType.CALLED,
        provenance=Provenance(
            source_id="CDR1002",
            source_type="TELECOM_CDR",
            snippet="Call 2",
            confidence=1.0,
        ),
    )

    # Two distinct bank transactions
    acc1 = Entity(id="BA001", type=EntityType.BANK_ACCOUNT, label="ACC-SINGH-9901")
    acc2 = Entity(id="BA002", type=EntityType.BANK_ACCOUNT, label="ACC-ASTRA-7701")

    tx1 = Relationship(
        id="R201",
        source="BA001",
        target="BA002",
        type=RelationshipType.TRANSACTED_WITH,
        provenance=Provenance(
            source_id="TX1001",
            source_type="BANK_LEDGER",
            snippet="Tx 1",
            confidence=1.0,
        ),
    )
    tx2 = Relationship(
        id="R202",
        source="BA001",
        target="BA002",
        type=RelationshipType.TRANSACTED_WITH,
        provenance=Provenance(
            source_id="TX1002",
            source_type="BANK_LEDGER",
            snippet="Tx 2",
            confidence=1.0,
        ),
    )

    _, rewritten_rels, _ = resolver.resolve_with_relationships(
        [ph1, ph2, acc1, acc2],
        [call1, call2, tx1, tx2]
    )

    # All 4 structured events must be preserved!
    assert len(rewritten_rels) == 4
    source_ids = {r.provenance.source_id for r in rewritten_rels}
    assert source_ids == {"CDR1001", "CDR1002", "TX1001", "TX1002"}
