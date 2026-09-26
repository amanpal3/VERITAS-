"""
VERITAS - Unit & Regression Tests for Data Ingestion and Preprocessing
Covers Document/FIR parsing, CDR ingestion, Transaction ingestion, malformed row handling,
and deterministic normalization across phones, vehicles, timestamps, names, and accounts.
"""
import os
import tempfile
import pytest
from pathlib import Path

from ai.ingestion.csv_parser import (
    CDRParser,
    CDRRecord,
    TransactionParser,
    TransactionRecord,
    load_cdrs_csv,
    load_transactions_csv,
)
from ai.ingestion.document_parser import (
    DocumentParser,
    DocumentRecord,
    load_document,
    load_documents_dir,
)
from ai.ingestion.preprocessing import (
    clean_text,
    normalize_account_id,
    normalize_name,
    normalize_org_name,
    normalize_phone_number,
    normalize_timestamp,
    normalize_vehicle_plate,
)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DEMO_DIR = ROOT_DIR / "data" / "demo"


# =====================================================================
# 1. Document / FIR Ingestion Tests
# =====================================================================
def test_fir_single_file_loading():
    """Verify loading and parsing of a single police report with section parsing."""
    fir_file = DEMO_DIR / "firs" / "FIR_001_Smuggling_Bust.txt"
    assert fir_file.exists(), f"Demo file missing: {fir_file}"

    doc = load_document(fir_file)
    assert isinstance(doc, DocumentRecord)
    assert doc.source_id == "FIR-104/2026"
    assert doc.document_type == "POLICE_REPORT"
    assert "ARJUN VERMA" in doc.raw_text
    assert "DL-1M-4412" in doc.raw_text
    assert "incident_summary" in doc.sections
    assert doc.metadata.get("crime_no") == "104/2026"


def test_firs_directory_loading():
    """Verify that all 5 demo FIR and surveillance reports load without loss."""
    firs_dir = DEMO_DIR / "firs"
    docs = load_documents_dir(firs_dir)
    assert len(docs) == 5

    source_ids = {d.source_id for d in docs}
    assert "FIR-104/2026" in source_ids
    assert "FIR-188/2026" in source_ids
    assert "INT-DEL-2026-409" in source_ids
    assert "SURV-2026-031" in source_ids
    assert "FIN-EOW-2026-092" in source_ids


def test_document_parser_unreadable_or_missing_file():
    """Verify clear error handling for non-existent and empty files."""
    with pytest.raises(FileNotFoundError):
        DocumentParser.parse_file("non_existent_file.txt")

    with tempfile.NamedTemporaryFile("w", delete=False) as tf:
        tf.write("   \n  ")
        tmp_name = tf.name

    try:
        with pytest.raises(ValueError) as exc_info:
            DocumentParser.parse_file(tmp_name)
        assert "empty" in str(exc_info.value).lower()
    finally:
        os.remove(tmp_name)


# =====================================================================
# 2. CDR Ingestion Tests
# =====================================================================
def test_cdr_loading_demo_dataset():
    """Verify loading of the 64 CDR rows from data/demo/cdrs.csv."""
    cdrs_path = DEMO_DIR / "cdrs.csv"
    assert cdrs_path.exists()

    cdrs = load_cdrs_csv(cdrs_path, strict=True)
    assert len(cdrs) == 64

    # Verify first record fields
    first = cdrs[0]
    assert first.call_id == "CDR1001"
    assert first.caller_raw == "+919811010001"
    assert first.caller_normalized == "+919811010001"
    assert first.receiver_raw == "+919811010002"
    assert first.receiver_normalized == "+919811010002"
    assert first.duration_sec == 420
    assert first.cell_tower_id == "TOWER_CP_01"
    assert first.row_index == 2


def test_cdr_malformed_rows():
    """Verify detection and handling of malformed CDR rows."""
    malformed_csv = (
        "call_id,caller_msisdn,receiver_msisdn,timestamp,duration_sec,call_type,cell_tower_id\n"
        "CDR999,+919811010001,+919811010002,2026-03-01T10:00:00Z,NOT_AN_INT,VOICE,TOWER_1\n"
        "CDR998,+919811010001,,2026-03-01T10:00:00Z,120,VOICE,TOWER_1\n"
        "CDR997,+919811010001,+919811010002,2026-03-01T10:00:00Z,-15,VOICE,TOWER_1\n"
    )
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as tf:
        tf.write(malformed_csv)
        tmp_path = tf.name

    try:
        # Non-strict mode: should collect errors and return valid records (here 0 valid)
        parser = CDRParser(strict=False)
        records = parser.parse_file(tmp_path)
        assert len(records) == 0
        assert len(parser.errors) == 3

        # Strict mode: raises ValueError immediately
        strict_parser = CDRParser(strict=True)
        with pytest.raises(ValueError):
            strict_parser.parse_file(tmp_path)
    finally:
        os.remove(tmp_path)


# =====================================================================
# 3. Transaction Ingestion Tests
# =====================================================================
def test_transaction_loading_demo_dataset():
    """Verify loading of the 51 financial transactions from data/demo/transactions.csv."""
    tx_path = DEMO_DIR / "transactions.csv"
    assert tx_path.exists()

    txs = load_transactions_csv(tx_path, strict=True)
    assert len(txs) == 51

    first = txs[0]
    assert first.transaction_id == "TX1001"
    assert first.sender_account_raw == "ACC-CASH-POOL"
    assert first.sender_account_normalized == "ACC-CASH-POOL"
    assert first.receiver_account_raw == "ACC-ASTRA-7701"
    assert first.receiver_account_normalized == "ACC-ASTRA-7701"
    assert first.amount == 195000.0
    assert first.currency == "INR"
    assert first.payment_channel == "CASH_DEPOSIT"
    assert first.row_index == 2


def test_transaction_malformed_rows():
    """Verify detection and handling of malformed transaction rows."""
    malformed_csv = (
        "transaction_id,sender_account,receiver_account,amount,currency,timestamp,payment_channel,reference_note\n"
        "TX999,ACC-1,ACC-2,NOT_A_NUMBER,INR,2026-02-15T11:20:00Z,RTGS,Test\n"
        "TX998,,ACC-2,1000,INR,2026-02-15T11:20:00Z,RTGS,Test\n"
        "TX997,ACC-1,ACC-2,-500,INR,2026-02-15T11:20:00Z,RTGS,Test\n"
    )
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as tf:
        tf.write(malformed_csv)
        tmp_path = tf.name

    try:
        parser = TransactionParser(strict=False)
        records = parser.parse_file(tmp_path)
        assert len(records) == 0
        assert len(parser.errors) == 3

        strict_parser = TransactionParser(strict=True)
        with pytest.raises(ValueError):
            strict_parser.parse_file(tmp_path)
    finally:
        os.remove(tmp_path)


# =====================================================================
# 4. Phone Normalization Tests
# =====================================================================
def test_phone_normalization_formats():
    """Verify standard E.164 normalization for all common Indian phone formats."""
    expected = "+919811010001"

    assert normalize_phone_number("09811010001") == expected
    assert normalize_phone_number("9811010001") == expected
    assert normalize_phone_number("+91 98110 10001") == expected
    assert normalize_phone_number("91-9811010001") == expected
    assert normalize_phone_number("+91(98110)10001") == expected
    assert normalize_phone_number("  +91 9811010001  ") == expected

    # International phone with plus preserved
    assert normalize_phone_number("+14155552671") == "+14155552671"

    # Non-phone string / invalid
    assert normalize_phone_number("NOT_A_PHONE") is None
    assert normalize_phone_number("12345") is None
    assert normalize_phone_number("") is None


# =====================================================================
# 5. Vehicle Normalization Tests
# =====================================================================
def test_vehicle_normalization_formats():
    """Verify Indian vehicle registration normalization and casing."""
    assert normalize_vehicle_plate("dl-1m-4412") == "DL-1M-4412"
    assert normalize_vehicle_plate("DL 1M 4412") == "DL-1M-4412"
    assert normalize_vehicle_plate("DL1M4412") == "DL-1M-4412"
    assert normalize_vehicle_plate("dl 4c 9901") == "DL-4C-9901"
    assert normalize_vehicle_plate("HR-26-DK-8392") == "HR-26DK-8392" or normalize_vehicle_plate("HR-26-DK-8392") == "HR-26-DK-8392"

    # With descriptive suffix preserved
    plate_desc = normalize_vehicle_plate("DL-1C-0001 (BMW 7-Series)")
    assert "DL-1C-0001" in plate_desc
    assert "BMW 7-Series" in plate_desc


# =====================================================================
# 6. Timestamp Normalization Tests
# =====================================================================
def test_timestamp_normalization():
    """Verify ISO conversion, timezone handling, and avoiding guessing unknown timezones."""
    # Already canonical UTC
    assert normalize_timestamp("2026-03-01T14:22:10Z") == "2026-03-01T14:22:10Z"

    # With IST timezone in FIR
    ist_ts = normalize_timestamp("12-FEB-2026 23:45 IST")
    assert ist_ts is not None
    assert "+05:30" in ist_ts or "Z" in ist_ts

    # Naive timestamp - preserve without guessing timezone
    naive = normalize_timestamp("2026-03-01 14:22:10")
    assert naive == "2026-03-01T14:22:10"
    assert not naive.endswith("Z")

    # Invalid timestamp
    assert normalize_timestamp("INVALID_DATE") is None


# =====================================================================
# 7. Name & Organization Normalization Tests
# =====================================================================
def test_name_normalization():
    """Verify conservative name normalization and whitespace cleanup."""
    assert normalize_name("  RAJESH   KUMAR  ") == "Rajesh Kumar"
    assert normalize_name("\"Raju Swift\"") == "Raju Swift"
    assert normalize_name("arjun verma") == "Arjun Verma"
    assert normalize_name("Arjun Verma S/o Ramesh Verma") == "Arjun Verma S/o Ramesh Verma"


def test_organization_normalization():
    """Verify corporate suffix standardization while preserving legal entity names."""
    assert normalize_org_name("  Astra Logistics  Ltd. ") == "Astra Logistics Ltd"
    assert normalize_org_name("SHEIKH TRADING ENTERPRISES") == "Sheikh Trading Enterprises"
    assert normalize_org_name("Trident Holdings Ltd (Offshore)") == "Trident Holdings Ltd (Offshore)"


# =====================================================================
# 8. Account Normalization Tests
# =====================================================================
def test_account_normalization():
    """Verify account identifier hyphenation and casing."""
    assert normalize_account_id("acc astra 7701") == "ACC-ASTRA-7701"
    assert normalize_account_id("ACC_SHEIKH_4401") == "ACC-SHEIKH-4401"
    assert normalize_account_id("  acc-singh-9901  ") == "ACC-SINGH-9901"
