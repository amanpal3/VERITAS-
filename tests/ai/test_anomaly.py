"""
VERITAS - Tests for Explainable Anomaly Detection Layer
Tests transaction outliers, frequency spikes, burst calls, high degree,
explanations, provenance retention, deterministic scoring, and safety boundaries.
"""
import pytest
from datetime import datetime, timezone, timedelta
from typing import List

from ai.anomaly.detector import (
    AnomalyDetector,
    AnomalyResult,
    AnomalySeverity,
    AnomalyType,
)
from ai.ingestion.csv_parser import CDRRecord, TransactionRecord
from ai.schemas.entity import Entity, EntityType
from ai.schemas.relationship import Provenance, Relationship, RelationshipType


@pytest.fixture
def detector() -> AnomalyDetector:
    return AnomalyDetector()


# ---------------------------------------------------------------------
# 1. Normal Transaction Is Not Incorrectly Flagged
# ---------------------------------------------------------------------
def test_normal_transaction_not_incorrectly_flagged(detector: AnomalyDetector):
    # Dataset with uniform normal amounts: 10,000 to 12,000
    txs = [
        TransactionRecord(
            transaction_id=f"TX{i:03d}",
            sender_account_raw="ACC-A",
            sender_account_normalized="ACC-A",
            receiver_account_raw="ACC-B",
            receiver_account_normalized="ACC-B",
            amount=10000.0 + (i * 100),
            currency="INR",
            timestamp_raw="2026-03-01T10:00:00Z",
            payment_channel="NEFT",
            row_index=i + 1,
        )
        for i in range(10)
    ]
    # Evaluate a baseline transaction (10,500)
    anomalies = detector.detect(records=txs)
    # Filter high amount anomalies for TX000 - TX008
    low_amounts = [a for a in anomalies if a.anomaly_type == AnomalyType.HIGH_TRANSACTION_AMOUNT and a.feature_values.get("amount", 0) <= 10500.0]
    assert len(low_amounts) == 0


# ---------------------------------------------------------------------
# 2. Extreme Transaction Is Detected
# ---------------------------------------------------------------------
def test_extreme_transaction_detected(detector: AnomalyDetector):
    # Normal cluster around 50,000 and one extreme spike at 5,000,000
    txs = [
        TransactionRecord(
            transaction_id=f"TX{i:03d}",
            sender_account_raw="ACC-NORM",
            sender_account_normalized="ACC-NORM",
            receiver_account_raw="ACC-RCV",
            receiver_account_normalized="ACC-RCV",
            amount=50000.0 + (i * 1000),
            currency="INR",
            timestamp_raw="2026-03-01T10:00:00Z",
            payment_channel="NEFT",
            row_index=i + 1,
        )
        for i in range(15)
    ]
    spike = TransactionRecord(
        transaction_id="TX_EXTREME",
        sender_account_raw="ACC-OUTLIER",
        sender_account_normalized="ACC-OUTLIER",
        receiver_account_raw="ACC-RCV",
        receiver_account_normalized="ACC-RCV",
        amount=5000000.0,
        currency="INR",
        timestamp_raw="2026-03-02T10:00:00Z",
        payment_channel="RTGS",
        row_index=16,
    )
    txs.append(spike)

    anomalies = detector.detect(records=txs)
    amount_anomalies = [a for a in anomalies if a.anomaly_type == AnomalyType.HIGH_TRANSACTION_AMOUNT]

    assert len(amount_anomalies) >= 1
    top = amount_anomalies[0]
    assert "TX_EXTREME" in top.supporting_record_ids
    assert top.feature_values["amount"] == 5000000.0
    assert top.severity == AnomalySeverity.HIGH
    assert top.score >= 0.85


# ---------------------------------------------------------------------
# 3. High-Frequency Account Detection
# ---------------------------------------------------------------------
def test_high_frequency_account_detection(detector: AnomalyDetector):
    # Accounts A, B, C have 2 transactions each; Account HIGH has 25 transactions
    txs = []
    tx_id = 1
    for i, acc in enumerate(["ACC-A", "ACC-B", "ACC-C", "ACC-D", "ACC-E", "ACC-F"]):
        for _ in range(2):
            txs.append(
                TransactionRecord(
                    transaction_id=f"TX{tx_id:04d}",
                    sender_account_raw=acc,
                    sender_account_normalized=acc,
                    receiver_account_raw=f"ACC-RCV-{i}",
                    receiver_account_normalized=f"ACC-RCV-{i}",
                    amount=10000.0,
                    currency="INR",
                    timestamp_raw="2026-03-01T10:00:00Z",
                    payment_channel="UPI",
                    row_index=tx_id,
                )
            )
            tx_id += 1

    for _ in range(25):
        txs.append(
            TransactionRecord(
                transaction_id=f"TX{tx_id:04d}",
                sender_account_raw="ACC-HIGH",
                sender_account_normalized="ACC-HIGH",
                receiver_account_raw="ACC-RCV-HIGH",
                receiver_account_normalized="ACC-RCV-HIGH",
                amount=10000.0,
                currency="INR",
                timestamp_raw="2026-03-01T10:00:00Z",
                payment_channel="UPI",
                row_index=tx_id,
            )
        )
        tx_id += 1

    anomalies = detector.detect(records=txs)
    freq_anomalies = [a for a in anomalies if a.anomaly_type == AnomalyType.HIGH_TRANSACTION_FREQUENCY]

    assert any(a.entity_id == "ACC-HIGH" for a in freq_anomalies)
    high_acc = [a for a in freq_anomalies if a.entity_id == "ACC-HIGH"][0]
    assert high_acc.severity == AnomalySeverity.HIGH
    assert high_acc.feature_values["transaction_count"] == 25


# ---------------------------------------------------------------------
# 4. High-Frequency Phone Detection
# ---------------------------------------------------------------------
def test_high_frequency_phone_detection(detector: AnomalyDetector):
    cdrs = []
    cid = 1
    for i, ph in enumerate(["+919811010001", "+919811010002", "+919811010003", "+919811010004", "+919811010005"]):
        for _ in range(2):
            cdrs.append(
                CDRRecord(
                    call_id=f"CDR{cid:04d}",
                    caller_raw=ph,
                    caller_normalized=ph,
                    receiver_raw=f"+91981109999{i}",
                    receiver_normalized=f"+91981109999{i}",
                    timestamp_raw="2026-03-01T12:00:00Z",
                    duration_sec=60,
                    call_type="VOICE",
                    cell_tower_id="T1",
                    row_index=cid,
                )
            )
            cid += 1

    for _ in range(30):
        cdrs.append(
            CDRRecord(
                call_id=f"CDR{cid:04d}",
                caller_raw="+919811099999",
                caller_normalized="+919811099999",
                receiver_raw="+919811088888",
                receiver_normalized="+919811088888",
                timestamp_raw="2026-03-01T12:00:00Z",
                duration_sec=60,
                call_type="VOICE",
                cell_tower_id="T1",
                row_index=cid,
            )
        )
        cid += 1

    anomalies = detector.detect(records=cdrs)
    call_anomalies = [a for a in anomalies if a.anomaly_type == AnomalyType.HIGH_CALL_FREQUENCY]

    assert any(a.entity_id == "+919811099999" for a in call_anomalies)
    top_phone = [a for a in call_anomalies if a.entity_id == "+919811099999"][0]
    assert top_phone.feature_values["call_count"] >= 30
    assert top_phone.severity == AnomalySeverity.HIGH


# ---------------------------------------------------------------------
# 5. Burst Activity Detection Where Timestamps Support It
# ---------------------------------------------------------------------
def test_burst_activity_detection(detector: AnomalyDetector):
    # 5 calls within 15 minutes for phone +919811010007
    base_time = datetime(2026, 3, 1, 14, 0, 0, tzinfo=timezone.utc)
    cdrs = []
    for i in range(5):
        ts = base_time + timedelta(minutes=i * 2)
        cdrs.append(
            CDRRecord(
                call_id=f"CDR_BURST_{i}",
                caller_raw="+919811010007",
                caller_normalized="+919811010007",
                receiver_raw="+919811010008",
                receiver_normalized="+919811010008",
                timestamp_raw=ts.isoformat(),
                duration_sec=120,
                call_type="VOICE",
                cell_tower_id="TOWER_BURST",
                row_index=i + 1,
            )
        )

    anomalies = detector.detect(records=cdrs)
    bursts = [a for a in anomalies if a.anomaly_type == AnomalyType.BURST_ACTIVITY]

    assert len(bursts) >= 1
    burst = bursts[0]
    assert burst.entity_id in {"+919811010007", "+919811010008"}
    assert burst.feature_values["burst_events_count"] == 5
    assert len(burst.supporting_record_ids) == 5


# ---------------------------------------------------------------------
# 6. High-Degree Node Detection
# ---------------------------------------------------------------------
def test_high_degree_node_detection(detector: AnomalyDetector):
    # Star graph topology: Hub node P001 connected to 10 satellite nodes
    entities = [
        Entity(id="P001", type=EntityType.PERSON, label="Hub Node"),
    ]
    relationships = []
    for i in range(1, 11):
        sat_id = f"P{i:03d}_SAT"
        entities.append(Entity(id=sat_id, type=EntityType.PERSON, label=f"Sat Node {i}"))
        relationships.append(
            Relationship(
                id=f"R{i:03d}",
                source="P001",
                target=sat_id,
                type=RelationshipType.COORDINATES_WITH,
                provenance=Provenance(
                    source_id=f"FIR_{i}",
                    source_type="POLICE_REPORT",
                    snippet="Coordinates with",
                    confidence=0.9,
                ),
            )
        )

    anomalies = detector.detect(entities=entities, relationships=relationships)
    degree_anomalies = [a for a in anomalies if a.anomaly_type == AnomalyType.HIGH_CONNECTIVITY]

    assert len(degree_anomalies) >= 1
    assert degree_anomalies[0].entity_id == "P001"
    assert degree_anomalies[0].feature_values["degree"] == 10
    assert degree_anomalies[0].severity == AnomalySeverity.HIGH


# ---------------------------------------------------------------------
# 7. Anomaly Explanation Exists & Is Descriptive
# ---------------------------------------------------------------------
def test_anomaly_explanation_exists(detector: AnomalyDetector):
    tx = TransactionRecord(
        transaction_id="TX_BIG",
        sender_account_raw="ACC-1",
        sender_account_normalized="ACC-1",
        receiver_account_raw="ACC-2",
        receiver_account_normalized="ACC-2",
        amount=10000000.0,
        currency="INR",
        timestamp_raw="2026-03-01T10:00:00Z",
        payment_channel="RTGS",
        row_index=1,
    )
    # Add small background transactions
    background = [
        TransactionRecord(
            transaction_id=f"TX_BG_{i}",
            sender_account_raw="ACC-B1",
            sender_account_normalized="ACC-B1",
            receiver_account_raw="ACC-B2",
            receiver_account_normalized="ACC-B2",
            amount=50000.0,
            currency="INR",
            timestamp_raw="2026-03-01T10:00:00Z",
            payment_channel="NEFT",
            row_index=i + 2,
        )
        for i in range(10)
    ]
    anomalies = detector.detect(records=[tx] + background)
    for a in anomalies:
        assert isinstance(a.explanation, str)
        assert len(a.explanation.strip()) > 20
        # Must NOT use non-analytical accusatory words
        assert "guilty" not in a.explanation.lower()
        assert "criminal" not in a.explanation.lower()


# ---------------------------------------------------------------------
# 8. Supporting Source IDs Are Preserved
# ---------------------------------------------------------------------
def test_supporting_source_ids_preserved(detector: AnomalyDetector):
    tx = TransactionRecord(
        transaction_id="TX_AUDIT_99",
        sender_account_raw="ACC-AUDIT",
        sender_account_normalized="ACC-AUDIT",
        receiver_account_raw="ACC-DEST",
        receiver_account_normalized="ACC-DEST",
        amount=9900000.0,
        currency="INR",
        timestamp_raw="2026-03-01T10:00:00Z",
        payment_channel="SWIFT",
        row_index=1,
    )
    bg = [
        TransactionRecord(
            transaction_id=f"TX_BG_{i}",
            sender_account_raw="ACC-X",
            sender_account_normalized="ACC-X",
            receiver_account_raw="ACC-Y",
            receiver_account_normalized="ACC-Y",
            amount=20000.0,
            currency="INR",
            timestamp_raw="2026-03-01T10:00:00Z",
            payment_channel="NEFT",
            row_index=i + 2,
        )
        for i in range(10)
    ]
    anomalies = detector.detect(records=[tx] + bg)
    tx_anom = [a for a in anomalies if a.anomaly_type == AnomalyType.HIGH_TRANSACTION_AMOUNT][0]
    assert "TX_AUDIT_99" in tx_anom.supporting_record_ids


# ---------------------------------------------------------------------
# 9. Score Bounds & Semantics Are Valid
# ---------------------------------------------------------------------
def test_score_bounds_and_severity_semantics(detector: AnomalyDetector):
    txs = [
        TransactionRecord(
            transaction_id=f"TX_{i}",
            sender_account_raw="ACC-S",
            sender_account_normalized="ACC-S",
            receiver_account_raw="ACC-R",
            receiver_account_normalized="ACC-R",
            amount=10000.0 * (i + 1),
            currency="INR",
            timestamp_raw="2026-03-01T10:00:00Z",
            payment_channel="NEFT",
            row_index=i + 1,
        )
        for i in range(20)
    ]
    anomalies = detector.detect(records=txs)
    for a in anomalies:
        assert 0.0 <= a.score <= 1.0
        assert a.severity in {AnomalySeverity.LOW, AnomalySeverity.MEDIUM, AnomalySeverity.HIGH}


# ---------------------------------------------------------------------
# 10. Deterministic Repeated Execution
# ---------------------------------------------------------------------
def test_deterministic_repeated_execution(detector: AnomalyDetector):
    txs = [
        TransactionRecord(
            transaction_id=f"TX_{i}",
            sender_account_raw=f"ACC-{i%3}",
            sender_account_normalized=f"ACC-{i%3}",
            receiver_account_raw="ACC-TGT",
            receiver_account_normalized="ACC-TGT",
            amount=50000.0 + (i * 25000),
            currency="INR",
            timestamp_raw="2026-03-01T10:00:00Z",
            payment_channel="NEFT",
            row_index=i + 1,
        )
        for i in range(15)
    ]
    run1 = detector.detect(records=txs)
    run2 = detector.detect(records=txs)

    assert len(run1) == len(run2)
    for a1, a2 in zip(run1, run2):
        assert a1.entity_id == a2.entity_id
        assert a1.anomaly_type == a2.anomaly_type
        assert a1.score == a2.score
        assert a1.severity == a2.severity


# ---------------------------------------------------------------------
# 11. Empty Dataset Handled Safely
# ---------------------------------------------------------------------
def test_empty_dataset_handled_safely(detector: AnomalyDetector):
    anomalies = detector.detect([], [], [])
    assert anomalies == []

    anomalies_none = detector.detect(None, None, None)
    assert anomalies_none == []


# ---------------------------------------------------------------------
# 12. Insufficient-Data Case Handled Safely
# ---------------------------------------------------------------------
def test_insufficient_data_handled_safely(detector: AnomalyDetector):
    single_tx = [
        TransactionRecord(
            transaction_id="TX_SINGLE",
            sender_account_raw="ACC-1",
            sender_account_normalized="ACC-1",
            receiver_account_raw="ACC-2",
            receiver_account_normalized="ACC-2",
            amount=1000.0,
            currency="INR",
            timestamp_raw="2026-03-01T10:00:00Z",
            payment_channel="UPI",
            row_index=1,
        )
    ]
    # Should not crash or produce false anomalies without baseline
    anomalies = detector.detect(records=single_tx)
    assert anomalies == []
