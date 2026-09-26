"""
VERITAS - CSV Ingestion Parser
Parses structured Call Detail Records (CDRs) and Banking/Financial transaction CSVs.
Validates schemas, normalizes phone numbers and account identifiers without destroying
raw values, handles malformed rows gracefully, and preserves source metadata for provenance.
"""
import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, ConfigDict, Field

from ai.ingestion.preprocessing import (
    normalize_account_id,
    normalize_phone_number,
    normalize_timestamp,
)


# Expected columns from data/demo/cdrs.csv
CDR_REQUIRED_COLUMNS = [
    "call_id",
    "caller_msisdn",
    "receiver_msisdn",
    "timestamp",
    "duration_sec",
    "call_type",
    "cell_tower_id",
]

# Expected columns from data/demo/transactions.csv
TRANSACTION_REQUIRED_COLUMNS = [
    "transaction_id",
    "sender_account",
    "receiver_account",
    "amount",
    "currency",
    "timestamp",
    "payment_channel",
    "reference_note",
]


class ParsingError(BaseModel):
    """Encapsulates a row-level parsing or validation failure."""
    row_index: int
    field: Optional[str] = None
    message: str
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class CDRRecord(BaseModel):
    """
    Standardized, validated Call Detail Record retaining both raw and normalized values.
    """
    model_config = ConfigDict(extra="allow")

    call_id: str = Field(..., description="Unique telecom call record identifier")
    caller_raw: str = Field(..., description="Unmodified caller MSISDN string")
    caller_normalized: str = Field(..., description="Canonical E.164 caller phone number")
    receiver_raw: str = Field(..., description="Unmodified receiver MSISDN string")
    receiver_normalized: str = Field(..., description="Canonical E.164 receiver phone number")
    timestamp_raw: str = Field(..., description="Unmodified timestamp string from switch dump")
    normalized_timestamp: Optional[str] = Field(default=None, description="ISO-8601 UTC timestamp")
    duration_sec: int = Field(..., ge=0, description="Call duration in seconds")
    call_type: str = Field(default="VOICE", description="VOICE, SMS, or DATA")
    cell_tower_id: str = Field(..., description="Cell tower / sector ID")
    row_index: int = Field(..., ge=0, description="1-indexed CSV row position for provenance")
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Complete original CSV row dictionary")


class TransactionRecord(BaseModel):
    """
    Standardized, validated financial transaction record retaining both raw and normalized values.
    """
    model_config = ConfigDict(extra="allow")

    transaction_id: str = Field(..., description="Unique transaction reference ID")
    sender_account_raw: str = Field(..., description="Unmodified sender account string")
    sender_account_normalized: str = Field(..., description="Canonical standardized sender account ID")
    receiver_account_raw: str = Field(..., description="Unmodified beneficiary account string")
    receiver_account_normalized: str = Field(..., description="Canonical standardized beneficiary account ID")
    amount: float = Field(..., ge=0.0, description="Transaction monetary value")
    currency: str = Field(default="INR", description="ISO currency code (INR, USD)")
    timestamp_raw: str = Field(..., description="Unmodified timestamp string from banking ledger")
    normalized_timestamp: Optional[str] = Field(default=None, description="ISO-8601 UTC timestamp")
    payment_channel: str = Field(..., description="Payment rail (RTGS, NEFT, IMPS, UPI, CASH_DEPOSIT, SWIFT)")
    reference_note: str = Field(default="", description="Transaction memo or invoice description")
    row_index: int = Field(..., ge=0, description="1-indexed CSV row position for provenance")
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Complete original CSV row dictionary")


class CDRParser:
    """
    Ingests and parses Call Detail Record (CDR) CSVs.
    """

    def __init__(self, strict: bool = False):
        self.strict = strict
        self.errors: List[ParsingError] = []

    def parse_file(self, file_path: Union[str, Path]) -> List[CDRRecord]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"CDR file not found: {file_path}")

        records: List[CDRRecord] = []
        self.errors = []

        with open(path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError(f"Empty or headerless CSV file: {file_path}")

            # Validate column headers
            missing_cols = [col for col in CDR_REQUIRED_COLUMNS if col not in reader.fieldnames]
            if missing_cols:
                raise ValueError(f"CDR CSV missing required columns: {missing_cols}")

            for idx, row in enumerate(reader, start=2):  # Header is line 1
                try:
                    record = self._parse_row(row, row_index=idx)
                    records.append(record)
                except Exception as e:
                    err = ParsingError(
                        row_index=idx,
                        message=str(e),
                        raw_data=row
                    )
                    self.errors.append(err)
                    if self.strict:
                        raise ValueError(f"Malformed CDR row {idx}: {e}") from e

        return records

    def _parse_row(self, row: Dict[str, str], row_index: int) -> CDRRecord:
        call_id = row.get("call_id", "").strip()
        if not call_id:
            raise ValueError("call_id cannot be empty")

        caller_raw = row.get("caller_msisdn", "").strip()
        receiver_raw = row.get("receiver_msisdn", "").strip()
        if not caller_raw or not receiver_raw:
            raise ValueError("caller_msisdn and receiver_msisdn are required")

        caller_norm = normalize_phone_number(caller_raw)
        if caller_norm is None:
            # Fallback to trimmed caller if normalization couldn't resolve
            caller_norm = caller_raw

        receiver_norm = normalize_phone_number(receiver_raw)
        if receiver_norm is None:
            receiver_norm = receiver_raw

        ts_raw = row.get("timestamp", "").strip()
        if not ts_raw:
            raise ValueError("timestamp cannot be empty")
        ts_norm = normalize_timestamp(ts_raw)

        dur_str = row.get("duration_sec", "0").strip()
        try:
            duration_sec = int(dur_str)
            if duration_sec < 0:
                raise ValueError(f"duration_sec cannot be negative: {dur_str}")
        except ValueError as e:
            raise ValueError(f"Invalid duration_sec integer '{dur_str}': {e}") from e

        call_type = row.get("call_type", "VOICE").strip().upper()
        cell_tower_id = row.get("cell_tower_id", "").strip()

        return CDRRecord(
            call_id=call_id,
            caller_raw=caller_raw,
            caller_normalized=caller_norm,
            receiver_raw=receiver_raw,
            receiver_normalized=receiver_norm,
            timestamp_raw=ts_raw,
            normalized_timestamp=ts_norm,
            duration_sec=duration_sec,
            call_type=call_type,
            cell_tower_id=cell_tower_id,
            row_index=row_index,
            raw_data=row,
        )


class TransactionParser:
    """
    Ingests and parses Financial and Banking Transaction CSVs.
    """

    def __init__(self, strict: bool = False):
        self.strict = strict
        self.errors: List[ParsingError] = []

    def parse_file(self, file_path: Union[str, Path]) -> List[TransactionRecord]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Transaction file not found: {file_path}")

        records: List[TransactionRecord] = []
        self.errors = []

        with open(path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError(f"Empty or headerless CSV file: {file_path}")

            # Validate column headers
            missing_cols = [col for col in TRANSACTION_REQUIRED_COLUMNS if col not in reader.fieldnames]
            if missing_cols:
                raise ValueError(f"Transaction CSV missing required columns: {missing_cols}")

            for idx, row in enumerate(reader, start=2):
                try:
                    record = self._parse_row(row, row_index=idx)
                    records.append(record)
                except Exception as e:
                    err = ParsingError(
                        row_index=idx,
                        message=str(e),
                        raw_data=row
                    )
                    self.errors.append(err)
                    if self.strict:
                        raise ValueError(f"Malformed Transaction row {idx}: {e}") from e

        return records

    def _parse_row(self, row: Dict[str, str], row_index: int) -> TransactionRecord:
        tx_id = row.get("transaction_id", "").strip()
        if not tx_id:
            raise ValueError("transaction_id cannot be empty")

        sender_raw = row.get("sender_account", "").strip()
        receiver_raw = row.get("receiver_account", "").strip()
        if not sender_raw or not receiver_raw:
            raise ValueError("sender_account and receiver_account are required")

        sender_norm = normalize_account_id(sender_raw)
        receiver_norm = normalize_account_id(receiver_raw)

        amt_str = row.get("amount", "0").strip()
        try:
            amount = float(amt_str)
            if amount < 0:
                raise ValueError(f"amount cannot be negative: {amt_str}")
        except ValueError as e:
            raise ValueError(f"Invalid numeric amount '{amt_str}': {e}") from e

        currency = row.get("currency", "INR").strip().upper()
        ts_raw = row.get("timestamp", "").strip()
        if not ts_raw:
            raise ValueError("timestamp cannot be empty")
        ts_norm = normalize_timestamp(ts_raw)

        channel = row.get("payment_channel", "").strip().upper()
        ref_note = row.get("reference_note", "").strip()

        return TransactionRecord(
            transaction_id=tx_id,
            sender_account_raw=sender_raw,
            sender_account_normalized=sender_norm,
            receiver_account_raw=receiver_raw,
            receiver_account_normalized=receiver_norm,
            amount=amount,
            currency=currency,
            timestamp_raw=ts_raw,
            normalized_timestamp=ts_norm,
            payment_channel=channel,
            reference_note=ref_note,
            row_index=row_index,
            raw_data=row,
        )


# Convenience module helpers
def load_cdrs_csv(file_path: Union[str, Path], strict: bool = False) -> List[CDRRecord]:
    parser = CDRParser(strict=strict)
    return parser.parse_file(file_path)


def load_transactions_csv(file_path: Union[str, Path], strict: bool = False) -> List[TransactionRecord]:
    parser = TransactionParser(strict=strict)
    return parser.parse_file(file_path)
