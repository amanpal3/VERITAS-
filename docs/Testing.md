# VERITAS Comprehensive Testing Strategy & Quality Assurance

This document details the testing architecture, validation protocols, test suites, and quality gates for the VERITAS platform.

---

## 1. Testing Philosophy & Test Pyramid

VERITAS enforces rigorous verification across every stage of the data and analytical pipeline to ensure intelligence reports and graph queries are strictly grounded in fact.

```
                  / \
                 / E2E \       End-to-End Demo Flow & API Smoke Tests
                /-------\
               /   INT   \     Cross-Module Integration (AI Ingestion -> Graph -> API)
              /-----------\
             /    UNIT     \   Algorithmic Correctness (Centrality, Resolution, NER)
            +---------------+
```

---

## 2. Test Suite Structure

```
tests/
├── ai/
│   ├── test_parsers.py         # CSV & Document parser sanity
│   ├── test_ner.py             # Entity extraction accuracy
│   ├── test_resolution.py      # Entity deduplication & alias matching
│   └── test_anomaly.py         # Anomaly detector logic
├── backend/
│   ├── test_graph_builder.py   # In-memory NetworkX & Neo4j model creation
│   ├── test_centrality.py      # Degree, Betweenness, and PageRank mathematics
│   ├── test_pathfinder.py      # Dijkstra & BFS multi-hop pathfinding
│   ├── test_communities.py     # Louvain modularity partitioning
│   └── test_api_routes.py      # FastAPI endpoint contracts & status codes
└── integration/
    ├── test_pipeline_e2e.py    # Raw Record -> Extracted Entities -> Graph Query
    └── test_failover.py        # Neo4j offline -> NetworkX fallback behavior
```

---

## 3. Backend & Graph Testing Protocols (`tests/backend/`)

### 3.1 Centrality Algorithm Validation
- **Ground-Truth Toy Graph**: Unit tests instantiate a known "Kite Graph" (Krackhardt kite network) where nodes have pre-calculated analytical properties.
- **Verification Criteria**:
  - Node with highest Degree Centrality must match the known hub.
  - Node bridging two components must score the highest Betweenness Centrality.
  - All centrality scores must normalize within range $[0.0, 1.0]$.

### 3.2 Pathfinding Validation
- **Multi-Hop Traversal**: Tests verify that given a 3-hop chain (`Suspect A -> Phone 1 -> Phone 2 -> Suspect B`), calling `/api/v1/paths/shortest` accurately returns all 4 nodes and 3 edges in sequential order.
- **Disconnected Subgraphs**: If two suspects have no path, the endpoint must return a structured 404/200 empty path indicator rather than crashing.

### 3.3 Community Detection Validation
- **Cluster Consistency**: Tests ensure tightly connected cliques are assigned identical `community_id` tags while disconnected components receive distinct IDs.

### 3.4 FastAPI Endpoint Testing
- Leverages `httpx.AsyncClient` or FastAPI `TestClient`:
  - `GET /api/v1/health` returns HTTP 200 with status `"healthy"`.
  - `GET /api/v1/graph` returns JSON containing `nodes` and `edges` arrays formatted for Cytoscape.js.
  - `GET /api/v1/entities/{id}` returns HTTP 404 with structured error response for invalid IDs.

---

## 4. AI & NLP Pipeline Testing Protocols (`tests/ai/`)

### 4.1 NER Extraction Accuracy
- **Synthetic Test Passages**: Predefined sentences containing known entities:
  - *"FIR states Rajesh Kumar (alias Raju) was spotted near Connaught Place driving silver Swift DL-3C-1234."*
  - Expected extractions:
    - `PERSON`: "Rajesh Kumar", Alias: "Raju"
    - `LOCATION`: "Connaught Place"
    - `VEHICLE`: "Swift", Plate: "DL-3C-1234"
- **Threshold**: Extraction confidence score must exceed `0.80`.

### 4.2 Entity Resolution & Deduplication
- **Fuzzy Match Checks**:
  - Names: `"Vikramaditya Singh"` and `"Vikram Singh"` with identical phone numbers must merge into a single entity.
  - Phones: `"+919811001122"` and `"09811001122"` must normalize and resolve to the same node ID.
- **Provenance Retention**: Merged nodes must retain all source document references in an array to avoid losing evidence.

### 4.3 Anomaly Detection Validation
- **Synthetic Spikes**: Ingest a CDR log with 50 calls in 30 minutes between two burner phones; test that `detector.py` flags this pair with an `"URGENT_COMMUNICATION_BURST"` warning.

---

## 5. End-to-End Integration Testing (`tests/integration/`)

### 5.1 Pipeline Full-Cycle Test
1. Script invokes `ai/pipeline.py` on a mini test dataset in `data/raw/test/`.
2. Verifies output JSON in `data/output/test/`.
3. Ingests JSON into `backend/app/graph/builder.py`.
4. Executes query through FastAPI client to retrieve the newly formed graph.
5. Verifies that every edge contains non-null `provenance` metadata.

### 5.2 Fail-Safe Graceful Degradation Test
- Simulate Neo4j unavailability by passing an invalid port (`bolt://localhost:9999`).
- Ensure backend initializes in **In-Memory NetworkX Mode** without raising uncaught exceptions, and returns HTTP 200 on graph requests.

---

## 6. Running Tests & Quality Gates

Run all automated tests:
```bash
pytest tests/ -v
```

Run only backend tests:
```bash
pytest tests/backend/ -v
```

Generate test coverage report:
```bash
pytest --cov=backend/app --cov=ai tests/ --cov-report=term-missing
```

### Pre-Commit Quality Gate:
Before pushing to Git:
1. `pytest` passes with 0 failures.
2. Code passes syntax formatting (`flake8` / `black` for Python, `eslint` for frontend).
3. No hardcoded database credentials or secrets exist in the codebase.
