"""
VERITAS - Handoff Scenario Loader Helper
Constructs typed DocumentRecord, CDRRecord, and TransactionRecord instances
from tests/fixtures/handoff_scenario.json.
"""
from typing import List, Tuple
from ai.ingestion.csv_parser import CDRRecord, TransactionRecord
from ai.ingestion.document_parser import DocumentRecord
from tests.fixtures import load_handoff_scenario


def get_handoff_records() -> Tuple[List[DocumentRecord], List[CDRRecord], List[TransactionRecord]]:
    """
    Returns typed records (docs, cdrs, txs) for the canonical Member 1 -> Member 2 handoff scenario.
    """
    data = load_handoff_scenario()

    docs = [DocumentRecord(**d) for d in data.get("documents", [])]
    cdrs = [CDRRecord(**c) for c in data.get("cdrs", [])]
    txs = [TransactionRecord(**t) for t in data.get("transactions", [])]

    return docs, cdrs, txs


def get_all_handoff_records() -> List[object]:
    """
    Returns a unified list of all heterogeneous records in the handoff fixture.
    """
    docs, cdrs, txs = get_handoff_records()
    return list(docs) + list(cdrs) + list(txs)
