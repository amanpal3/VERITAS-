# VERITAS — AI Entity Resolution Specification

> **Module Documentation** // Member 1 (AI/NLP + Data)  
> Architectural design, multi-signal candidate matching, explainable resolution evidence, canonical identity deduplication, and relationship endpoint rewriting.

---

## 1. Overview & Core Principles

In law enforcement knowledge graphs, premature or erroneous entity merging ("over-merging") is catastrophic: falsely collapsing two distinct suspects (e.g. sharing a common surname like Kumar or Sharma) corrupts evidentiary chain-of-custody and undermines criminal prosecution. Conversely, failing to link aliases, burner devices, or corporate shell accounts creates fragmented intelligence silos.

The Entity Resolution layer ([`ai/resolution/entity_resolver.py`](file:///C:/Users/omupa/OneDrive/Desktop/VERITAS-/ai/resolution/entity_resolver.py)) resolves real-world identities across heterogeneous data streams (FIRs, CDRs, financial ledgers, surveillance logs) under strict investigative constraints.

### Core Principles
1. **Explainable Resolution Evidence**: Every merge decision is accompanied by a [`ResolutionEvidence`](file:///C:/Users/omupa/OneDrive/Desktop/VERITAS-/ai/resolution/entity_resolver.py#L38-L51) record containing candidate IDs, confidence score, decision boundary, and explicit justification strings.
2. **Category-Specific Strictness**:
   - **Phones, Vehicles, Bank Accounts**: Require 100% exact normalized value match. Fuzzy matching is strictly prohibited.
   - **Persons, Organizations, Locations**: Evaluated via multi-signal matching (name similarity, phonetic codes, alias overlap, contextual cues).
3. **Conservative Decision Boundaries**:
   - **`MATCH`** ($\text{Score} \ge 0.85$): Automated consolidation.
   - **`UNCERTAIN`** ($0.60 \le \text{Score} < 0.85$): Flagged for human investigator audit without automated merging.
   - **`NO_MATCH`** ($\text{Score} < 0.60$): Maintained as distinct entities.
4. **Zero Evidentiary Loss**: Merging two entities unifies 100% of `source_records`, preserves all known aliases, retains maximum `risk_score`, and consolidates attributes.
5. **Deterministic Canonical ID Selection**: Lowest lexicographical ID (e.g. `P001` before `P099`) or earliest source record is chosen deterministically as canonical.
6. **Relationship Endpoint Rewriting**: Graph relationships are updated so `source` and `target` reference canonical IDs, while strictly preserving distinct structured events (`CDR1001` vs `CDR1002`, `TX1001` vs `TX1002`).

---

## 2. Matching Rules by Entity Type

| Entity Type | Permitted Matching Mechanisms | Prohibited / Negative Rules | Decision Thresholds |
| :--- | :--- | :--- | :---: |
| `Phone` | Exact normalized E.164 (`+919811010001`) equality or exact match in alias set. | **No fuzzy matching**. Single-digit differences are rejected. | 1.0 = MATCH, 0.0 = NO_MATCH |
| `Vehicle` | Exact normalized registration plate (e.g. `DL-1C-0001`) equality. | **No fuzzy matching**. Model descriptor variations are stripped before comparison. | 1.0 = MATCH, 0.0 = NO_MATCH |
| `BankAccount` | Exact normalized account identifier (e.g. `ACC-SINGH-9901`) equality. | **No fuzzy matching**. | 1.0 = MATCH, 0.0 = NO_MATCH |
| `Person` | Exact name match, direct alias overlap, or Jaro-Winkler/Levenshtein similarity + shared phone/account identifier. | **Common surnames alone are NOT merged** (e.g. "Rajesh Kumar" vs "Rakesh Kumar"). Distinct first names without shared phone = NO_MATCH. | $\ge 0.85$: MATCH<br>$[0.60, 0.85)$: UNCERTAIN<br>$< 0.60$: NO_MATCH |
| `Organization` | Exact name, alias overlap, identical corporate stem (`Astra Logistics Ltd` vs `Astra Logistics`), or high string similarity ($\ge 0.90$). | Distinct companies or unrelated acronyms. | $\ge 0.85$: MATCH<br>$[0.70, 0.85)$: UNCERTAIN<br>$< 0.70$: NO_MATCH |
| `Location` | Exact name, nested hub inclusion (`Okhla Industrial Area, Phase II` $\subset$ `Okhla Industrial Area`), or high string similarity. | **Distinct regional jurisdictions** (`New Delhi` vs `Noida`) are never merged. | $\ge 0.85$: MATCH<br>$[0.65, 0.85)$: UNCERTAIN<br>$< 0.65$: NO_MATCH |

---

## 3. Architecture & Data Structures

```
                 [ Extracted Entities ]
                           │
                           ▼
              ┌──────────────────────────┐
              │      EntityResolver      │
              │  - compare_candidates()  │
              │  - resolve()             │
              │  - resolve_with_rels()   │
              └────────────┬─────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
   [ MatchDecision ] [ ResolutionEvidence ] [ Disjoint Set ]
     • MATCH           • candidate_a/b        • Canonical Root
     • UNCERTAIN       • decision             • ID Remap Table
     • NO_MATCH        • score & reasons
                           │
                           ▼
          ┌───────────────────────────────────┐
          │     Consolidated Canonical Node   │
          │  - ID: lowest lexicographical ID  │
          │  - Risk: max(risk_scores)         │
          │  - Aliases: union(aliases)        │
          │  - Sources: union(source_records) │
          └───────────────────────────────────┘
```

### 3.1 Explainable Evidence Structure
```python
class ResolutionEvidence(BaseModel):
    candidate_a: str
    candidate_b: str
    entity_type: EntityType
    decision: MatchDecision
    score: float
    reasons: List[str]
```

### 3.2 Canonical Merge Consolidation
When a cluster $\{E_1, E_2, \dots, E_k\}$ is merged:
$$\text{Canonical ID} = \min_{i}(E_i.\text{id})$$
$$\text{risk\_score} = \max_{i}(E_i.\text{risk\_score})$$
$$\text{aliases} = \bigcup_{i} (E_i.\text{aliases} \cup \{E_i.\text{label}\}) \setminus \{\text{Canonical Label}\}$$
$$\text{source\_records} = \bigcup_{i} E_i.\text{source\_records}$$

---

## 4. Relationship Endpoint Rewriting & Event Preservation

When entity identities are resolved, all existing graph edges must be rewritten so their `source` and `target` endpoints point to canonical IDs:
1. **Self-Loop Prevention**: If an edge's source and target resolve to the identical canonical node ($u = v$), the self-loop is dropped.
2. **Narrative Edge Deduplication**: Duplicate relationships extracted from the same police report are collapsed into a single canonical edge.
3. **Structured Event Preservation**: Telecom CDR calls (`CDR1001`, `CDR1002`) and banking transactions (`TX1001`, `TX1002`) represent discrete temporal events; they are **never** collapsed, even if they share identical endpoints.

---

## 5. Usage Example

```python
from ai.resolution.entity_resolver import EntityResolver
from ai.schemas.entity import Entity, EntityType

resolver = EntityResolver()

# Pairwise candidate comparison
evidence = resolver.compare_candidates(entity_a, entity_b)
print(f"Decision: {evidence.decision.value}, Score: {evidence.score}")
print(f"Reasons: {evidence.reasons}")

# Batch resolution with relationship rewriting
resolved_entities, rewritten_rels, evidence_list = resolver.resolve_with_relationships(
    entities=raw_entities,
    relationships=raw_relationships
)
```
