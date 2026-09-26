"""
VERITAS - Entity Resolution & Canonical Identity Deduplication
Multi-signal deterministic matching and identity consolidation across heterogenous data sources.
Conforms strictly to docs/DATA_SCHEMA.md and docs/ARCHITECTURE.md.
"""
import re
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, ConfigDict, Field

from ai.ingestion.preprocessing import (
    normalize_account_id,
    normalize_name,
    normalize_org_name,
    normalize_phone_number,
    normalize_vehicle_plate,
)
from ai.resolution.similarity import (
    jaro_winkler_similarity,
    levenshtein_similarity,
    phonetic_match,
    token_overlap_ratio,
)
from ai.schemas.entity import Entity, EntityType
from ai.schemas.relationship import Relationship


class MatchDecision(str, Enum):
    """
    Controlled match classification boundaries.
    """
    MATCH = "MATCH"
    UNCERTAIN = "UNCERTAIN"
    NO_MATCH = "NO_MATCH"


class ResolutionEvidence(BaseModel):
    """
    Explainable match evidence between two entity candidates.
    Every merge decision is supported by an audit trail of signals.
    """
    model_config = ConfigDict(extra="allow")

    candidate_a: str = Field(..., description="Entity ID or display label of Candidate A")
    candidate_b: str = Field(..., description="Entity ID or display label of Candidate B")
    entity_type: EntityType = Field(..., description="Entity category of the candidates")
    decision: MatchDecision = Field(..., description="Resolution classification: MATCH, UNCERTAIN, or NO_MATCH")
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence score bounded in [0.0, 1.0]")
    reasons: List[str] = Field(default_factory=list, description="Specific deterministic matching signals observed")


class EntityResolver:
    """
    Entity Resolution Engine.
    - Evaluates pairs of entities of identical type.
    - Enforces strict deterministic matching for Phones, Vehicles, BankAccounts.
    - Applies multi-signal matching (name similarity, phonetic codes, alias overlap, contextual cues)
      for Persons, Organizations, and Locations.
    - Emits explainable ResolutionEvidence.
    - Consolidates merged entities preserving 100% of aliases, source records, and maximum risk score.
    - Rewrites relationship endpoints to canonical IDs while preserving distinct structured events.
    """

    MATCH_THRESHOLD: float = 0.85
    UNCERTAIN_THRESHOLD: float = 0.60

    def __init__(
        self,
        match_threshold: float = MATCH_THRESHOLD,
        uncertain_threshold: float = UNCERTAIN_THRESHOLD,
    ):
        self.match_threshold = match_threshold
        self.uncertain_threshold = uncertain_threshold

    def compare_candidates(self, ent_a: Entity, ent_b: Entity) -> ResolutionEvidence:
        """
        Compares two entities and produces explainable ResolutionEvidence.
        """
        # Entity types must match
        if ent_a.type != ent_b.type:
            return ResolutionEvidence(
                candidate_a=ent_a.id,
                candidate_b=ent_b.id,
                entity_type=ent_a.type,
                decision=MatchDecision.NO_MATCH,
                score=0.0,
                reasons=[f"Mismatched entity types: {ent_a.type.value} vs {ent_b.type.value}."],
            )

        etype = ent_a.type

        # Dispatch rule-specific comparison
        if etype == EntityType.PHONE:
            return self._compare_phones(ent_a, ent_b)
        elif etype == EntityType.VEHICLE:
            return self._compare_vehicles(ent_a, ent_b)
        elif etype == EntityType.BANK_ACCOUNT:
            return self._compare_bank_accounts(ent_a, ent_b)
        elif etype == EntityType.PERSON:
            return self._compare_persons(ent_a, ent_b)
        elif etype == EntityType.ORGANIZATION:
            return self._compare_organizations(ent_a, ent_b)
        elif etype == EntityType.LOCATION:
            return self._compare_locations(ent_a, ent_b)

        return ResolutionEvidence(
            candidate_a=ent_a.id,
            candidate_b=ent_b.id,
            entity_type=etype,
            decision=MatchDecision.NO_MATCH,
            score=0.0,
            reasons=["Unsupported entity type."],
        )

    # -----------------------------------------------------------------
    # Exact-Match Entity Categories (Phone, Vehicle, BankAccount)
    # -----------------------------------------------------------------

    def _compare_phones(self, a: Entity, b: Entity) -> ResolutionEvidence:
        norm_a = normalize_phone_number(a.label) or normalize_phone_number(a.id)
        norm_b = normalize_phone_number(b.label) or normalize_phone_number(b.id)

        reasons = []
        if norm_a and norm_b and norm_a == norm_b:
            reasons.append(f"Exact normalized E.164 phone number match: {norm_a}.")
            return ResolutionEvidence(
                candidate_a=a.id,
                candidate_b=b.id,
                entity_type=EntityType.PHONE,
                decision=MatchDecision.MATCH,
                score=1.0,
                reasons=reasons,
            )

        # Check aliases for exact phone overlap
        aliases_a = {normalize_phone_number(x) for x in a.aliases if normalize_phone_number(x)}
        aliases_b = {normalize_phone_number(x) for x in b.aliases if normalize_phone_number(x)}
        if norm_a:
            aliases_a.add(norm_a)
        if norm_b:
            aliases_b.add(norm_b)

        overlap = aliases_a.intersection(aliases_b)
        if overlap:
            matched_val = sorted(list(overlap))[0]
            reasons.append(f"Exact phone number match across alias records: {matched_val}.")
            return ResolutionEvidence(
                candidate_a=a.id,
                candidate_b=b.id,
                entity_type=EntityType.PHONE,
                decision=MatchDecision.MATCH,
                score=1.0,
                reasons=reasons,
            )

        reasons.append("Distinct phone numbers; fuzzy matching is prohibited for telecommunications.")
        return ResolutionEvidence(
            candidate_a=a.id,
            candidate_b=b.id,
            entity_type=EntityType.PHONE,
            decision=MatchDecision.NO_MATCH,
            score=0.0,
            reasons=reasons,
        )

    def _compare_vehicles(self, a: Entity, b: Entity) -> ResolutionEvidence:
        norm_a = normalize_vehicle_plate(a.label)
        norm_b = normalize_vehicle_plate(b.label)

        # Strip any parenthetical descriptor like "(BMW 7-Series)"
        clean_plate_a = norm_a.split("(")[0].strip() if norm_a else ""
        clean_plate_b = norm_b.split("(")[0].strip() if norm_b else ""

        reasons = []
        if clean_plate_a and clean_plate_b and clean_plate_a == clean_plate_b:
            reasons.append(f"Exact normalized vehicle registration plate match: {clean_plate_a}.")
            return ResolutionEvidence(
                candidate_a=a.id,
                candidate_b=b.id,
                entity_type=EntityType.VEHICLE,
                decision=MatchDecision.MATCH,
                score=1.0,
                reasons=reasons,
            )

        reasons.append("Distinct vehicle registration plates; fuzzy plate matching is prohibited.")
        return ResolutionEvidence(
            candidate_a=a.id,
            candidate_b=b.id,
            entity_type=EntityType.VEHICLE,
            decision=MatchDecision.NO_MATCH,
            score=0.0,
            reasons=reasons,
        )

    def _compare_bank_accounts(self, a: Entity, b: Entity) -> ResolutionEvidence:
        norm_a = normalize_account_id(a.label)
        norm_b = normalize_account_id(b.label)

        reasons = []
        if norm_a and norm_b and norm_a == norm_b:
            reasons.append(f"Exact normalized bank account identifier match: {norm_a}.")
            return ResolutionEvidence(
                candidate_a=a.id,
                candidate_b=b.id,
                entity_type=EntityType.BANK_ACCOUNT,
                decision=MatchDecision.MATCH,
                score=1.0,
                reasons=reasons,
            )

        reasons.append("Distinct financial bank accounts; fuzzy account matching is prohibited.")
        return ResolutionEvidence(
            candidate_a=a.id,
            candidate_b=b.id,
            entity_type=EntityType.BANK_ACCOUNT,
            decision=MatchDecision.NO_MATCH,
            score=0.0,
            reasons=reasons,
        )

    # -----------------------------------------------------------------
    # Multi-Signal Entities (Person, Organization, Location)
    # -----------------------------------------------------------------

    def _compare_persons(self, a: Entity, b: Entity) -> ResolutionEvidence:
        name_a = normalize_name(a.label)
        name_b = normalize_name(b.label)

        reasons = []
        score = 0.0

        # Exact normalized label match
        if name_a and name_b and name_a.lower() == name_b.lower():
            reasons.append(f"Exact normalized name match: '{name_a}'.")
            return ResolutionEvidence(
                candidate_a=a.id,
                candidate_b=b.id,
                entity_type=EntityType.PERSON,
                decision=MatchDecision.MATCH,
                score=1.0,
                reasons=reasons,
            )

        # Check known aliases
        aliases_a = {x.strip().lower() for x in a.aliases if x.strip()}
        aliases_b = {x.strip().lower() for x in b.aliases if x.strip()}

        # Check if label of A matches an alias of B, or vice-versa, or direct alias intersection
        direct_alias_match = False
        if name_a.lower() in aliases_b:
            reasons.append(f"Candidate A name '{name_a}' is a known alias of Candidate B.")
            direct_alias_match = True
        elif name_b.lower() in aliases_a:
            reasons.append(f"Candidate B name '{name_b}' is a known alias of Candidate A.")
            direct_alias_match = True
        elif aliases_a.intersection(aliases_b):
            common_alias = sorted(list(aliases_a.intersection(aliases_b)))[0]
            reasons.append(f"Exact known alias overlap: '{common_alias}'.")
            direct_alias_match = True

        if direct_alias_match:
            return ResolutionEvidence(
                candidate_a=a.id,
                candidate_b=b.id,
                entity_type=EntityType.PERSON,
                decision=MatchDecision.MATCH,
                score=0.95,
                reasons=reasons,
            )

        # Check shared contextual attributes: phone number or account
        shared_phone = self._check_shared_attribute(a, b, ["primary_line", "phone", "msisdn"])
        shared_account = self._check_shared_attribute(a, b, ["account", "bank_account", "account_id"])

        # Linguistic & phonetic metrics
        jw = jaro_winkler_similarity(name_a, name_b)
        lev = levenshtein_similarity(name_a, name_b)
        overlap = token_overlap_ratio(name_a, name_b)
        phon_match = phonetic_match(name_a, name_b)

        # Surnames / tokens check
        tokens_a = [t.lower() for t in re.findall(r"\b\w+\b", name_a)]
        tokens_b = [t.lower() for t in re.findall(r"\b\w+\b", name_b)]

        # Guard against merging distinct people who merely share a common surname
        # e.g. "Rajesh Kumar" vs "Rakesh Kumar" -> token overlap is 0.5 (Kumar), but distinct first names!
        is_same_surname = (
            len(tokens_a) >= 2 and len(tokens_b) >= 2 and
            tokens_a[-1] == tokens_b[-1]
        )
        first_names_match = (
            tokens_a[0] == tokens_b[0] or
            phonetic_match(tokens_a[0], tokens_b[0]) or
            levenshtein_similarity(tokens_a[0], tokens_b[0]) >= 0.85
        )

        if is_same_surname and not first_names_match and not (shared_phone or shared_account):
            reasons.append(
                f"Distinct first names ('{tokens_a[0]}' vs '{tokens_b[0]}') sharing surname '{tokens_a[-1]}'; "
                "not merged without strong corroborating identifiers."
            )
            # Cap score below uncertain threshold if first names are distinct
            score = min(0.40, jw * 0.5)
            return ResolutionEvidence(
                candidate_a=a.id,
                candidate_b=b.id,
                entity_type=EntityType.PERSON,
                decision=MatchDecision.NO_MATCH,
                score=round(score, 3),
                reasons=reasons,
            )

        # If shared strong identifier exists
        if shared_phone:
            reasons.append(f"Shared primary phone number: {shared_phone}.")
            score += 0.50
        if shared_account:
            reasons.append(f"Shared financial account: {shared_account}.")
            score += 0.50

        # High string similarity (minor spelling variations like Vikram Singhania vs Vikramaditya Singhania)
        if jw >= 0.88 or lev >= 0.85:
            reasons.append(f"High name string similarity (Jaro-Winkler: {jw:.2f}, Levenshtein: {lev:.2f}).")
            score += (jw * 0.50)
        elif jw >= 0.75:
            reasons.append(f"Moderate name string similarity (Jaro-Winkler: {jw:.2f}).")
            score += (jw * 0.35)

        if phon_match:
            reasons.append("Phonetic soundex/metaphone agreement on name.")
            score += 0.20

        if overlap >= 0.5 and (not is_same_surname or first_names_match):
            reasons.append(f"Substantial name token overlap ratio: {overlap:.2f}.")
            score += (overlap * 0.20)

        # Normalize score bounds
        score = min(1.0, max(0.0, score))

        if score >= self.match_threshold:
            decision = MatchDecision.MATCH
        elif score >= self.uncertain_threshold:
            decision = MatchDecision.UNCERTAIN
            reasons.append("Score falls within ambiguous confidence window [0.60, 0.85); flagged for analyst review.")
        else:
            decision = MatchDecision.NO_MATCH
            if not reasons:
                reasons.append("Insufficient name similarity and no corroborating forensic identifiers.")

        return ResolutionEvidence(
            candidate_a=a.id,
            candidate_b=b.id,
            entity_type=EntityType.PERSON,
            decision=decision,
            score=round(score, 3),
            reasons=reasons,
        )

    def _compare_organizations(self, a: Entity, b: Entity) -> ResolutionEvidence:
        org_a = normalize_org_name(a.label)
        org_b = normalize_org_name(b.label)

        reasons = []
        if org_a.lower() == org_b.lower():
            reasons.append(f"Exact normalized organization name match: '{org_a}'.")
            return ResolutionEvidence(
                candidate_a=a.id,
                candidate_b=b.id,
                entity_type=EntityType.ORGANIZATION,
                decision=MatchDecision.MATCH,
                score=1.0,
                reasons=reasons,
            )

        # Alias check
        aliases_a = {x.strip().lower() for x in a.aliases}
        aliases_b = {x.strip().lower() for x in b.aliases}
        if org_a.lower() in aliases_b or org_b.lower() in aliases_a or aliases_a.intersection(aliases_b):
            reasons.append("Organization match via alias registry.")
            return ResolutionEvidence(
                candidate_a=a.id,
                candidate_b=b.id,
                entity_type=EntityType.ORGANIZATION,
                decision=MatchDecision.MATCH,
                score=0.95,
                reasons=reasons,
            )

        # Check core corporate stem (e.g. "Astra Logistics Ltd" vs "Astra Logistics")
        stem_a = re.sub(r"\b(ltd|pvt|inc|limited|private|enterprises|holdings|corp)\b", "", org_a.lower()).strip()
        stem_b = re.sub(r"\b(ltd|pvt|inc|limited|private|enterprises|holdings|corp)\b", "", org_b.lower()).strip()

        if stem_a and stem_b and stem_a == stem_b:
            reasons.append(f"Identical corporate core stem: '{stem_a}'.")
            return ResolutionEvidence(
                candidate_a=a.id,
                candidate_b=b.id,
                entity_type=EntityType.ORGANIZATION,
                decision=MatchDecision.MATCH,
                score=0.92,
                reasons=reasons,
            )

        jw = jaro_winkler_similarity(org_a, org_b)
        if jw >= 0.90:
            reasons.append(f"High organization string similarity (Jaro-Winkler: {jw:.2f}).")
            return ResolutionEvidence(
                candidate_a=a.id,
                candidate_b=b.id,
                entity_type=EntityType.ORGANIZATION,
                decision=MatchDecision.MATCH,
                score=round(jw, 3),
                reasons=reasons,
            )
        elif jw >= 0.70:
            reasons.append(f"Ambiguous organization similarity (Jaro-Winkler: {jw:.2f}).")
            return ResolutionEvidence(
                candidate_a=a.id,
                candidate_b=b.id,
                entity_type=EntityType.ORGANIZATION,
                decision=MatchDecision.UNCERTAIN,
                score=round(jw, 3),
                reasons=reasons,
            )

        reasons.append("Distinct organization entities.")
        return ResolutionEvidence(
            candidate_a=a.id,
            candidate_b=b.id,
            entity_type=EntityType.ORGANIZATION,
            decision=MatchDecision.NO_MATCH,
            score=round(jw, 3),
            reasons=reasons,
        )

    def _compare_locations(self, a: Entity, b: Entity) -> ResolutionEvidence:
        loc_a = normalize_name(a.label)
        loc_b = normalize_name(b.label)

        reasons = []
        if loc_a.lower() == loc_b.lower():
            reasons.append(f"Exact normalized location match: '{loc_a}'.")
            return ResolutionEvidence(
                candidate_a=a.id,
                candidate_b=b.id,
                entity_type=EntityType.LOCATION,
                decision=MatchDecision.MATCH,
                score=1.0,
                reasons=reasons,
            )

        # Distinct generic cities/states should never be merged
        # e.g. "Noida" vs "New Delhi"
        generic_locations = {"noida", "new delhi", "delhi", "south delhi", "old delhi", "ghaziabad"}
        if loc_a.lower() in generic_locations and loc_b.lower() in generic_locations and loc_a.lower() != loc_b.lower():
            reasons.append(f"Distinct regional jurisdictions ('{loc_a}' vs '{loc_b}'); merging prohibited.")
            return ResolutionEvidence(
                candidate_a=a.id,
                candidate_b=b.id,
                entity_type=EntityType.LOCATION,
                decision=MatchDecision.NO_MATCH,
                score=0.0,
                reasons=reasons,
            )

        # Check sub-district inclusion (e.g. "Okhla Industrial Area, Phase II" vs "Okhla Industrial Area")
        if loc_a.lower() in loc_b.lower() or loc_b.lower() in loc_a.lower():
            reasons.append(f"Nested location hub inclusion ('{loc_a}' / '{loc_b}').")
            return ResolutionEvidence(
                candidate_a=a.id,
                candidate_b=b.id,
                entity_type=EntityType.LOCATION,
                decision=MatchDecision.MATCH,
                score=0.90,
                reasons=reasons,
            )

        jw = jaro_winkler_similarity(loc_a, loc_b)
        if jw >= 0.88:
            reasons.append(f"High location name similarity (Jaro-Winkler: {jw:.2f}).")
            return ResolutionEvidence(
                candidate_a=a.id,
                candidate_b=b.id,
                entity_type=EntityType.LOCATION,
                decision=MatchDecision.MATCH,
                score=round(jw, 3),
                reasons=reasons,
            )
        elif jw >= 0.65:
            reasons.append(f"Uncertain location proximity or phrasing: '{loc_a}' vs '{loc_b}'.")
            return ResolutionEvidence(
                candidate_a=a.id,
                candidate_b=b.id,
                entity_type=EntityType.LOCATION,
                decision=MatchDecision.UNCERTAIN,
                score=round(jw, 3),
                reasons=reasons,
            )

        reasons.append("Distinct geographical locations.")
        return ResolutionEvidence(
            candidate_a=a.id,
            candidate_b=b.id,
            entity_type=EntityType.LOCATION,
            decision=MatchDecision.NO_MATCH,
            score=round(jw, 3),
            reasons=reasons,
        )

    # -----------------------------------------------------------------
    # Batch Resolution & Consolidation
    # -----------------------------------------------------------------

    def resolve(
        self,
        entities: List[Entity]
    ) -> Tuple[List[Entity], List[ResolutionEvidence], Dict[str, str]]:
        """
        Performs pairwise entity resolution and connected-component clustering.
        Returns:
            - resolved_entities: Consolidated canonical entities.
            - all_evidence: Complete audit trail of pairwise comparisons.
            - id_mapping: Mapping from old entity ID to canonical entity ID.
        """
        if not entities:
            return ([], [], {})

        all_evidence: List[ResolutionEvidence] = []
        # Group entities by type
        by_type: Dict[EntityType, List[Entity]] = {}
        for ent in entities:
            by_type.setdefault(ent.type, []).append(ent)

        id_mapping: Dict[str, str] = {}
        resolved_entities: List[Entity] = []

        for etype, ent_list in by_type.items():
            n = len(ent_list)
            # Disjoint set / union-find structures
            parent: Dict[str, str] = {e.id: e.id for e in ent_list}

            def find(x: str) -> str:
                if parent[x] != x:
                    parent[x] = find(parent[x])
                return parent[x]

            def union(x: str, y: str):
                root_x = find(x)
                root_y = find(y)
                if root_x != root_y:
                    # Select deterministic root (lexicographically earliest ID)
                    canonical = min(root_x, root_y)
                    other = max(root_x, root_y)
                    parent[other] = canonical

            # Pairwise candidate comparison
            for i in range(n):
                for j in range(i + 1, n):
                    e_a = ent_list[i]
                    e_b = ent_list[j]
                    ev = self.compare_candidates(e_a, e_b)
                    all_evidence.append(ev)

                    if ev.decision == MatchDecision.MATCH:
                        union(e_a.id, e_b.id)

            # Group entities by cluster canonical root
            clusters: Dict[str, List[Entity]] = {}
            for e in ent_list:
                root = find(e.id)
                clusters.setdefault(root, []).append(e)

            # Merge clusters into canonical entities
            for root_id, cluster in clusters.items():
                canonical_ent = self._merge_entity_cluster(cluster)
                resolved_entities.append(canonical_ent)
                for member in cluster:
                    id_mapping[member.id] = canonical_ent.id

        return (resolved_entities, all_evidence, id_mapping)

    def resolve_with_relationships(
        self,
        entities: List[Entity],
        relationships: List[Relationship]
    ) -> Tuple[List[Entity], List[Relationship], List[ResolutionEvidence]]:
        """
        Executes entity resolution over entities and rewrites relationship endpoints
        (source and target) to their canonical IDs.
        Preserves distinct structured events (CDRs, Transactions).
        """
        resolved_entities, evidence, id_mapping = self.resolve(entities)

        rewritten_relationships: List[Relationship] = []
        seen_narrative_edges: Set[Tuple[str, str, str, str]] = set()

        for rel in relationships:
            new_source = id_mapping.get(rel.source, rel.source)
            new_target = id_mapping.get(rel.target, rel.target)

            # Suppress self-loops that might occur if source and target resolved to the same entity
            if new_source == new_target:
                continue

            # Check if this is a structured log event (CDR or Transaction)
            # Distinct CDRs and Transactions must NEVER be collapsed!
            is_structured = rel.provenance.source_type in {"TELECOM_CDR", "BANK_LEDGER"}

            if not is_structured:
                # Deduplicate narrative edges within the same source document
                dedup_key = (rel.provenance.source_id, new_source, new_target, rel.type.value)
                if dedup_key in seen_narrative_edges:
                    continue
                seen_narrative_edges.add(dedup_key)

            # Create updated relationship with canonical endpoints
            updated_rel = rel.model_copy(
                update={
                    "source": new_source,
                    "target": new_target,
                }
            )
            rewritten_relationships.append(updated_rel)

        return (resolved_entities, rewritten_relationships, evidence)

    # -----------------------------------------------------------------
    # Internal Consolidation Helpers
    # -----------------------------------------------------------------

    @staticmethod
    def _check_shared_attribute(a: Entity, b: Entity, keys: List[str]) -> Optional[str]:
        for k in keys:
            v_a = a.attributes.get(k)
            v_b = b.attributes.get(k)
            if v_a and v_b:
                str_a = str(v_a).strip()
                str_b = str(v_b).strip()
                if str_a and str_a == str_b:
                    return str_a
        return None

    def _merge_entity_cluster(self, cluster: List[Entity]) -> Entity:
        """
        Merges a cluster of matched entities into a single canonical Entity.
        Deterministic policy:
        1. Canonical ID: Pick the smallest lexicographical ID (e.g. P001 before P011) or earliest source.
        2. Label: Select the label of the entity with the highest risk_score or lowest ID.
        3. Aliases: Full union of all aliases plus alternative labels from merged entities.
        4. Source Records: Full deduplicated union of source_records.
        5. Risk Score: Maximum risk_score among all cluster members.
        6. Attributes: Merge attributes preserving non-empty values.
        """
        if len(cluster) == 1:
            return cluster[0]

        # Deterministic sorting: sort by (id)
        sorted_cluster = sorted(cluster, key=lambda x: x.id)
        canonical_base = sorted_cluster[0]

        # Select highest risk score
        max_risk = max(e.risk_score for e in cluster)

        # Best display label: entity with highest risk or first base
        best_label_ent = max(cluster, key=lambda x: (x.risk_score, -len(x.label)))
        canonical_label = best_label_ent.label

        # Union aliases
        all_aliases: Set[str] = set()
        for e in cluster:
            all_aliases.update(e.aliases)
            if e.label != canonical_label:
                all_aliases.add(e.label)
            if e.name and e.name != canonical_label:
                all_aliases.add(e.name)
        # Discard empty strings
        all_aliases.discard("")

        # Union source records
        all_source_records: Set[str] = set()
        for e in cluster:
            all_source_records.update(e.source_records)

        # Merge attributes
        merged_attributes: Dict[str, Any] = {}
        for e in sorted_cluster:
            for k, v in e.attributes.items():
                if v is not None and v != "":
                    merged_attributes[k] = v

        # Combine occurrences if present
        total_occurrences = sum(e.attributes.get("occurrences", 1) for e in cluster)
        merged_attributes["occurrences"] = total_occurrences
        merged_attributes["merged_from_ids"] = [e.id for e in sorted_cluster]

        # Primary role
        best_role = canonical_base.role
        for e in sorted_cluster:
            if e.role and e.role != "Suspect":
                best_role = e.role
                break

        return Entity(
            id=canonical_base.id,
            type=canonical_base.type,
            label=canonical_label,
            name=canonical_label,
            role=best_role,
            risk_score=max_risk,
            aliases=sorted(list(all_aliases)),
            attributes=merged_attributes,
            source_records=sorted(list(all_source_records)),
        )
