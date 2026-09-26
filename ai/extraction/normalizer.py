"""
VERITAS - Entity Normalizer
Standardizes names, phone formats (E.164), vehicle registration, timestamps,
and identifiers. Reuses canonical normalizers from ai.ingestion.preprocessing
to eliminate duplication.
"""
from ai.ingestion.preprocessing import (
    clean_text,
    normalize_account_id,
    normalize_name,
    normalize_org_name,
    normalize_phone_number,
    normalize_timestamp,
    normalize_vehicle_plate,
)


class EntityNormalizer:
    """
    Standardization helper for investigative entities extracted from unstructured texts
    and tabular forensic ledgers.
    """

    @staticmethod
    def phone(raw_phone: str) -> str:
        res = normalize_phone_number(raw_phone)
        return res if res is not None else raw_phone.strip()

    @staticmethod
    def vehicle(raw_plate: str) -> str:
        res = normalize_vehicle_plate(raw_plate)
        return res if res is not None else raw_plate.strip()

    @staticmethod
    def timestamp(raw_ts: str) -> str:
        res = normalize_timestamp(raw_ts)
        return res if res is not None else raw_ts.strip()

    @staticmethod
    def name(raw_name: str) -> str:
        return normalize_name(raw_name)

    @staticmethod
    def organization(raw_org: str) -> str:
        return normalize_org_name(raw_org)

    @staticmethod
    def account(raw_acc: str) -> str:
        return normalize_account_id(raw_acc)

    @staticmethod
    def text(raw_text: str) -> str:
        return clean_text(raw_text)
