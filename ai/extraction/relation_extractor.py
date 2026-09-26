"""
VERITAS - Semantic Relationship Extractor
Extracts multi-relational edges and evidentiary provenance from structured records
(CDRs, Transactions) and unstructured forensic narratives (FIRs, surveillance logs).
Strictly adheres to the 12 approved relationship types in docs/GRAPH_SCHEMA.md.
"""
import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from ai.ingestion.csv_parser import CDRRecord, TransactionRecord
from ai.ingestion.document_parser import DocumentRecord
from ai.schemas.entity import Entity, EntityType
from ai.schemas.relationship import Provenance, Relationship, RelationshipType


class RelationshipIDGenerator:
    """
    Generates predictable, deterministic relationship IDs (R001, R002, ...)
    ensuring identical events within a source produce stable identifiers.
    """

    def __init__(self, start_idx: int = 1):
        self._start_idx = start_idx
        self._counter = start_idx - 1
        self._registry: Dict[str, str] = {}

    def get_id(
        self,
        source_id: str,
        source: str,
        target: str,
        rel_type: Union[RelationshipType, str],
        event_id: Optional[str] = None
    ) -> str:
        # If an explicit event_id is given (e.g. CDR1001, TX1001), distinguish it
        key = f"{source_id}:{event_id or ''}:{source}:{target}:{rel_type}"
        if key in self._registry:
            return self._registry[key]

        self._counter += 1
        rid = f"R{self._counter:03d}"
        self._registry[key] = rid
        return rid

    def reset(self):
        self._counter = self._start_idx - 1
        self._registry.clear()


class RelationshipExtractor:
    """
    Extracts canonical multi-relational edges using:
    1. CDR records -> CALLED (Phone -> Phone)
    2. Transaction records -> TRANSACTED_WITH (BankAccount -> BankAccount)
    3. Document text -> Semantic relationships among recognized entities:
       USES_PHONE, OWNS, OPERATES, LOCATED_AT, ASSOCIATED_WITH,
       SUPERVISES, COORDINATES_WITH, CONTROLS, MEMBER_OF, OWNS_ACCOUNT.
    """

    def __init__(self, id_generator: Optional[RelationshipIDGenerator] = None):
        self.id_generator = id_generator or RelationshipIDGenerator()

    def extract_from_record(
        self,
        record: Any,
        entities: Optional[List[Entity]] = None
    ) -> List[Relationship]:
        """
        Dispatches relationship extraction according to record type.
        """
        if isinstance(record, CDRRecord):
            return self._extract_from_cdr(record, entities)
        elif isinstance(record, TransactionRecord):
            return self._extract_from_transaction(record, entities)
        elif isinstance(record, DocumentRecord):
            return self._extract_from_document(record, entities or [])
        else:
            raise TypeError(f"Unsupported record type: {type(record)}")

    def extract(
        self,
        records: List[Any],
        entities: Optional[List[Entity]] = None
    ) -> List[Relationship]:
        """
        Extracts relationships across a batch of records.
        """
        all_relationships: List[Relationship] = []
        entity_list = entities or []
        for rec in records:
            all_relationships.extend(self.extract_from_record(rec, entity_list))
        return all_relationships

    # -----------------------------------------------------------------
    # Structured Extractors: CDR & Transactions
    # -----------------------------------------------------------------

    def _extract_from_cdr(
        self,
        record: CDRRecord,
        entities: Optional[List[Entity]] = None
    ) -> List[Relationship]:
        """
        Produces Phone -> CALLED -> Phone relationship from a CDR row.
        """
        caller_id = record.caller_normalized
        receiver_id = record.receiver_normalized

        # Map to entity ID if entities are provided
        if entities:
            for ent in entities:
                if ent.type == EntityType.PHONE:
                    if ent.label == record.caller_normalized or ent.name == record.caller_normalized:
                        caller_id = ent.id
                    if ent.label == record.receiver_normalized or ent.name == record.receiver_normalized:
                        receiver_id = ent.id

        if caller_id == receiver_id:
            # Self-calls are invalid in relationship schema
            return []

        rel_id = self.id_generator.get_id(
            source_id="CDR-LOG",
            source=caller_id,
            target=receiver_id,
            rel_type=RelationshipType.CALLED,
            event_id=record.call_id
        )

        snippet = (
            f"Call record {record.call_id} from {record.caller_raw} to {record.receiver_raw} "
            f"lasting {record.duration_sec}s via tower {record.cell_tower_id}."
        )

        provenance = Provenance(
            source_id=record.call_id,
            source_type="TELECOM_CDR",
            snippet=snippet,
            confidence=1.0,
        )

        rel = Relationship(
            id=rel_id,
            source=caller_id,
            target=receiver_id,
            type=RelationshipType.CALLED,
            directed=True,
            weight=1.0,
            timestamp=record.normalized_timestamp or record.timestamp_raw,
            provenance=provenance,
        )
        return [rel]

    def _extract_from_transaction(
        self,
        record: TransactionRecord,
        entities: Optional[List[Entity]] = None
    ) -> List[Relationship]:
        """
        Produces BankAccount -> TRANSACTED_WITH -> BankAccount from a transaction row.
        """
        sender_id = record.sender_account_normalized
        receiver_id = record.receiver_account_normalized

        # Map to entity ID if entities are provided
        if entities:
            for ent in entities:
                if ent.type == EntityType.BANK_ACCOUNT:
                    if ent.label == record.sender_account_normalized or ent.name == record.sender_account_normalized:
                        sender_id = ent.id
                    if ent.label == record.receiver_account_normalized or ent.name == record.receiver_account_normalized:
                        receiver_id = ent.id

        if sender_id == receiver_id:
            return []

        rel_id = self.id_generator.get_id(
            source_id="BANK-TX",
            source=sender_id,
            target=receiver_id,
            rel_type=RelationshipType.TRANSACTED_WITH,
            event_id=record.transaction_id
        )

        snippet = (
            f"Financial transaction {record.transaction_id} of {record.currency} {record.amount:,.2f} "
            f"from {record.sender_account_raw} to {record.receiver_account_raw} via {record.payment_channel}."
        )

        provenance = Provenance(
            source_id=record.transaction_id,
            source_type="BANK_LEDGER",
            snippet=snippet,
            confidence=1.0,
        )

        rel = Relationship(
            id=rel_id,
            source=sender_id,
            target=receiver_id,
            type=RelationshipType.TRANSACTED_WITH,
            directed=True,
            weight=record.amount,
            timestamp=record.normalized_timestamp or record.timestamp_raw,
            provenance=provenance,
        )
        return [rel]

    # -----------------------------------------------------------------
    # Text-Based Relationship Extraction
    # -----------------------------------------------------------------

    def _extract_from_document(
        self,
        doc: DocumentRecord,
        entities: List[Entity]
    ) -> List[Relationship]:
        """
        Extracts semantic relationships between entities explicitly referenced in document text.
        Applies sentence-level syntactic patterns and suppresses duplicate edges within the document.
        """
        text = doc.raw_text
        source_id = doc.source_id
        source_type = doc.document_type
        timestamp = doc.normalized_timestamp

        # Index available entities by type for efficient lookup
        persons = [e for e in entities if e.type == EntityType.PERSON]
        phones = [e for e in entities if e.type == EntityType.PHONE]
        vehicles = [e for e in entities if e.type == EntityType.VEHICLE]
        locations = [e for e in entities if e.type == EntityType.LOCATION]
        orgs = [e for e in entities if e.type == EntityType.ORGANIZATION]
        accounts = [e for e in entities if e.type == EntityType.BANK_ACCOUNT]

        relationships: List[Relationship] = []
        seen_keys: Set[Tuple[str, str, RelationshipType]] = set()

        sentences = self._split_into_sentences(text)

        for sent in sentences:
            # 1. Person -> Phone (USES_PHONE)
            for p in persons:
                for ph in phones:
                    if self._entity_in_sentence(p, sent) and self._entity_in_sentence(ph, sent):
                        if self._matches_uses_phone(sent):
                            key = (p.id, ph.id, RelationshipType.USES_PHONE)
                            if key not in seen_keys:
                                seen_keys.add(key)
                                rel = self._create_relationship(
                                    source=p.id,
                                    target=ph.id,
                                    rel_type=RelationshipType.USES_PHONE,
                                    source_id=source_id,
                                    source_type=source_type,
                                    snippet=sent.strip(),
                                    confidence=0.96,
                                    weight=1.0,
                                    timestamp=timestamp
                                )
                                relationships.append(rel)

            # 2. Person -> Vehicle (OWNS or OPERATES)
            for p in persons:
                for v in vehicles:
                    if self._entity_in_sentence(p, sent) and self._entity_in_sentence(v, sent):
                        is_operates, is_owns = self._matches_vehicle_relationship(sent)
                        if is_operates:
                            key = (p.id, v.id, RelationshipType.OPERATES)
                            if key not in seen_keys:
                                seen_keys.add(key)
                                rel = self._create_relationship(
                                    source=p.id,
                                    target=v.id,
                                    rel_type=RelationshipType.OPERATES,
                                    source_id=source_id,
                                    source_type=source_type,
                                    snippet=sent.strip(),
                                    confidence=0.95,
                                    weight=1.0,
                                    timestamp=timestamp
                                )
                                relationships.append(rel)
                        elif is_owns:
                            key = (p.id, v.id, RelationshipType.OWNS)
                            if key not in seen_keys:
                                seen_keys.add(key)
                                rel = self._create_relationship(
                                    source=p.id,
                                    target=v.id,
                                    rel_type=RelationshipType.OWNS,
                                    source_id=source_id,
                                    source_type=source_type,
                                    snippet=sent.strip(),
                                    confidence=0.95,
                                    weight=1.0,
                                    timestamp=timestamp
                                )
                                relationships.append(rel)

            # 3. Person -> Location (LOCATED_AT)
            for p in persons:
                for loc in locations:
                    if self._entity_in_sentence(p, sent) and self._entity_in_sentence(loc, sent):
                        if self._matches_located_at(sent):
                            key = (p.id, loc.id, RelationshipType.LOCATED_AT)
                            if key not in seen_keys:
                                seen_keys.add(key)
                                rel = self._create_relationship(
                                    source=p.id,
                                    target=loc.id,
                                    rel_type=RelationshipType.LOCATED_AT,
                                    source_id=source_id,
                                    source_type=source_type,
                                    snippet=sent.strip(),
                                    confidence=0.92,
                                    weight=1.0,
                                    timestamp=timestamp
                                )
                                relationships.append(rel)

            # 4. Person -> Organization (CONTROLS or MEMBER_OF)
            for p in persons:
                for org in orgs:
                    if self._entity_in_sentence(p, sent) and self._entity_in_sentence(org, sent):
                        is_controls, is_member = self._matches_org_relationship(sent)
                        if is_controls:
                            key = (p.id, org.id, RelationshipType.CONTROLS)
                            if key not in seen_keys:
                                seen_keys.add(key)
                                rel = self._create_relationship(
                                    source=p.id,
                                    target=org.id,
                                    rel_type=RelationshipType.CONTROLS,
                                    source_id=source_id,
                                    source_type=source_type,
                                    snippet=sent.strip(),
                                    confidence=0.94,
                                    weight=1.0,
                                    timestamp=timestamp
                                )
                                relationships.append(rel)
                        elif is_member:
                            key = (p.id, org.id, RelationshipType.MEMBER_OF)
                            if key not in seen_keys:
                                seen_keys.add(key)
                                rel = self._create_relationship(
                                    source=p.id,
                                    target=org.id,
                                    rel_type=RelationshipType.MEMBER_OF,
                                    source_id=source_id,
                                    source_type=source_type,
                                    snippet=sent.strip(),
                                    confidence=0.92,
                                    weight=1.0,
                                    timestamp=timestamp
                                )
                                relationships.append(rel)

            # 5. Person / Org -> BankAccount (OWNS_ACCOUNT)
            owners = persons + orgs
            for owner in owners:
                for acc in accounts:
                    if self._entity_in_sentence(owner, sent) and self._entity_in_sentence(acc, sent):
                        if self._matches_owns_account(sent):
                            key = (owner.id, acc.id, RelationshipType.OWNS_ACCOUNT)
                            if key not in seen_keys:
                                seen_keys.add(key)
                                rel = self._create_relationship(
                                    source=owner.id,
                                    target=acc.id,
                                    rel_type=RelationshipType.OWNS_ACCOUNT,
                                    source_id=source_id,
                                    source_type=source_type,
                                    snippet=sent.strip(),
                                    confidence=0.95,
                                    weight=1.0,
                                    timestamp=timestamp
                                )
                                relationships.append(rel)

            # 6. Person <-> Person (SUPERVISES, COORDINATES_WITH, ASSOCIATED_WITH)
            if len(persons) >= 2:
                for i in range(len(persons)):
                    for j in range(len(persons)):
                        if i == j:
                            continue
                        p1 = persons[i]
                        p2 = persons[j]
                        if self._entity_in_sentence(p1, sent) and self._entity_in_sentence(p2, sent):
                            rel_type, conf, is_reversed = self._matches_interpersonal(sent, p1, p2)
                            if rel_type:
                                src = p2.id if is_reversed else p1.id
                                tgt = p1.id if is_reversed else p2.id
                                key = (src, tgt, rel_type)
                                if key not in seen_keys:
                                    seen_keys.add(key)
                                    rel = self._create_relationship(
                                        source=src,
                                        target=tgt,
                                        rel_type=rel_type,
                                        source_id=source_id,
                                        source_type=source_type,
                                        snippet=sent.strip(),
                                        confidence=conf,
                                        weight=0.90,
                                        timestamp=timestamp
                                    )
                                    relationships.append(rel)

        return relationships

    # -----------------------------------------------------------------
    # Linguistic Trigger Checkers
    # -----------------------------------------------------------------

    @staticmethod
    def _split_into_sentences(text: str) -> List[str]:
        # Split on sentence terminals or bullet dashes
        raw_sentences = re.split(r"(?<=[.!?])\s+|\n+|- \b", text)
        return [s.strip() for s in raw_sentences if len(s.strip()) > 10]

    @staticmethod
    def _entity_in_sentence(entity: Entity, sentence: str) -> bool:
        """Checks if entity label, name, or any alias appears in sentence."""
        candidates = [entity.label]
        if entity.name and entity.name != entity.label:
            candidates.append(entity.name)
        candidates.extend(entity.aliases)

        s_lower = sentence.lower()
        for cand in candidates:
            # Handle vehicle registration without model description
            c_clean = re.sub(r"\s*\(.*?\)", "", cand).strip().lower()
            if len(c_clean) > 2 and c_clean in s_lower:
                return True
        return False

    @staticmethod
    def _matches_uses_phone(sentence: str) -> bool:
        triggers = [
            "phone", "msisdn", "possession", "recovered", "handset", "device",
            "number", "line", "terminal", "sim", "operated by"
        ]
        s_lower = sentence.lower()
        return any(t in s_lower for t in triggers)

    @staticmethod
    def _matches_vehicle_relationship(sentence: str) -> Tuple[bool, bool]:
        s_lower = sentence.lower()
        operates_triggers = ["driver", "driving", "driven by", "intercepted", "courier", "operates"]
        owns_triggers = ["registered to", "owns", "owner", "luxury sedan", "fleet"]

        is_operates = any(t in s_lower for t in operates_triggers)
        is_owns = any(t in s_lower for t in owns_triggers)
        return is_operates, is_owns

    @staticmethod
    def _matches_located_at(sentence: str) -> bool:
        triggers = [
            "at", "arrived", "outside", "inside", "warehouse", "premises", "residence",
            "border", "hub", "godown", "vault", "checkpoint", "observed"
        ]
        s_lower = sentence.lower()
        return any(t in s_lower for t in triggers)

    @staticmethod
    def _matches_org_relationship(sentence: str) -> Tuple[bool, bool]:
        s_lower = sentence.lower()
        controls_triggers = [
            "beneficiary", "beneficial owner", "proprietor", "controls", "overseen by",
            "shareholder", "director & primary", "non-executive director"
        ]
        member_triggers = [
            "director", "managing director", "holding", "member", "manager", "operated as"
        ]
        is_controls = any(t in s_lower for t in controls_triggers)
        is_member = any(t in s_lower for t in member_triggers)
        return is_controls, is_member

    @staticmethod
    def _matches_owns_account(sentence: str) -> bool:
        triggers = ["account", "acc-", "deposits", "wired out to", "registered under", "received"]
        s_lower = sentence.lower()
        return any(t in s_lower for t in triggers)

    @staticmethod
    def _matches_interpersonal(
        sentence: str,
        p1: Entity,
        p2: Entity
    ) -> Tuple[Optional[RelationshipType], float, bool]:
        """
        Determines criminal hierarchy or coordination between two suspects.
        Returns (RelationshipType, confidence, is_reversed).
        """
        s_lower = sentence.lower()

        # SUPERVISES: e.g. Verma confirmed Rajesh as immediate handler / consignment received from Rajesh
        if any(t in s_lower for t in ["handler", "received from", "dispatched", "supervises", "subordinate"]):
            # In "received consignment from Rajesh", Rajesh supervises Arjun
            if "received from" in s_lower or "handler" in s_lower:
                # If p2 appears after "from" or "managed by", p2 supervises p1
                return RelationshipType.SUPERVISES, 0.92, True
            return RelationshipType.SUPERVISES, 0.90, False

        # COORDINATES_WITH: e.g. calls with coordinator / coordination over encrypted lines
        if any(t in s_lower for t in ["coordination", "coordinator", "dispatches", "short-duration calls", "encrypted lines"]):
            return RelationshipType.COORDINATES_WITH, 0.88, False

        # ASSOCIATED_WITH: e.g. meeting occurred / accompanied by / closed-door meeting
        if any(t in s_lower for t in ["meeting", "accompanied by", "conspiracy", "associated with", "syndicate"]):
            return RelationshipType.ASSOCIATED_WITH, 0.85, False

        return None, 0.0, False

    def _create_relationship(
        self,
        source: str,
        target: str,
        rel_type: RelationshipType,
        source_id: str,
        source_type: str,
        snippet: str,
        confidence: float,
        weight: float = 1.0,
        timestamp: Optional[str] = None
    ) -> Relationship:
        rel_id = self.id_generator.get_id(
            source_id=source_id,
            source=source,
            target=target,
            rel_type=rel_type
        )

        provenance = Provenance(
            source_id=source_id,
            source_type=source_type,
            snippet=snippet,
            confidence=confidence,
        )

        return Relationship(
            id=rel_id,
            source=source,
            target=target,
            type=rel_type,
            directed=True,
            weight=weight,
            timestamp=timestamp,
            provenance=provenance,
        )
