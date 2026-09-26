# VERITAS — AI Relationship Extraction Specification

> **Module Documentation** // Member 1 (AI/NLP + Data)  
> Architectural design, pattern triggers, directedness, confidence strategy, and provenance binding for multi-relational graph edge extraction.

---

## 1. Overview & Core Principle

The Relationship Extraction layer (`ai/extraction/relation_extractor.py`) transforms structured forensic logs (CDRs, banking ledgers) and unstructured natural language police reports (FIRs, field surveillance) into explainable graph relationships.

### Core Principle
In alignment with the VERITAS core principle:
- **No speculative relationships**: Co-occurrence alone in a sentence does **not** trigger an edge. Relationships require explicit semantic or structural evidence.
- **100% Provenance Binding**: Every extracted edge is permanently anchored to ground-truth evidence (source ID, source type, timestamp, snippet, and confidence score).
- **Approved Vocabulary Only**: Exactly 12 relationship types are permitted, matching [`docs/GRAPH_SCHEMA.md`](file:///C:/Users/omupa/OneDrive/Desktop/VERITAS-/docs/GRAPH_SCHEMA.md).

---

## 2. Supported Relationship Types & Semantics

| Relationship Type | Source Entity Type | Target Entity Type | Directed? | Description & Investigative Utility |
| :--- | :--- | :--- | :---: | :--- |
| `CALLED` | `Phone` | `Phone` | **Yes** | Telecom voice/SMS call event between two MSISDNs. |
| `TRANSACTED_WITH` | `BankAccount` | `BankAccount` | **Yes** | Financial fund wire or cash deposit transfer between accounts. |
| `USES_PHONE` | `Person` | `Phone` | **Yes** | Suspect operating, possessing, or registered to a phone/SIM card. |
| `OWNS` | `Person` | `Vehicle` | **Yes** | Registered ownership of a motor vehicle or transport asset. |
| `OPERATES` | `Person` | `Vehicle` | **Yes** | Suspect observed driving or physically controlling a vehicle. |
| `LOCATED_AT` | `Person` | `Location` | **Yes** | Suspect presence observed at a physical safehouse, depot, or hub. |
| `ASSOCIATED_WITH` | `Person` | `Person` | **Yes** | Documented meeting, conspiracy, or close-door criminal association. |
| `SUPERVISES` | `Person` | `Person` | **Yes** | Hierarchical command (handler $\to$ courier or dispatcher $\to$ runner). |
| `COORDINATES_WITH` | `Person` | `Person` | **Yes** | Lateral tactical coordination between cell coordinators or enforcers. |
| `CONTROLS` | `Person` | `Organization` | **Yes** | Beneficial ownership, proprietary control, or executive power. |
| `MEMBER_OF` | `Person` | `Organization` | **Yes** | Formal directorship, employment, or syndicate membership. |
| `OWNS_ACCOUNT` | `Person` / `Organization` | `BankAccount` | **Yes** | Legal or operational ownership of a financial account. |

*No speculative verbs (e.g. `WORKS_FOR`, `TRANSFERRED_TO`, `MESSAGED`, `PAID`) are permitted.*

---

## 3. Extraction Mechanisms

### 3.1 CDR Telecom Extraction
- **Input**: [`CDRRecord`](file:///C:/Users/omupa/OneDrive/Desktop/VERITAS-/ai/ingestion/csv_parser.py#L52-L68) (e.g. from `data/demo/cdrs.csv`).
- **Semantic Edge**: `(:Phone)-[:CALLED]->(:Phone)`.
- **Direction**: `caller_msisdn` $\longrightarrow$ `receiver_msisdn`.
- **Weight**: Default `1.0` per call, or aggregated total duration/call count.
- **Confidence**: `1.0` (high confidence originating from raw switch records).
- **Provenance Snippet**: Auto-generated call descriptor: `"Call record CDR1001 from +919811010001 to +919811010002 lasting 420s via tower TOWER_CP_01."`

### 3.2 Financial Transaction Extraction
- **Input**: [`TransactionRecord`](file:///C:/Users/omupa/OneDrive/Desktop/VERITAS-/ai/ingestion/csv_parser.py#L71-L87) (e.g. from `data/demo/transactions.csv`).
- **Semantic Edge**: `(:BankAccount)-[:TRANSACTED_WITH]->(:BankAccount)`.
- **Direction**: `sender_account` $\longrightarrow$ `receiver_account`.
- **Weight**: Monetary value (e.g. `850000.0` INR).
- **Confidence**: `1.0` (originating from banking export or FIU ledger).
- **Provenance Snippet**: Auto-generated financial descriptor: `"Financial transaction TX1006 of INR 850,000.00 from ACC-ASTRA-7701 to ACC-SHEIKH-4401 via RTGS."`

### 3.3 Text-Based Semantic Extraction
Processes unstructured narrative text from police complaints, interrogation transcripts, and field surveillance reports. Evaluates sentence-level syntactic patterns between recognized entities:

1. **`USES_PHONE`**: Triggered by possession, recovery, or registration keywords (`possession of phone`, `MSISDN:`, `device recovered from`, `terminal registered to`).
2. **`OWNS` vs `OPERATES`**:
   - `OWNS`: Triggered by `registered to`, `owner`, `owns vehicle`.
   - `OPERATES`: Triggered by `driven by`, `driving`, `driver identified as`, `intercepted truck`.
3. **`LOCATED_AT`**: Triggered by arrival, presence, or meeting locations (`at Okhla Industrial Area`, `present inside warehouse`, `premises in Chandni Chowk`).
4. **`CONTROLS` vs `MEMBER_OF`**:
   - `CONTROLS`: Beneficial ownership triggers (`beneficial owner`, `proprietor`, `controls`).
   - `MEMBER_OF`: Position/directorship triggers (`Managing Director`, `holding equity`, `member`).
5. **`OWNS_ACCOUNT`**: Triggered by account listings (`account registered under`, `corporate account`).
6. **Interpersonal (`SUPERVISES`, `COORDINATES_WITH`, `ASSOCIATED_WITH`)**:
   - `SUPERVISES`: Handler-runner relationship (`received from immediate handler`, `dispatched on courier run`).
   - `COORDINATES_WITH`: Tactical communication (`coordination over encrypted phone lines`).
   - `ASSOCIATED_WITH`: Criminal conspiracy and meetings (`closed-door meeting behind shuttered glass`).

---

## 4. Confidence Strategy

All confidence scores are explainable and bounded within $[0.0, 1.0]$:
- **`1.00`**: Structured CDR switch records and bank ledger transfers.
- **`0.96`**: Explicit `USES_PHONE` matches with direct E.164 phone tokens.
- **`0.95`**: Explicit `OWNS`, `OPERATES`, and `OWNS_ACCOUNT` patterns.
- **`0.94`**: Beneficial corporate ownership (`CONTROLS`).
- **`0.92`**: Location presence (`LOCATED_AT`), `SUPERVISES`, and `MEMBER_OF`.
- **`0.88`**: Operational `COORDINATES_WITH`.
- **`0.85`**: Meeting and association observations (`ASSOCIATED_WITH`).

---

## 5. Relationship ID Generation & Duplicate Suppression

### 5.1 ID Format
Generated by [`RelationshipIDGenerator`](file:///C:/Users/omupa/OneDrive/Desktop/VERITAS-/ai/extraction/relation_extractor.py#L16-L45) using stable identifiers:
$$\text{RID} = \text{"R"} + \text{counter:03d} \quad (\text{e.g. } R001, R002, \dots)$$
The registry keys on `source_id:event_id:source:target:type`, guaranteeing that repeated extractions over identical events produce the exact same ID.

### 5.2 Duplicate Suppression Policy
- **Within a single document**: If a narrative document repeats that *"Arjun Verma drove truck DL-1M-4412"* across multiple paragraphs, only **one** `OPERATES` edge is emitted for `(P006, V004)`.
- **Across structured log events**: Separate CDR calls (`CDR1001` vs `CDR1002`) or financial wires (`TX1001` vs `TX1002`) between identical entities represent distinct real-world events and are both preserved.

---

## 6. Code Examples

```python
from ai.extraction.ner import EntityExtractor
from ai.extraction.relation_extractor import RelationshipExtractor
from ai.ingestion.csv_parser import load_cdrs_csv, load_transactions_csv
from ai.ingestion.document_parser import load_document

# 1. Initialize extractors
ner = EntityExtractor(use_spacy=False)
rel_extractor = RelationshipExtractor()

# 2. Extract from Police Report
doc = load_document("data/demo/firs/FIR_001_Smuggling_Bust.txt")
entities = ner.extract_from_record(doc)
relationships = rel_extractor.extract_from_record(doc, entities=entities)

# 3. Extract from Telecom CDRs
cdrs = load_cdrs_csv("data/demo/cdrs.csv")
cdr_entities = [e for r in cdrs for e in ner.extract_from_record(r)]
cdr_relationships = rel_extractor.extract(cdrs, entities=cdr_entities)
```
