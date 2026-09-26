"""
VERITAS - Ingestion Package
Provides document, CDR, and transaction parsers, along with deterministic normalizers.
"""
from ai.ingestion.csv_parser import (
    CDRParser,
    CDRRecord,
    ParsingError,
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

__all__ = [
    "CDRParser",
    "CDRRecord",
    "TransactionParser",
    "TransactionRecord",
    "ParsingError",
    "load_cdrs_csv",
    "load_transactions_csv",
    "DocumentParser",
    "DocumentRecord",
    "load_document",
    "load_documents_dir",
    "clean_text",
    "normalize_phone_number",
    "normalize_vehicle_plate",
    "normalize_timestamp",
    "normalize_name",
    "normalize_org_name",
    "normalize_account_id",
]
