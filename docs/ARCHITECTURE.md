# VERITAS — System Architecture

> **Architectural Blueprint & Layer Boundaries** // Multi-tier decoupled architecture for high-concurrency graph analytics and intelligence visualization.

---

## 1. High-Level System Architecture

```text
                     ┌───────────────────────────────────────┐
                     │          RAW DATA SOURCES             │
                     │  FIRs/Police Reports | Telecom CDRs   │
                     │  Banking Ledgers | Field Surveillance │
                     └───────────────────┬───────────────────┘
                                         │
                                         ▼
                     ┌───────────────────────────────────────┐
                     │       MEMBER 1: AI / NLP LAYER        │
                     │  - Ingestion & Text Normalization     │
                     │  - Named Entity Recognition (spaCy)   │
                     │  - Relationship Extraction & Rules    │
                     │  - Entity Resolution & Deduplication  │
                     └───────────────────┬───────────────────┘
                                         │ Canonical JSON Entities & Relations
                                         ▼
                     ┌───────────────────────────────────────┐
                     │     MEMBER 2: GRAPH & API BACKEND     │
                     │  - Knowledge Graph Construction       │
                     │  - Primary: Neo4j Graph Database      │
                     │  - Fail-Safe: In-Memory NetworkX      │
                     │  - Centrality, Louvain & Pathfinding  │
                     │  - FastAPI REST Interface (/api/v1/*) │
                     │  - Sentry Error Boundary Monitoring   │
                     └───────────────────┬───────────────────┘
                                         │ Cytoscape-formatted JSON & REST APIs
                                         ▼
                     ┌───────────────────────────────────────┐
                     │       MEMBER 3: FRONTEND & UI         │
                     │  - React 18 + Vite + TailwindCSS      │
                     │  - Cytoscape.js Force-Directed Graph  │
                     │  - Recharts Centrality & Communities  │
                     │  - Evidence Provenance Drawer Modal   │
                     │  - Suspect Dossier Panel & Filters    │
                     └───────────────────────────────────────┘
```

---

## 2. Team Responsibility Boundaries

| Role | Team Member | Primary Domain | Core Deliverable |
| :--- | :--- | :--- | :--- |
| **Member 1** | AI / NLP / Data | Ingestion, NLP extraction, entity resolution, anomaly detection | Canonical, normalized entity & relationship records (`data/output/`) with provenance citations. |
| **Member 2** | **Backend / Graph Intelligence (YOU)** | Graph algorithms, Neo4j, NetworkX, FastAPI, deployment | High-performance REST API, graph pathfinding, centrality computation, and cloud backend on Render. |
| **Member 3** | UI / UX Visualization | React 18, Vite, TailwindCSS, Cytoscape.js, Recharts | Interactive visual investigation interface, path highlighting, suspect dossiers, and evidence drawers. |
| **All Members** | Cross-Team Coordination | Contracts, testing, documentation, and live rehearsal | Frozen API contract, unified demo dataset, automated test suite, and Render cloud deployment. |

---

## 3. Backend Architectural Layers

To guarantee modularity, testability, and zero tight coupling, the backend is organized into 4 distinct execution layers:

```text
HTTP Clients (React UI)
       │
       ▼
[ Layer 1: API Routers (`backend/app/api/`) ]
  - Validates request schemas with Pydantic
  - Handles routing, CORS, and query parameters
  - Captures exceptions via Sentry error boundaries
       │
       ▼
[ Layer 2: Business Logic Services (`backend/app/services/`) ]
  - Coordinates multi-step queries (e.g. ego-network + centrality)
  - Enforces caching and filters
       │
       ▼
[ Layer 3: Graph Engine & Algorithms (`backend/app/graph/`) ]
  - Decoupled from HTTP framework for independent unit testing
  - Centrality calculator (Degree, Betweenness, PageRank)
  - Community partitioning (Louvain Modularity)
  - Pathfinder (Shortest paths, all simple paths)
       │
       ▼
[ Layer 4: Database & Cache Adapters (`backend/app/database/`) ]
  - Neo4j driver with connection pooling and Cypher queries
  - Automatic In-Memory NetworkX fallback loaded from `data/demo/graph.json`
```

---

## 4. Evidentiary Provenance Pipeline

VERITAS guarantees 100% explainability by binding every graph edge to its source evidence at creation time:

```text
[Raw Input Record]
       │
       ▼
[Extraction with Metadata] ──► Provenance Payload:
       │                         - source_id: "FIR-104/2026"
       │                         - source_type: "POLICE_REPORT"
       │                         - timestamp: "2026-02-12T23:45:00Z"
       │                         - confidence: 0.98
       │                         - snippet: "...accused stated cargo was received from Rajesh Kumar..."
       ▼
[Graph Edge Created] ──► Edge(id="R003", source="P006", target="P003", type="SUPERVISES", provenance={...})
```

When an investigator clicks any connection in Cytoscape, the frontend inspects the edge's `provenance` object and displays the exact underlying police complaint, CDR call log, or bank ledger row.
