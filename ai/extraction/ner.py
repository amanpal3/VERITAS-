"""
VERITAS - Hybrid Named Entity Recognition (NER) & Extraction Layer
Combines deterministic regex and rule-based extractors with spaCy NLP (and a robust
rule-based fallback). Extracts Person, Phone, Vehicle, Location, Organization, and
BankAccount entities while preserving complete evidentiary provenance and assigning stable IDs.
"""
import re
import logging
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from ai.ingestion.csv_parser import CDRRecord, TransactionRecord
from ai.ingestion.document_parser import DocumentRecord
from ai.ingestion.preprocessing import (
    clean_text,
    normalize_account_id,
    normalize_name,
    normalize_org_name,
    normalize_phone_number,
    normalize_vehicle_plate,
)
from ai.schemas.entity import Entity, EntityType

logger = logging.getLogger(__name__)


# =====================================================================
# Deterministic Patterns for Criminal Forensics
# =====================================================================

# Indian Vehicle Registration Pattern
# Matches e.g. DL-1M-4412, DL-4C-9901, DL-3C-1234, DL-1C-0001, HR-26-DK-8392
VEHICLE_REGEX = re.compile(
    r"\b([A-Z]{2}[-\s]?[0-9]{1,2}[-\s]?[A-Z]{1,3}[-\s]?[0-9]{4})\b",
    re.IGNORECASE
)

# Indian Phone / MSISDN Pattern (strict: 10-12 digits, leading +91, 91, or 0, starting with 6-9)
# Avoids plain integers like "14 kg", "50,000", "48,00,000"
PHONE_REGEX = re.compile(
    r"(?:\+91[\s\-]?[6-9][0-9]{4}[\s\-]?[0-9]{5}|\+91[\s\-]?[6-9][0-9]{9}|0?[6-9][0-9]{9})\b"
)

# Forensic Bank Account Pattern (e.g. ACC-ASTRA-7701, ACC-SINGH-9901, ACC-SHEIKH-4401)
ACCOUNT_REGEX = re.compile(
    r"\b(ACC[-_][A-Z0-9]+[-_][0-9]{3,6})\b",
    re.IGNORECASE
)

# Case / Report Reference IDs (for context extraction)
REPORT_REF_REGEX = re.compile(
    r"\b(?:FIR[-:\s]*[0-9]+/[0-9]{4}|INT-DEL-[0-9]{4}-[0-9]+|SURV-[0-9]{4}-[0-9]+|FIN-EOW-[0-9]{4}-[0-9]+)\b",
    re.IGNORECASE
)


class EntityIDGenerator:
    """
    Generates predictable, deterministic, human-readable IDs for entities
    (e.g. P001, PH001, V001, LOC001, ORG001, BA001).
    Ensures identical normalized entity keys receive the exact same ID across calls.
    """

    PREFIXES = {
        EntityType.PERSON: "P",
        EntityType.PHONE: "PH",
        EntityType.VEHICLE: "V",
        EntityType.LOCATION: "LOC",
        EntityType.ORGANIZATION: "ORG",
        EntityType.BANK_ACCOUNT: "BA",
    }

    # Pre-seeded canonical mappings for demo dataset consistency
    CANONICAL_DEMO_SEEDS = {
        (EntityType.PERSON, "Vikramaditya Singhania"): "P001",
        (EntityType.PERSON, "Tariq Sheikh"): "P002",
        (EntityType.PERSON, "Rajesh Kumar"): "P003",
        (EntityType.PERSON, "Kabir Mirza"): "P004",
        (EntityType.PERSON, "Anita Roy"): "P005",
        (EntityType.PERSON, "Arjun Verma"): "P006",
        (EntityType.PERSON, "Sameer Khan"): "P007",
        (EntityType.PERSON, "Deepak Sharma"): "P008",
        (EntityType.PERSON, "Imran Qureshi"): "P009",
        (EntityType.PERSON, "Farhan Ali"): "P010",
        (EntityType.PHONE, "+919811010001"): "PH001",
        (EntityType.PHONE, "+919811010002"): "PH002",
        (EntityType.PHONE, "+919811010003"): "PH003",
        (EntityType.PHONE, "+919811010004"): "PH004",
        (EntityType.PHONE, "+919811010005"): "PH005",
        (EntityType.PHONE, "+919811010006"): "PH006",
        (EntityType.VEHICLE, "DL-1C-0001"): "V001",
        (EntityType.VEHICLE, "DL-3C-1234"): "V002",
        (EntityType.VEHICLE, "DL-4C-9901"): "V003",
        (EntityType.VEHICLE, "DL-1M-4412"): "V004",
        (EntityType.ORGANIZATION, "Astra Logistics Ltd"): "ORG001",
        (EntityType.ORGANIZATION, "Sheikh Trading Enterprises"): "ORG002",
        (EntityType.ORGANIZATION, "Trident Holdings Ltd"): "ORG003",
        (EntityType.LOCATION, "Okhla Industrial Area"): "LOC001",
        (EntityType.LOCATION, "Chandni Chowk"): "LOC002",
        (EntityType.LOCATION, "Vasant Vihar"): "LOC003",
        (EntityType.BANK_ACCOUNT, "ACC-SINGH-9901"): "BA001",
        (EntityType.BANK_ACCOUNT, "ACC-ASTRA-7701"): "BA002",
        (EntityType.BANK_ACCOUNT, "ACC-SHEIKH-4401"): "BA003",
    }

    def __init__(self):
        self._registry: Dict[Tuple[EntityType, str], str] = dict(self.CANONICAL_DEMO_SEEDS)
        self._counters: Dict[EntityType, int] = {
            t: 10 for t in EntityType
        }
        # Advance counters past any pre-seeded ID values
        for (etype, _), assigned_id in self._registry.items():
            num_part = re.sub(r"\D", "", assigned_id)
            if num_part.isdigit():
                val = int(num_part)
                if val >= self._counters[etype]:
                    self._counters[etype] = val

    def get_id(self, entity_type: EntityType, normalized_key: str) -> str:
        key = (entity_type, normalized_key)
        if key in self._registry:
            return self._registry[key]

        prefix = self.PREFIXES.get(entity_type, "E")
        self._counters[entity_type] += 1
        new_id = f"{prefix}{self._counters[entity_type]:03d}"
        self._registry[key] = new_id
        return new_id

    def reset(self):
        self.__init__()


class RawEntityCandidate:
    """Internal candidate representation before record-level deduplication."""
    def __init__(
        self,
        entity_type: EntityType,
        raw_text: str,
        normalized_value: str,
        confidence: float,
        char_span: Tuple[int, int],
        snippet: str,
        role: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        self.entity_type = entity_type
        self.raw_text = raw_text
        self.normalized_value = normalized_value
        self.confidence = confidence
        self.char_span = char_span
        self.snippet = snippet
        self.role = role
        self.aliases = aliases or []
        self.attributes = attributes or {}


class EntityExtractor:
    """
    Hybrid Named Entity Recognition engine.
    - Deterministic Regex/Rule matching for Phone, Vehicle, BankAccount.
    - spaCy NLP for Person, Location, Organization (with conservative rule-based fallback).
    - Preserves provenance, sentence snippets, character spans, and assigns stable IDs.
    """

    def __init__(self, use_spacy: bool = True):
        self.use_spacy = use_spacy
        self.id_generator = EntityIDGenerator()
        self.nlp = None

        if self.use_spacy:
            try:
                import spacy
                # Try loading en_core_web_sm if installed locally
                self.nlp = spacy.load("en_core_web_sm")
            except (ImportError, OSError):
                # Graceful fallback: do not download over network, operate purely deterministic
                self.nlp = None

    def extract_from_text(
        self,
        text: str,
        source_id: str,
        source_type: str = "POLICE_REPORT"
    ) -> List[Entity]:
        """
        Extracts all canonical entities from text with record-level deduplication.
        """
        if not text or not text.strip():
            return []

        candidates: List[RawEntityCandidate] = []

        # 1. Deterministic Extraction: Phone, Vehicle, BankAccount
        candidates.extend(self._extract_deterministic_phones(text))
        candidates.extend(self._extract_deterministic_vehicles(text))
        candidates.extend(self._extract_deterministic_accounts(text))

        # 2. NLP or Fallback Extraction: Person, Location, Organization
        if self.nlp is not None:
            candidates.extend(self._extract_with_spacy(text))
        else:
            candidates.extend(self._extract_fallback_nlp(text))

        # 3. Deduplicate candidates within this record
        entities = self._consolidate_candidates(candidates, source_id, source_type)
        return entities

    def extract_from_record(self, record: Any) -> List[Entity]:
        """
        Extracts entities from structured Ingestion records (DocumentRecord, CDRRecord, TransactionRecord).
        """
        if isinstance(record, DocumentRecord):
            return self.extract_from_text(
                text=record.raw_text,
                source_id=record.source_id,
                source_type=record.document_type
            )
        elif isinstance(record, CDRRecord):
            return self._extract_from_cdr(record)
        elif isinstance(record, TransactionRecord):
            return self._extract_from_transaction(record)
        else:
            raise TypeError(f"Unsupported record type: {type(record)}")

    # -----------------------------------------------------------------
    # Deterministic Extractors
    # -----------------------------------------------------------------

    def _extract_deterministic_phones(self, text: str) -> List[RawEntityCandidate]:
        candidates = []
        for match in PHONE_REGEX.finditer(text):
            raw = match.group(0).strip()
            norm = normalize_phone_number(raw)
            if norm:
                span = match.span()
                snippet = self._get_surrounding_sentence(text, span[0], span[1])
                candidates.append(
                    RawEntityCandidate(
                        entity_type=EntityType.PHONE,
                        raw_text=raw,
                        normalized_value=norm,
                        confidence=0.98,
                        char_span=span,
                        snippet=snippet,
                        role="Mobile Line",
                    )
                )
        return candidates

    def _extract_deterministic_vehicles(self, text: str) -> List[RawEntityCandidate]:
        candidates = []
        for match in VEHICLE_REGEX.finditer(text):
            raw = match.group(1).strip()
            # Reject false positives: e.g. "DL" followed by words or short numbers
            norm = normalize_vehicle_plate(raw)
            if norm and len(norm) >= 7:
                span = match.span()
                snippet = self._get_surrounding_sentence(text, span[0], span[1])
                candidates.append(
                    RawEntityCandidate(
                        entity_type=EntityType.VEHICLE,
                        raw_text=raw,
                        normalized_value=norm,
                        confidence=0.95,
                        char_span=span,
                        snippet=snippet,
                        role="Vehicle",
                    )
                )
        return candidates

    def _extract_deterministic_accounts(self, text: str) -> List[RawEntityCandidate]:
        candidates = []
        for match in ACCOUNT_REGEX.finditer(text):
            raw = match.group(1).strip()
            norm = normalize_account_id(raw)
            if norm:
                span = match.span()
                snippet = self._get_surrounding_sentence(text, span[0], span[1])
                candidates.append(
                    RawEntityCandidate(
                        entity_type=EntityType.BANK_ACCOUNT,
                        raw_text=raw,
                        normalized_value=norm,
                        confidence=0.95,
                        char_span=span,
                        snippet=snippet,
                        role="Bank Account",
                    )
                )
        return candidates

    # -----------------------------------------------------------------
    # spaCy NLP Extractor
    # -----------------------------------------------------------------

    def _extract_with_spacy(self, text: str) -> List[RawEntityCandidate]:
        candidates = []
        doc = self.nlp(text)
        for ent in doc.ents:
            raw = ent.text.strip()
            if not raw:
                continue

            span = (ent.start_char, ent.end_char)
            snippet = self._get_surrounding_sentence(text, span[0], span[1])

            if ent.label_ == "PERSON":
                norm = normalize_name(raw)
                # Discard single character initials or officer titles caught as names
                if len(norm) > 2 and not norm.isupper() and not self._is_legal_noise(norm):
                    role, aliases = self._infer_person_context(text, span[0], span[1])
                    candidates.append(
                        RawEntityCandidate(
                            entity_type=EntityType.PERSON,
                            raw_text=raw,
                            normalized_value=norm,
                            confidence=0.85,
                            char_span=span,
                            snippet=snippet,
                            role=role,
                            aliases=aliases,
                        )
                    )
            elif ent.label_ in {"GPE", "LOC"}:
                norm = normalize_name(raw)
                if len(norm) > 2:
                    candidates.append(
                        RawEntityCandidate(
                            entity_type=EntityType.LOCATION,
                            raw_text=raw,
                            normalized_value=norm,
                            confidence=0.85,
                            char_span=span,
                            snippet=snippet,
                            role="Location",
                        )
                    )
            elif ent.label_ == "ORG":
                norm = normalize_org_name(raw)
                if len(norm) > 2 and not self._is_legal_noise(norm):
                    candidates.append(
                        RawEntityCandidate(
                            entity_type=EntityType.ORGANIZATION,
                            raw_text=raw,
                            normalized_value=norm,
                            confidence=0.85,
                            char_span=span,
                            snippet=snippet,
                            role="Organization",
                        )
                    )

        # Supplement with structural forensic heuristics even when spaCy runs
        candidates.extend(self._extract_fallback_nlp(text))
        return candidates

    # -----------------------------------------------------------------
    # Fallback Rule-Based NLP Extractor (No external dependencies)
    # -----------------------------------------------------------------

    def _extract_fallback_nlp(self, text: str) -> List[RawEntityCandidate]:
        candidates = []

        # 1. Forensic Person Patterns (Contextual cues in FIR text)
        person_patterns = [
            (re.compile(r"\bidentified as\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)", re.IGNORECASE), "Suspect"),
            (re.compile(r"\baccused\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)", re.IGNORECASE), "Accused"),
            (re.compile(r"\bmanaged by\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)", re.IGNORECASE), "Logistics Coordinator"),
            (re.compile(r"\boverseen by\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)", re.IGNORECASE), "Hawala Broker"),
            (re.compile(r"\boperated by\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)", re.IGNORECASE), "Enforcer"),
            (re.compile(r"\bbelonging to\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)", re.IGNORECASE), "Beneficiary"),
            (re.compile(r"\baccompanied by\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)", re.IGNORECASE), "Associate"),
            (re.compile(r"\bINSPECTOR\s+([A-Z\.\s]+),\s+SPECIAL", re.IGNORECASE), "Investigating Officer"),
            (re.compile(r"\bACP\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)", re.IGNORECASE), "Investigating Officer"),
            (re.compile(r"\bS/o\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)", re.IGNORECASE), "Relative"),
            (re.compile(r"\b([A-Z]{2,}(?:\s+[A-Z]{2,})+)\s+\(Age\s+[0-9]+", re.IGNORECASE), "Suspect"),
            (re.compile(r"\b([A-Z]{2,}(?:\s+[A-Z]{2,})+)\s+\(Account:", re.IGNORECASE), "Beneficiary"),
            (re.compile(r"\b([A-Z]{2,}(?:\s+[A-Z]{2,})+)\s+\(Director,", re.IGNORECASE), "Company Director"),
        ]

        for pat, default_role in person_patterns:
            for match in pat.finditer(text):
                raw = match.group(1).strip()
                norm = normalize_name(raw)
                if len(norm) > 2 and not self._is_legal_noise(norm):
                    span = match.span(1)
                    snippet = self._get_surrounding_sentence(text, span[0], span[1])
                    role, aliases = self._infer_person_context(text, span[0], span[1], default_role)
                    candidates.append(
                        RawEntityCandidate(
                            entity_type=EntityType.PERSON,
                            raw_text=raw,
                            normalized_value=norm,
                            confidence=0.90,
                            char_span=span,
                            snippet=snippet,
                            role=role,
                            aliases=aliases,
                        )
                    )

        # Find all mentions of discovered persons throughout the document
        discovered_names = {c.normalized_value for c in candidates if c.entity_type == EntityType.PERSON}
        for name in discovered_names:
            for m in re.finditer(rf"\b{re.escape(name)}\b", text, re.IGNORECASE):
                span = m.span()
                if not any(c.char_span == span for c in candidates):
                    raw = m.group(0)
                    snippet = self._get_surrounding_sentence(text, span[0], span[1])
                    candidates.append(
                        RawEntityCandidate(
                            entity_type=EntityType.PERSON,
                            raw_text=raw,
                            normalized_value=name,
                            confidence=0.88,
                            char_span=span,
                            snippet=snippet,
                            role="Suspect",
                        )
                    )

        # 2. Location Patterns
        location_terms = [
            "Singhu Border",
            "Okhla Industrial Area",
            "Okhla Industrial Area, Phase II",
            "Noida",
            "New Delhi",
            "Old Delhi",
            "Chandni Chowk",
            "Connaught Place",
            "Aerocity",
            "Vasant Vihar",
            "Barakhamba Road",
            "South Delhi",
            "Ghaziabad",
            "Mehrauli",
        ]
        for loc in location_terms:
            for match in re.finditer(rf"\b{re.escape(loc)}\b", text, re.IGNORECASE):
                raw = match.group(0)
                norm = normalize_name(raw)
                span = match.span()
                snippet = self._get_surrounding_sentence(text, span[0], span[1])
                candidates.append(
                    RawEntityCandidate(
                        entity_type=EntityType.LOCATION,
                        raw_text=raw,
                        normalized_value=norm,
                        confidence=0.85,
                        char_span=span,
                        snippet=snippet,
                        role="Location Hub",
                    )
                )

        # 3. Organization Patterns
        org_terms = [
            "Astra Logistics Ltd",
            "Astra Logistics",
            "Astra Exports",
            "Sheikh Trading Enterprises",
            "Trident Holdings Ltd",
            "Trident Holdings",
            "Special Cell",
            "Economic Offences Wing",
            "EOW",
            "Financial Intelligence Unit",
            "FIU",
            "Crime Intelligence Branch",
        ]
        for org in org_terms:
            for match in re.finditer(rf"\b{re.escape(org)}\b", text, re.IGNORECASE):
                raw = match.group(0)
                norm = normalize_org_name(raw)
                span = match.span()
                snippet = self._get_surrounding_sentence(text, span[0], span[1])
                candidates.append(
                    RawEntityCandidate(
                        entity_type=EntityType.ORGANIZATION,
                        raw_text=raw,
                        normalized_value=norm,
                        confidence=0.88,
                        char_span=span,
                        snippet=snippet,
                        role="Organization",
                    )
                )

        return candidates

    # -----------------------------------------------------------------
    # Ingestion Record Extractors
    # -----------------------------------------------------------------

    def _extract_from_cdr(self, record: CDRRecord) -> List[Entity]:
        """Extracts caller and receiver phones from a CDRRecord."""
        entities = []
        for is_caller, norm, raw in [
            (True, record.caller_normalized, record.caller_raw),
            (False, record.receiver_normalized, record.receiver_raw),
        ]:
            eid = self.id_generator.get_id(EntityType.PHONE, norm)
            ent = Entity(
                id=eid,
                type=EntityType.PHONE,
                label=norm,
                name=norm,
                role="Active Caller" if is_caller else "Call Receiver",
                risk_score=75.0,
                aliases=[raw] if raw != norm else [],
                attributes={
                    "original_value": raw,
                    "confidence": 1.0,
                    "source_id": record.call_id,
                    "source_type": "TELECOM_CDR",
                    "cell_tower_id": record.cell_tower_id,
                    "timestamp": record.normalized_timestamp or record.timestamp_raw,
                },
                source_records=[record.call_id],
            )
            entities.append(ent)
        return entities

    def _extract_from_transaction(self, record: TransactionRecord) -> List[Entity]:
        """Extracts sender and receiver accounts from a TransactionRecord."""
        entities = []
        for is_sender, norm, raw in [
            (True, record.sender_account_normalized, record.sender_account_raw),
            (False, record.receiver_account_normalized, record.receiver_account_raw),
        ]:
            eid = self.id_generator.get_id(EntityType.BANK_ACCOUNT, norm)
            ent = Entity(
                id=eid,
                type=EntityType.BANK_ACCOUNT,
                label=norm,
                name=norm,
                role="Originating Account" if is_sender else "Beneficiary Account",
                risk_score=85.0,
                aliases=[raw] if raw != norm else [],
                attributes={
                    "original_value": raw,
                    "confidence": 1.0,
                    "source_id": record.transaction_id,
                    "source_type": "BANK_LEDGER",
                    "currency": record.currency,
                    "payment_channel": record.payment_channel,
                },
                source_records=[record.transaction_id],
            )
            entities.append(ent)
        return entities

    # -----------------------------------------------------------------
    # Candidate Consolidation & Provenance Binding
    # -----------------------------------------------------------------

    def _consolidate_candidates(
        self,
        candidates: List[RawEntityCandidate],
        source_id: str,
        source_type: str
    ) -> List[Entity]:
        """
        Deduplicates candidates sharing identical (type, normalized_value)
        within the same source document. Merges aliases and spans.
        """
        grouped: Dict[Tuple[EntityType, str], List[RawEntityCandidate]] = {}
        for c in candidates:
            key = (c.entity_type, c.normalized_value)
            grouped.setdefault(key, []).append(c)

        entities: List[Entity] = []

        for (etype, norm_val), items in grouped.items():
            # Use candidate with highest confidence as primary
            best = max(items, key=lambda x: x.confidence)
            stable_id = self.id_generator.get_id(etype, norm_val)

            # Union aliases
            all_aliases: Set[str] = set()
            for it in items:
                all_aliases.update(it.aliases)
            # If raw differs from normalized, include raw as alias
            for it in items:
                if it.raw_text.strip() != norm_val:
                    all_aliases.add(it.raw_text.strip())

            # Compile character spans and snippets
            spans = [it.char_span for it in items]
            best_snippet = best.snippet

            # Determine risk score based on entity category and investigative role
            risk = self._calculate_risk_score(etype, best.role)

            entity = Entity(
                id=stable_id,
                type=etype,
                label=norm_val,
                name=norm_val,
                role=best.role,
                risk_score=risk,
                aliases=sorted(list(all_aliases)),
                attributes={
                    "original_value": best.raw_text,
                    "confidence": best.confidence,
                    "source_id": source_id,
                    "source_type": source_type,
                    "snippet": best_snippet,
                    "char_spans": spans,
                    "occurrences": len(items),
                },
                source_records=[source_id],
            )
            entities.append(entity)

        return entities

    # -----------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------

    @staticmethod
    def _get_surrounding_sentence(text: str, start: int, end: int, window: int = 150) -> str:
        """Extracts the sentence or context snippet containing the span."""
        s_start = max(0, start - window)
        s_end = min(len(text), end + window)
        snippet = text[s_start:s_end].replace("\n", " ").strip()
        return snippet

    @staticmethod
    def _is_legal_noise(term: str) -> bool:
        """Filters out statutory section headings or police report noise."""
        noise = {
            "IPC", "NDPS", "PMLA", "SEC", "SECTION", "DATE", "TIME",
            "NEW DELHI", "DELHI", "REPORT", "CRIME NO", "ACT", "INCIDENT"
        }
        return term.strip().upper() in noise

    @staticmethod
    def _infer_person_context(
        text: str,
        start: int,
        end: int,
        default_role: str = "Suspect"
    ) -> Tuple[str, List[str]]:
        """
        Inspects text window near person mention to extract aliases (alias "...")
        and investigative roles.
        """
        window = text[max(0, start - 50) : min(len(text), end + 80)]
        aliases = []

        alias_match = re.search(r'alias\s+["“\']([^"”\']+)["”\']', window, re.IGNORECASE)
        if alias_match:
            aliases.append(alias_match.group(1).strip())

        role = default_role
        w_lower = window.lower()
        if "driver" in w_lower or "courier" in w_lower:
            role = "Transport Courier"
        elif "logistics" in w_lower or "warehouse" in w_lower:
            role = "Logistics Coordinator"
        elif "broker" in w_lower or "forex" in w_lower or "hawala" in w_lower:
            role = "Hawala Broker"
        elif "ghost" in w_lower or "enforcer" in w_lower or "extortion" in w_lower:
            role = "Enforcer & Security"
        elif "mastermind" in w_lower or "don" in w_lower:
            role = "Syndicate Mastermind"
        elif "director" in w_lower:
            role = "Shell Company Director"
        elif "inspector" in w_lower or "acp" in w_lower or "analyst" in w_lower:
            role = "Investigating Officer"

        return role, aliases

    @staticmethod
    def _calculate_risk_score(entity_type: EntityType, role: Optional[str]) -> float:
        """
        Analytical baseline risk scoring strictly between 0 and 100.
        Law enforcement officers receive 0 risk score.
        """
        if role == "Investigating Officer":
            return 0.0

        if entity_type == EntityType.PERSON:
            if role == "Syndicate Mastermind":
                return 95.0
            if role in {"Enforcer & Security", "Hawala Broker"}:
                return 88.0
            if role == "Logistics Coordinator":
                return 82.0
            if role in {"Transport Courier", "Accused"}:
                return 75.0
            return 70.0
        elif entity_type == EntityType.BANK_ACCOUNT:
            return 88.0
        elif entity_type == EntityType.PHONE:
            return 80.0
        elif entity_type == EntityType.VEHICLE:
            return 75.0
        elif entity_type == EntityType.ORGANIZATION:
            return 82.0
        elif entity_type == EntityType.LOCATION:
            return 75.0
        return 50.0
