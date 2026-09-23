# VERITAS System Architecture & Technical Blueprint

## 1. System Overview & Architectural Vision
VERITAS is an enterprise-grade criminal network intelligence platform designed to ingest multi-source forensic data (police FIRs, Call Detail Records, financial transactions, and surveillance reports), extract entities and semantic relationships, construct an explainable knowledge graph, and perform advanced graph analytics to empower law enforcement investigators.

```
+-------------------------------------------------------------------------------+
|                                DATA INGESTION                                 |
|  FIR Documents (PDF/TXT) | Telecom CDRs (CSV) | Banking / Financial Logs (CSV) |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                          AI / NLP PIPELINE (`ai/`)                             |
|  +-------------------+   +--------------------+   +-----------------------+   |
|  | Document Parsers  |-->| NER & Extraction   |-->| Entity Resolution     |   |
|  | & Preprocessing   |   | (spaCy/Regex/Rules)|   | (Fuzzy/Phone Normal.) |   |
|  +-------------------+   +--------------------+   +-----------------------+   |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                       GRAPH STORAGE & PERSISTENCE                             |
|   Primary: Neo4j Graph Database (AuraDB / Local Bolt)                         |
|   Fail-Safe: In-Memory NetworkX Graph Cache & Demo Fixtures                   |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                      BACKEND GRAPH INTELLIGENCE (`backend/`)                  |
|  +----------------------+  +---------------------+  +----------------------+  |
|  | Centrality Engine    |  | Community Detection |  | Multi-Hop Pathfinder |  |
|  | (PageRank/Degree/Bet)|  | (Louvain Partition) |  | (Dijkstra / BFS)     |  |
|  +----------------------+  +---------------------+  +----------------------+  |
|  +-------------------------------------------------------------------------+  |
|  | FastAPI REST Interface (/api/v1/graph, /entities, /paths, /analytics)   |  |
|  | Sentry Monitoring & Robust Error Boundary Handlers                      |  |
|  +-------------------------------------------------------------------------+  |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                       INVESTIGATOR DASHBOARD (`frontend/`)                    |
|  +-------------------+  +--------------------+  +--------------------------+  |
|  | Cytoscape.js      |  | Suspect Dossier    |  | Evidence / Provenance    |  |
|  | Interactive Graph |  | Details Panel      |  | Modal (Source Records)   |  |
|  +-------------------+  +--------------------+  +--------------------------+  |
|  +-------------------------------------------------------------------------+  |
|  | Analytics Charts (Recharts) | Global Search & Entity/Edge Type Filters  |  |
|  +-------------------------------------------------------------------------+  |
+-------------------------------------------------------------------------------+
```

---

## 2. Core Subsystems

### 2.1 AI & NLP Extraction Subsystem (`ai/`)
1. **Ingestion & Parsers (`ai/ingestion/`)**:
   - `csv_parser.py`: Stream-parses telecom CDRs (timestamp, caller, receiver, duration, tower_id) and financial ledgers (sender, receiver, amount, currency, timestamp).
   - `document_parser.py`: Ingests free-form police complaints, FIR records, witness testimonies, and surveillance reports.
   - `preprocessing.py`: Cleans raw text, strips noise, standardizes date formats, and normalizes phone numbers to standard international formats.
2. **Extraction Engine (`ai/extraction/`)**:
   - `ner.py`: Identifies core investigative entity types:
     - `PERSON`: Suspect names, aliases, witnesses.
     - `PHONE`: Mobile numbers, SIM IMSIs, IMEI references.
     - `VEHICLE`: License plates, vehicle models, colors.
     - `LOCATION`: Addresses, coordinates, cities, safehouses.
     - `ORGANIZATION`: Front companies, shell corporations, gangs, syndicates.
     - `BANK_ACCOUNT`: Account numbers, IFSC/SWIFT codes.
   - `relation_extractor.py`: Maps sentence semantics to typed edges (`CALLED`, `TRANSACTED_WITH`, `ASSOCIATED_WITH`, `OWNS`, `LOCATED_AT`, `MEMBER_OF`).
   - `normalizer.py`: Standardizes casing, removes honorifics, and strips punctuation from identifiers.
3. **Resolution & Anomaly (`ai/resolution/`, `ai/anomaly/`)**:
   - `entity_resolver.py`: Deduplicates multiple mentions of the same individual across separate documents using fuzzy string distance and shared phone/address anchors.
   - `detector.py`: Scans structured records for high-risk anomalies (e.g., sudden bursts in communication preceding an incident, circular fund routing, or multiple SIMs tied to one IMEI).

---

### 2.2 Backend & Graph Engine Subsystem (`backend/app/`)
1. **Database Adapter & Fail-Safe Strategy (`backend/app/database/`)**:
   - `neo4j.py`: Implements robust connection pooling to Neo4j.
   - **Hybrid Fail-Safe Architecture**: The backend checks Neo4j connectivity at startup. If Neo4j is offline or unavailable, the backend automatically falls back to an in-memory `NetworkX` graph seeded from `data/demo/graph.json`. This ensures 100% uptime during hackathon judging.
2. **Graph Algorithms (`backend/app/graph/`)**:
   - `centrality.py`:
     - **Degree Centrality**: Identifies high-volume communicators and hub nodes.
     - **Betweenness Centrality**: Pinpoints critical gatekeepers/brokers bridging two disparate criminal cliques.
     - **PageRank**: Computes structural influence across the entire syndicate network.
   - `communities.py`: Implements Louvain modularity algorithm to group dense suspect clusters into colored sub-gangs.
   - `pathfinder.py`: Solves shortest paths and all simple paths between any two selected entities, returning every intermediary node and edge with full metadata.
   - `metrics.py`: Computes network density, diameter, reciprocity, and connected component counts.
3. **API Layer (`backend/app/api/`)**:
   - Exposes clean, typed REST endpoints compliant with [`docs/API_CONTRACT.md`](file:///C:/Users/amanp/OneDrive/Desktop/Detective/docs/API_CONTRACT.md).
   - Validates all query parameters and JSON payloads using Pydantic models.
   - Integrated Sentry error monitoring with graceful error degradation.

---

### 2.3 Frontend & Visualization Subsystem (`frontend/src/`)
1. **Cytoscape.js Canvas (`frontend/src/graph/`)**:
   - Employs physics-based layouts (`fcose` / `cola`) for force-directed node positioning without overlapping labels.
   - Dynamic node visual styling based on entity type (icons/colors) and degree centrality (node size scaling).
   - Interactive events: Click node to focus/inspect; Click edge to view provenance modal; Double-click to expand 1-hop neighborhood.
2. **State & Filter Management (`frontend/src/pages/`)**:
   - Filter by entity type (hide locations, isolate phones).
   - Filter by edge confidence or transaction threshold.
   - Path finding mode: Select Source Node and Target Node $\to$ Highlight shortest path with glowing neon stroke.
3. **Evidence & Dossier Drawer (`frontend/src/components/evidence/`)**:
   - Every graph connection links directly to the raw FIR paragraph, CDR row, or bank transaction ID. Clicking an edge immediately displays this evidentiary basis.

---

## 3. Data Flow & Provenance Architecture

```
[Raw Document/Row]
       |
       v
[Extraction with Metadata]
       |
       +---> Provenance Record:
       |        source_id: "FIR-2026-089"
       |        source_type: "POLICE_REPORT"
       |        timestamp: "2026-03-12T14:30:00Z"
       |        confidence: 0.94
       |        raw_snippet: "...observed entering black Honda Civic plate DL-4C-9901..."
       v
[Graph Edge Creation]
       Edge(
         type="OPERATES_VEHICLE",
         source="P001",
         target="V101",
         metadata={...provenance...}
       )
```

By embedding provenance into every edge attribute, the platform maintains absolute explainability, satisfying strict law enforcement evidentiary requirements.
