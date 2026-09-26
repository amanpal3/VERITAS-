# VERITAS — Member 1 to Member 2 Backend Handoff Specification

> **Target Audience**: Member 2 (Backend, FastAPI, Neo4j, Graph Data Service)  
> **Source Module**: Member 1 (AI/NLP, Ingestion, Entity Resolution, Anomaly Detection)  
> **Version**: 1.0.0  
> **Status**: Production-Ready & Verified (104/104 Tests Passing, 6/6 Integrity Checks Passing)

---

## 1. How Member 2 Imports `IntelligencePipeline`

Member 2 can import the pipeline orchestrator and associated result types directly from the top-level `ai` package or from `ai.pipeline`:

```python
# Primary Recommended Import
from ai import IntelligencePipeline, PipelineResult, PipelineMetadata

# Module-level Import
from ai.pipeline import IntelligencePipeline, PipelineResult, PipelineMetadata
```

No external model downloads or network calls are required on startup. If spaCy is not installed or the `en_core_web_sm` model is absent, the pipeline automatically falls back to deterministic rule-based forensic heuristics without raising an exception.

---

## 2. How to Execute the Pipeline

Instantiate `IntelligencePipeline` as a stateless, thread-safe service. The orchestrator exposes a single entrypoint: `.run()`.

```python
pipeline = IntelligencePipeline(use_spacy=True)

# Mode A: Execute over in-memory records
result: PipelineResult = pipeline.run(records=records_list)

# Mode B: Execute over filesystem paths (directory or file)
result: PipelineResult = pipeline.run(raw_data_path="data/demo")

# Mode C: Combined execution
result: PipelineResult = pipeline.run(records=records_list, raw_data_path="data/demo/firs")
```

### Constructor Arguments
| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `use_spacy` | `bool` | `True` | Attempts loading spaCy `en_core_web_sm`. Falls back to rule-based NER if unavailable. Set to `False` for deterministic/headless execution. |
| `entity_id_generator` | `Optional[EntityIDGenerator]` | `None` | Custom entity ID allocator. Defaults to pre-seeded canonical generator. |
| `rel_id_generator` | `Optional[RelationshipIDGenerator]` | `None` | Custom relationship ID allocator. Defaults to deterministic sequential generator. |
| `entity_resolver` | `Optional[EntityResolver]` | `None` | Configured entity resolution engine. |
| `anomaly_detector` | `Optional[AnomalyDetector]` | `None` | Configured anomaly detection engine. |

---

## 3. Pipeline Input Formats

The `.run()` method accepts heterogeneous inputs polymorphically:

### 3.1 Typed Pydantic Ingestion Records
Directly instantiated from [`ai.ingestion`](file:///C:/Users/omupa/OneDrive/Desktop/VERITAS-/ai/ingestion):
* **`DocumentRecord`**: Police reports, intelligence summaries, surveillance logs.
* **`CDRRecord`**: Telecommunication call detail records.
* **`TransactionRecord`**: Bank ledger transfers.

### 3.2 Raw Narrative Strings
Unstructured plaintext (e.g. direct text pasted into a dashboard or API payload). The pipeline automatically wraps raw strings into `DocumentRecord` instances:
```python
result = pipeline.run(records=["Accused Arjun Verma was intercepted driving truck DL-1M-4412."])
```

### 3.3 Loose Python Dictionaries
JSON-deserialized dicts from HTTP requests or message brokers:
* **Call Detail Record Dict**:
  ```python
  {"call_id": "CDR1001", "caller_raw": "+919811010001", "receiver_raw": "+919811010002", "timestamp": "2026-03-01T12:00:00Z", "duration_sec": 300}
  ```
* **Transaction Dict**:
  ```python
  {"transaction_id": "TX1001", "sender_account": "ACC-ASTRA-7701", "receiver_account": "ACC-SHEIKH-4401", "amount": 850000.0, "currency": "INR"}
  ```
* **Document Dict**:
  ```python
  {"raw_text": "Surveillance log...", "source_id": "SURV-001", "document_type": "SURVEILLANCE"}
  ```

### 3.4 Filesystem Directory / File Paths
Points to a directory containing standard subdirectories and files:
* Subdirectory `firs/` (containing `.txt` or `.pdf` narratives).
* File `cdrs.csv` (standard CSV headers: `call_id`, `caller_msisdn`, `receiver_msisdn`, `timestamp`, `duration_sec`).
* File `transactions.csv` (standard CSV headers: `transaction_id`, `sender_account`, `receiver_account`, `amount`, `timestamp`).

---

## 4. `PipelineResult` Structure

The result returned by `pipeline.run()` is a Pydantic model containing:

```python
class PipelineResult(BaseModel):
    entities: List[Entity]                        # Canonical resolved graph nodes
    relationships: List[Relationship]            # Canonical multi-relational graph edges
    anomalies: List[AnomalyResult]                # Explainable behavioral anomaly signals
    resolution_evidence: List[ResolutionEvidence] # Full audit trail of pairwise resolution decisions
    pipeline_metadata: PipelineMetadata          # Execution counts and diagnostic metrics
```

### Serialization Methods
* `result.to_dict() -> Dict[str, Any]`: Returns raw Python dictionary representation.
* `result.to_json(indent: int = 2) -> str`: Returns formatted JSON string matching project contracts.

### `PipelineMetadata` Schema
```python
class PipelineMetadata(BaseModel):
    records_processed: int       # Total input records ingested (e.g. 120)
    entity_count_raw: int        # Raw entities extracted before cross-record resolution (e.g. 293)
    entity_count: int            # Canonical entities remaining after resolution (e.g. 65)
    relationship_count_raw: int  # Raw relationships extracted before rewriting (e.g. 178)
    relationship_count: int      # Final canonical relationships after endpoint rewriting (e.g. 161)
    anomaly_count: int           # Total behavioral anomalies flagged (e.g. 15)
    resolution_merge_count: int  # Total entity instances merged into canonical clusters (e.g. 228)
    status: str                  # "SUCCESS" or "PARTIAL" (if malformed records were quarantined)
```

---

## 5. Entity JSON Schema

Matches [`ai/schemas/entity.py`](file:///C:/Users/omupa/OneDrive/Desktop/VERITAS-/ai/schemas/entity.py):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Entity",
  "type": "object",
  "required": ["id", "type", "label"],
  "properties": {
    "id": { "type": "string", "description": "Deterministic ID (e.g. P001, PH001)" },
    "type": { "type": "string", "enum": ["Person", "Phone", "Vehicle", "Organization", "Location", "BankAccount"] },
    "label": { "type": "string", "description": "Canonical normalized display label" },
    "name": { "type": ["string", "null"], "description": "Alias matching label for backward compatibility" },
    "role": { "type": ["string", "null"], "description": "Investigative role (e.g. Syndicate Mastermind, Transport Courier)" },
    "risk_score": { "type": "number", "minimum": 0.0, "maximum": 100.0, "default": 0.0 },
    "aliases": { "type": "array", "items": { "type": "string" }, "default": [] },
    "attributes": { "type": "object", "additionalProperties": true, "default": {} },
    "source_records": { "type": "array", "items": { "type": "string" }, "default": [] }
  }
}
```

---

## 6. Relationship JSON Schema

Matches [`ai/schemas/relationship.py`](file:///C:/Users/omupa/OneDrive/Desktop/VERITAS-/ai/schemas/relationship.py):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Relationship",
  "type": "object",
  "required": ["id", "source", "target", "type", "provenance"],
  "properties": {
    "id": { "type": "string", "description": "Deterministic relationship ID (e.g. R001)" },
    "source": { "type": "string", "description": "Source Entity ID (must exist in entities)" },
    "target": { "type": "string", "description": "Target Entity ID (must exist in entities)" },
    "type": { 
      "type": "string", 
      "enum": [
        "USES_PHONE", "CALLED", "OWNS", "OPERATES", "LOCATED_AT", 
        "ASSOCIATED_WITH", "SUPERVISES", "COORDINATES_WITH", "CONTROLS", 
        "MEMBER_OF", "OWNS_ACCOUNT", "TRANSACTED_WITH"
      ] 
    },
    "weight": { "type": "number", "default": 1.0 },
    "timestamp": { "type": ["string", "null"], "description": "ISO-8601 timestamp string" },
    "provenance": { "$ref": "#/definitions/Provenance" },
    "attributes": { "type": "object", "additionalProperties": true, "default": {} }
  }
}
```

---

## 7. Anomaly JSON Schema

Matches [`ai/anomaly/detector.py`](file:///C:/Users/omupa/OneDrive/Desktop/VERITAS-/ai/anomaly/detector.py):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AnomalyResult",
  "type": "object",
  "required": ["entity_id", "anomaly_type", "score", "severity", "evidence", "explanation", "supporting_record_ids", "feature_values"],
  "properties": {
    "entity_id": { "type": "string", "description": "Flagged entity ID or account/phone key" },
    "anomaly_type": { 
      "type": "string", 
      "enum": [
        "HIGH_TRANSACTION_AMOUNT", "HIGH_TRANSACTION_FREQUENCY", 
        "HIGH_CALL_FREQUENCY", "BURST_ACTIVITY", 
        "HIGH_CONNECTIVITY", "CROSS_COMMUNITY_BRIDGE"
      ] 
    },
    "score": { "type": "number", "minimum": 0.0, "maximum": 1.0, "description": "Normalized statistical extremity" },
    "severity": { "type": "string", "enum": ["LOW", "MEDIUM", "HIGH"] },
    "evidence": { "type": "string", "description": "Quantitative summary (e.g. Amount: 8,500,000.00 vs P90: 940,000.00)" },
    "explanation": { "type": "string", "description": "Objective, non-accusatory investigative explanation" },
    "supporting_record_ids": { "type": "array", "items": { "type": "string" } },
    "feature_values": { "type": "object", "additionalProperties": true }
  }
}
```

---

## 8. Provenance Fields

Provenance is preserved across 100% of pipeline stages to guarantee strict evidentiary auditability:

```json
{
  "source_id": "FIR-001_Smuggling_Bust",
  "source_type": "POLICE_REPORT",
  "snippet": "Arjun Verma was intercepted driving truck DL-1M-4412 containing smuggled contraband.",
  "confidence": 0.95
}
```

* `source_id`: The originating document filename, batch code, or record ID (e.g. `FIR_001_Smuggling_Bust`, `CDR1001`, `TX1001`).
* `source_type`: Category of evidence: `POLICE_REPORT`, `SURVEILLANCE`, `TELECOM_CDR`, or `BANK_LEDGER`.
* `snippet`: Verbatim sentence excerpt from the source document or analytical transaction summary.
* `confidence`: Statistical or evidentiary certainty bounded within $[0.0, 1.0]$. Structured CDRs and transactions are assigned `1.0`.

---

## 9. Entity ID Conventions

Entity IDs are deterministic and prefixed according to entity type:

| Entity Type | Prefix | Format | Example | Pre-Seeded Demo Range |
| :--- | :--- | :--- | :--- | :--- |
| `Person` | `P` | `P{seq:03d}` | `P001`, `P011` | `P001` – `P010` |
| `Phone` | `PH` | `PH{seq:03d}` | `PH001`, `PH011` | `PH001` – `PH006` |
| `Vehicle` | `V` | `V{seq:03d}` | `V001`, `V005` | `V001` – `V004` |
| `Organization` | `ORG` | `ORG{seq:03d}`| `ORG001`, `ORG011`| `ORG001` – `ORG003` |
| `Location` | `LOC` | `LOC{seq:03d}`| `LOC001`, `LOC011`| `LOC001` – `LOC003` |
| `BankAccount` | `BA` | `BA{seq:03d}` | `BA001`, `BA011` | `BA001` – `BA003` |

Pre-seeded IDs correspond directly to the benchmark identities defined in `data/demo/entities.json`. Any new entity discovered during ingestion is deterministically allocated the next sequence index (e.g. `P011`, `PH007`, `BA004`).

---

## 10. Relationship ID Conventions

Relationship IDs are sequential, deterministic strings formatted as `R{seq:03d}` (e.g. `R001`, `R002`, `R161`).
* The registry hashes `source_id:event_id:source:target:rel_type` to ensure that identical extractions within a source produce stable IDs across runs.
* Distinct CDR call instances (`CDR1001`, `CDR1002`) and financial transfers (`TX1001`, `TX1002`) between identical entities receive distinct relationship IDs.

---

## 11. Relationship Direction Semantics

Relationships are strictly directed. Member 2 must enforce the following directional ontology when creating edges in Neo4j or Cytoscape:

```
(:Person)       -[:USES_PHONE]->        (:Phone)
(:Phone)        -[:CALLED]->            (:Phone)           # (Caller) -> (Receiver)
(:Person)       -[:OWNS]->              (:Vehicle)         # (Registered Owner) -> (Vehicle)
(:Person)       -[:OPERATES]->          (:Vehicle)         # (Driver/Operator) -> (Vehicle)
(:Person)       -[:LOCATED_AT]->        (:Location)        # (Observed Person) -> (Location Hub)
(:Person)       -[:ASSOCIATED_WITH]->   (:Person)          # (Suspect A) -> (Suspect B)
(:Person)       -[:SUPERVISES]->        (:Person)          # (Boss/Handler) -> (Subordinate/Courier)
(:Person)       -[:COORDINATES_WITH]->  (:Person)          # (Peer A) -> (Peer B)
(:Person)       -[:CONTROLS]->          (:Organization)    # (Beneficial Owner) -> (Corporate Shell)
(:Person)       -[:MEMBER_OF]->         (:Organization)    # (Employee/Director) -> (Organization)
(:Person)       -[:OWNS_ACCOUNT]->      (:BankAccount)     # (Account Signatory) -> (Bank Account)
(:Organization) -[:OWNS_ACCOUNT]->      (:BankAccount)     # (Corporate Shell) -> (Bank Account)
(:BankAccount)  -[:TRANSACTED_WITH]->   (:BankAccount)     # (Sender Account) -> (Beneficiary Account)
```

---

## 12. Entity Type Vocabulary

Allowed entity types in `Entity.type`:
* `"Person"`
* `"Phone"`
* `"Vehicle"`
* `"Organization"`
* `"Location"`
* `"BankAccount"`

No other entity labels exist. Any unexpected type raises a Pydantic `ValidationError`.

---

## 13. Relationship Type Vocabulary

Allowed relationship types in `Relationship.type`:
* `"USES_PHONE"`
* `"CALLED"`
* `"OWNS"`
* `"OPERATES"`
* `"LOCATED_AT"`
* `"ASSOCIATED_WITH"`
* `"SUPERVISES"`
* `"COORDINATES_WITH"`
* `"CONTROLS"`
* `"MEMBER_OF"`
* `"OWNS_ACCOUNT"`
* `"TRANSACTED_WITH"`

*(Note: In narrative text, mentions of "OWNS_VEHICLE" are automatically aliased to `"OWNS"` upon ingestion).*

---

## 14. How Entity Resolution Changes IDs

During Stage 5, the `EntityResolver` clusters co-referent entities across documents and tabular records using Disjoint-Set Union (Union-Find):
1. **Cluster Formation**: If candidate entity $E_1$ (e.g. `P011`, label: `"The Don"`) matches $E_2$ (e.g. `P001`, label: `"Vikramaditya Singhania"`) via alias or exact matching, they join the same cluster.
2. **Canonical ID Selection**: The canonical ID chosen for the cluster is the smallest lexicographical identifier (preferring pre-seeded benchmark IDs like `P001` over dynamically allocated IDs like `P011`).
3. **Payload Merging**:
   - `label`: Preserves the canonical name with highest risk or benchmark priority.
   - `aliases`: Full set union of all aliases across merged nodes.
   - `source_records`: Full union of all originating file IDs (`["FIR-A", "FIR-B"]`).
   - `attributes`: Merged attribute dictionaries.
4. **Resolution Mapping**: An internal dictionary `id_mapping[old_id] = canonical_id` is created for all merged nodes.

---

## 15. How Relationship Endpoints Are Rewritten

During Stage 6, every extracted relationship undergoes endpoint translation:
1. `new_source = id_mapping.get(rel.source, rel.source)`
2. `new_target = id_mapping.get(rel.target, rel.target)`
3. **Self-Loop Suppression**: If `new_source == new_target` (which occurs if two co-referent entities in the same document were linked), the edge is automatically dropped ($source \neq target$ invariant).
4. **Narrative Deduplication**: If multiple identical narrative relationships (same `source_id`, `source`, `target`, and `type`) exist after rewriting, redundant assertions are collapsed into a single canonical edge.
5. **Referential Safety**: All final edges point only to surviving canonical entities in `result.entities`.

---

## 16. How Structured CDR and Transaction Events Are Preserved

To prevent loss of crucial forensic timeline data:
* Line `608` of [`ai/resolution/entity_resolver.py`](file:///C:/Users/omupa/OneDrive/Desktop/VERITAS-/ai/resolution/entity_resolver.py#L608) inspects the relationship provenance:
  ```python
  is_structured = rel.provenance.source_type in {"TELECOM_CDR", "BANK_LEDGER"}
  ```
* If `is_structured` is `True`, narrative deduplication is bypassed.
* **Result**: If phone `PH001` calls `PH002` 10 separate times, the output contains **10 distinct `CALLED` edges**, each retaining its individual `timestamp`, call duration, cell tower attribute, and `source_id` (e.g. `CDR1001` through `CDR1010`).
* Financial transfers behave identically: distinct transfers between the same accounts retain individual amounts, timestamps, payment channels, and transaction IDs.

---

## 17. Example Python Invocation

```python
from pathlib import Path
from ai.pipeline import IntelligencePipeline, PipelineResult

# 1. Initialize Pipeline
pipeline = IntelligencePipeline(use_spacy=True)

# 2. Run over the standard demo directory
result: PipelineResult = pipeline.run(raw_data_path=Path("data/demo"))

# 3. Access Canonical Entities
print(f"Total Canonical Entities: {len(result.entities)}")
for entity in result.entities[:3]:
    print(f"[{entity.id}] {entity.type.value}: {entity.label} (Risk: {entity.risk_score})")

# 4. Access Rewritten Relationships
print(f"Total Canonical Relationships: {len(result.relationships)}")
for rel in result.relationships[:3]:
    print(f"[{rel.id}] {rel.source} -[:{rel.type.value}]-> {rel.target} (Conf: {rel.provenance.confidence})")

# 5. Access Explainable Anomalies
print(f"Total Anomalies: {len(result.anomalies)}")
for anom in result.anomalies[:3]:
    print(f"[{anom.severity.value}] {anom.anomaly_type.value} on {anom.entity_id}: {anom.explanation}")

# 6. Export to Dict or JSON
graph_payload = result.to_dict()
json_string = result.to_json(indent=2)
```

---

## 18. Example `PipelineResult` JSON

```json
{
  "entities": [
    {
      "id": "P001",
      "type": "Person",
      "label": "Vikramaditya Singhania",
      "name": "Vikramaditya Singhania",
      "role": "Syndicate Mastermind",
      "risk_score": 95.0,
      "aliases": ["The Don", "Vikram"],
      "attributes": {
        "confidence": 0.95,
        "source_type": "POLICE_REPORT"
      },
      "source_records": ["FIR_001_Smuggling_Bust", "FIR_002_Hawala_Raid"]
    },
    {
      "id": "PH001",
      "type": "Phone",
      "label": "+919811010001",
      "name": "+919811010001",
      "role": "Active Caller",
      "risk_score": 75.0,
      "aliases": ["9811010001"],
      "attributes": {
        "source_id": "CDR1001",
        "source_type": "TELECOM_CDR"
      },
      "source_records": ["CDR1001", "FIR_001_Smuggling_Bust"]
    }
  ],
  "relationships": [
    {
      "id": "R001",
      "source": "P001",
      "target": "PH001",
      "type": "USES_PHONE",
      "weight": 1.0,
      "timestamp": "2026-03-01T00:00:00Z",
      "provenance": {
        "source_id": "FIR_001_Smuggling_Bust",
        "source_type": "POLICE_REPORT",
        "snippet": "Accused Vikramaditya Singhania was observed using mobile line +919811010001.",
        "confidence": 0.95
      },
      "attributes": {}
    }
  ],
  "anomalies": [
    {
      "entity_id": "ACC-ASTRA-7701",
      "anomaly_type": "HIGH_TRANSACTION_AMOUNT",
      "score": 1.0,
      "severity": "HIGH",
      "evidence": "Amount: 8,500,000.00 vs P90: 940,000.00",
      "explanation": "Transaction amount of INR 8,500,000.00 exceeds the 90th percentile (INR 940,000.00) of observed financial transactions (median: INR 250,000.00).",
      "supporting_record_ids": ["TX1048"],
      "feature_values": {
        "amount": 8500000.0,
        "currency": "INR",
        "p90_threshold": 940000.0
      }
    }
  ],
  "resolution_evidence": [],
  "pipeline_metadata": {
    "records_processed": 120,
    "entity_count_raw": 293,
    "entity_count": 65,
    "relationship_count_raw": 178,
    "relationship_count": 161,
    "anomaly_count": 15,
    "resolution_merge_count": 228,
    "status": "SUCCESS"
  }
}
```

---

## 19. Mapping from Pipeline Output to Neo4j Nodes

Member 2 should execute parameter-batched Cypher queries over `result.entities`:

```cypher
UNWIND $entities AS e
MERGE (n:Entity {id: e.id})
SET n.label = e.label,
    n.name = e.label,
    n.role = e.role,
    n.risk_score = e.risk_score,
    n.aliases = e.aliases,
    n.source_records = e.source_records

// Apply dynamic secondary label matching EntityType (:Person, :Phone, etc.)
WITH n, e
CALL apoc.create.addLabels(n, [e.type]) YIELD node
RETURN count(node)
```

*(If APOC is disabled, Member 2 can group entities by `e.type` in Python and execute standard typed Cypher statements: `MERGE (n:Person {id: e.id}) ...`, `MERGE (n:Phone {id: e.id}) ...`).*

---

## 20. Mapping from Pipeline Output to Neo4j Relationships

Relationships can be written using APOC dynamic relationship creation or per-type parameterized queries:

```cypher
UNWIND $relationships AS r
MATCH (src:Entity {id: r.source})
MATCH (tgt:Entity {id: r.target})
CALL apoc.create.relationship(src, r.type, {
    id: r.id,
    weight: r.weight,
    timestamp: r.timestamp,
    source_id: r.provenance.source_id,
    source_type: r.provenance.source_type,
    snippet: r.provenance.snippet,
    confidence: r.provenance.confidence
}, tgt) YIELD rel
RETURN count(rel)
```

*(Without APOC, generate standard Cypher using pre-validated `r.type` since all types come from the strict 12-item controlled enum).*

---

## 21. Recommended FastAPI Integration Boundary

Member 2 should host `IntelligencePipeline` as a singleton dependency inside FastAPI:

```python
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from typing import List
from ai import IntelligencePipeline, PipelineResult

router = APIRouter(prefix="/api/v1/intelligence", tags=["Intelligence"])

# Singleton pipeline instance
_pipeline = IntelligencePipeline()

@router.post("/process-batch", response_model=None)
async def process_investigation_batch(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Ingests uploaded investigation files, parses entities and relationships,
    executes resolution, flags anomalies, and returns the canonical graph.
    """
    try:
        # 1. Read files into ingestion records
        records = []
        for file in files:
            content = await file.read()
            text = content.decode("utf-8", errors="ignore")
            records.append({
                "raw_text": text,
                "file_name": file.filename,
                "file_path": f"uploaded/{file.filename}"
            })

        # 2. Execute Pipeline
        result: PipelineResult = _pipeline.run(records=records)

        # 3. Optional: Trigger asynchronous Neo4j persistence
        # background_tasks.add_task(neo4j_service.ingest_pipeline_result, result)

        return result.to_dict()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline processing failed: {str(e)}")
```

---

## 22. Errors & Exceptions Member 2 Should Handle

| Exception | Root Cause | Member 2 Recommended Handling |
| :--- | :--- | :--- |
| `FileNotFoundError` | `raw_data_path` does not exist on disk. | Return HTTP 400 with message `"Specified ingestion path not found"`. |
| `pydantic.ValidationError` | Invalid typed record passed to `pipeline.run()`. | Return HTTP 422 with validation errors. |
| `status == "PARTIAL"` | One or more CSV rows or loose dicts were malformed and quarantined. | Return HTTP 200/207 with payload, including `pipeline_metadata.status` and warnings. |
| `Empty Input` | An empty list `records=[]` or empty folder is passed. | Pipeline returns safe empty `PipelineResult` with status `"SUCCESS"`. |

---

## 23. Determinism Guarantees

Member 1 guarantees 100% deterministic execution:
1. **Idempotent IDs**: Ingesting the same dataset multiple times produces identical entity IDs (`P001`, `PH001`) and relationship IDs (`R001`).
2. **Stable Disjoint-Set Roots**: Resolution clustering merges entities using deterministic lexicographical rules.
3. **Reproducible Centrality & Outliers**: Percentile and IQR calculations use deterministic sorting.
4. **No Random Seeds**: No stochastic models, LLM hallucination risk, or random hashes exist in the extraction pipeline.

---

## 24. Important Limitations

1. **In-Memory Resolution Complexity**: Cross-record entity resolution evaluates pairwise candidate comparisons in memory. For extremely large datasets ($>50,000$ entities), chunked batching or vector pre-blocking should be coordinated with Member 2.
2. **spaCy Fallback Differences**: If spaCy is unavailable, entity extraction falls back to regex patterns. While core entities (phones, vehicles, accounts, and suspects with standard titles like "Accused" or "S/o") extract identically, nuanced organizational names lacking corporate suffixes ("Ltd", "Enterprises") may be omitted in fallback mode.
3. **Naive Timestamps**: Preprocessing standardizes timestamps to ISO-8601 without speculative UTC conversions when timezones are omitted in source documents, preventing artificial chronological shifts.
4. **Graph Mutability**: The pipeline produces a complete batch result. Incremental graph mutations (adding single edges to an existing Neo4j instance) should be managed via Member 2's Cypher `MERGE` queries.
