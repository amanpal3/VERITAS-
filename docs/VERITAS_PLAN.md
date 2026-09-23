# VERITAS Hackathon Execution & Sprint Plan

This document outlines the phased 36-hour sprint roadmap, work package assignments for all three team members, quality milestones, and contingency protocols for the KAYA Hackathon.

---

## 1. 36-Hour Hackathon Sprint Schedule

```
  +-------------+   +---------------+   +---------------+   +----------------+   +---------------+
  |   PHASE 1   |-->|    PHASE 2    |-->|    PHASE 3    |-->|    PHASE 4     |-->|    PHASE 5    |
  |  Hours 0-6  |   |  Hours 6-16   |   |  Hours 16-26  |   |  Hours 26-32   |   |  Hours 32-36  |
  +-------------+   +---------------+   +---------------+   +----------------+   +---------------+
     Foundation,       Core Engine,        Cytoscape UI,        Analytics &          Rehearsal,
      Data Schema       Graph Math &        API Contract         Render Live          Pitch Deck &
     & Static Demo       AI Pipeline         Wiring Up           Deployment           Verification
```

---

## 2. Phase Breakdown & Deliverables

### Phase 1: Foundations & Demo Datasets (Hours 0 – 6)
- **Goal**: Establish project contracts, verify repository skeleton, and freeze stable synthetic demo data.
- **Milestones**:
  - [x] Complete project file structure and folder hierarchy created.
  - [x] Technical blueprints, API contracts, and schema documentation finalized.
  - [ ] Generate synthetic judging dataset (`data/demo/`) containing:
    - 20+ Person entities (kingpins, lieutenants, runners, frontmen).
    - 30+ Phone numbers with CDR call records.
    - 40+ Financial transaction ledgers showing money trails.
    - 5 Unstructured police FIR reports.
  - [ ] Export `data/demo/graph.json` so Frontend and Backend have static fixtures immediately.
- **Definition of Done (DoD)**: All three members have working local environments and identical demo datasets.

---

### Phase 2: Core Engines & Algorithm Construction (Hours 6 – 16)
- **Member 1 (AI Pipeline)**:
  - Implement `ai/ingestion/` parsers for CSV and FIR text.
  - Implement spaCy NER rules for extracting entities and aliases.
  - Implement entity resolution to merge aliases and phone formats into unified records.
- **Member 2 (Backend / Graph Engine — YOU)**:
  - Implement NetworkX graph builder (`backend/app/graph/builder.py`).
  - Implement centrality algorithms: Degree, Betweenness, and PageRank (`centrality.py`).
  - Implement multi-hop pathfinding (`pathfinder.py`) and Louvain communities (`communities.py`).
  - Implement Neo4j driver connection and fallback mechanism.
- **Member 3 (Frontend / Visualization)**:
  - Configure Vite, TailwindCSS, and Cytoscape.js canvas container.
  - Implement node styling based on entity types (icons, colors, badges).
  - Implement zoom, pan, and node click inspector handlers.
- **DoD**: Backend passes unit tests on graph calculations; Frontend renders a mock Cytoscape graph.

---

### Phase 3: API Integration & Visual Wiring (Hours 16 – 26)
- **Goal**: Connect frontend to live backend endpoints via [`docs/API_CONTRACT.md`](file:///C:/Users/amanp/OneDrive/Desktop/Detective/docs/API_CONTRACT.md).
- **Milestones**:
  - Implement FastAPI routes in `backend/app/api/`:
    - `GET /api/v1/health`
    - `GET /api/v1/graph` (returns Cytoscape formatted nodes and edges)
    - `GET /api/v1/entities` & `GET /api/v1/entities/{id}`
    - `GET /api/v1/paths/shortest?source={id}&target={id}`
    - `GET /api/v1/communities`
  - Frontend hooks up Axios API client to backend routes.
  - Implement "Find Connection" UI: selecting two suspects highlights the path in the canvas.
  - Implement filter drawer: toggle node types and relationship types dynamically.
- **DoD**: Clicking a suspect in the UI queries the live backend and renders their sub-network in real time.

---

### Phase 4: Evidence Dossiers, Analytics & Deployment (Hours 26 – 32)
- **Goal**: Integrate evidentiary provenance, analytics charts, and deploy live to Render.
- **Milestones**:
  - Implement **Evidence View Drawer**: Clicking any graph edge opens the modal showing source FIR/CDR snippet.
  - Implement Analytics Dashboard:
    - Centrality leaderboards (bar charts of top influencers).
    - Community distribution chart (breakdown of syndicates).
  - Deploy `veritas-backend` and `veritas-frontend` to **Render** using [`render.yaml`](file:///C:/Users/amanp/OneDrive/Desktop/Detective/render.yaml).
  - Integrate Sentry error monitoring across the backend.
- **DoD**: Live production URL is reachable and fully functional on public web.

---

### Phase 5: Rehearsal, Verification & Demo Polish (Hours 32 – 36)
- **Goal**: Ensure flawless presentation to hackathon judges.
- **Milestones**:
  - Execute pre-flight checklist from [`docs/Deployment.md`](file:///C:/Users/amanp/OneDrive/Desktop/Detective/docs/Deployment.md).
  - Rehearse the 8-minute demo story from [`docs/DEMO_FLOW.md`](file:///C:/Users/amanp/OneDrive/Desktop/Detective/docs/DEMO_FLOW.md).
  - Prepare backup screencast video and screenshots in case of network instability.
- **DoD**: Presentation story rehearsed twice with zero technical errors.

---

## 3. Work Package Ownership Matrix

| Work Package | Task Title | Owner | Target Completion |
| :--- | :--- | :--- | :--- |
| **WP-1.1** | Synthetic Demo Data Generator (`seed_demo.py`) | Member 1 & 2 | Hour 4 |
| **WP-1.2** | AI Ingestion & NER Extraction (`ai/`) | Member 1 | Hour 14 |
| **WP-1.3** | Entity Resolution & Deduplication | Member 1 | Hour 18 |
| **WP-2.1** | Graph Builder & Centrality Algorithms (`graph/`) | **Member 2 (YOU)** | Hour 12 |
| **WP-2.2** | Pathfinder & Community Detection Engine | **Member 2 (YOU)** | Hour 15 |
| **WP-2.3** | FastAPI Endpoints & Contract Fulfillment | **Member 2 (YOU)** | Hour 20 |
| **WP-2.4** | Hybrid Fail-Safe (NetworkX + Neo4j) & Sentry | **Member 2 (YOU)** | Hour 24 |
| **WP-3.1** | Cytoscape Network Graph Canvas & Styling | Member 3 | Hour 14 |
| **WP-3.2** | Path Highlighting & Filter Drawer | Member 3 | Hour 22 |
| **WP-3.3** | Evidence Modal & Analytics Charts | Member 3 | Hour 28 |
| **WP-DEPLOY**| Render Cloud Deployment & Health Verification | All Members | Hour 30 |

---

## 4. Contingency & Plan B Protocols

1. **Risk: Neo4j AuraDB experiences cloud latency or connection timeouts.**
   - *Protocol*: The backend includes `USE_IN_MEMORY_FALLBACK=true`. If Neo4j times out, the backend instantly routes queries through in-memory `NetworkX` without throwing an error to the frontend.
2. **Risk: spaCy NLP processing takes too long during live demonstration.**
   - *Protocol*: Use the pre-computed extracted entities in `data/demo/graph.json` for live instant 150ms query responses, with a separate screen showcasing asynchronous ingestion.
3. **Risk: CORS errors when connecting deployed frontend to deployed backend.**
   - *Protocol*: Ensure `backend/app/main.py` has `CORSMiddleware` configured with `allow_origins=["*"]` or explicit wildcard patterns for `.onrender.com`.
