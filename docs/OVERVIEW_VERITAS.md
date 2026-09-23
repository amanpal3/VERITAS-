# 🔍 VERITAS — Team Master Overview & Quickstart Guide

> **For All Team Members**: Member 1 (AI/NLP), Member 2 (Backend/Graph), and Member 3 (UI/UX).  
> **Read this file first** to understand what we are building, who owns what, how the parts fit together, and how we will win the hackathon!

---

## 1. What is VERITAS? (The 2-Minute Summary)

**VERITAS** is an AI-powered criminal network intelligence system for law enforcement investigators.

### The Real-World Problem
Police and intelligence agencies collect massive amounts of data from different places:
- **Police FIR reports & interrogation logs** (Unstructured text)
- **Call Detail Records - CDRs** (Who called whom, when, and from what cell tower)
- **Banking & Hawala records** (Money transfers, structured cash deposits)
- **Surveillance & vehicle registries** (Vehicle plates, safehouses)

Currently, investigators analyze these in Excel spreadsheets and siloed databases. **They miss indirect connections.** A street-level drug courier caught at a border checkpoint appears completely unrelated to the wealthy mastermind funding the whole operation.

### The VERITAS Solution
VERITAS connects all the dots automatically:
$$\text{Raw Files (FIR/CDR/Bank)} \longrightarrow \text{AI Extraction} \longrightarrow \text{Knowledge Graph} \longrightarrow \text{FastAPI} \longrightarrow \text{Cytoscape UI}$$

### The Golden Principle of VERITAS
> [!IMPORTANT]
> **VERITAS supports investigation; it does NOT make guilt determinations.**
> An algorithm score is an *analytical signal*, not legal proof. Every single link in our graph links directly to **source evidence** (the exact sentence in the FIR or the exact CDR call log row).

---

## 2. Who Does What? (3-Member Work Division)

We have divided the project into 3 clean, independent layers so **nobody waits for anyone else**:

```text
 ┌────────────────────────────────┐
 │ MEMBER 1: AI / NLP / DATA      │ ──► Produces: data/output/entities.json & relationships.json
 └────────────────┬───────────────┘
                  │ (Canonical JSON Contract)
                  ▼
 ┌────────────────────────────────┐
 │ MEMBER 2: BACKEND & GRAPH      │ ──► Produces: FastAPI REST API & Graph Algorithms
 └────────────────┬───────────────┘
                  │ (REST API Contract: /api/v1/graph, /paths/shortest, etc.)
                  ▼
 ┌────────────────────────────────┐
 │ MEMBER 3: FRONTEND / UI/UX     │ ──► Produces: React + Cytoscape.js Interactive Dashboard
 └────────────────────────────────┘
```

### 👤 Member 1: AI / NLP / Data
- **Folder**: `ai/`
- **Tech**: Python, pandas, spaCy, regex rules
- **Job**:
  1. Ingest raw text FIRs (`ai/ingestion/`) and CSVs (CDRs, bank ledgers).
  2. Run Named Entity Recognition (NER) to find: People, Phones, Vehicles, Locations, Organizations, and Bank Accounts (`ai/extraction/`).
  3. Extract relationships (who called whom, who owns what vehicle, who manages which company).
  4. Deduplicate aliases and phone formats (Entity Resolution) (`ai/resolution/`).
- **Deliverable**: Export clean, standardized `entities.json` and `relationships.json`.

### 👤 Member 2: Backend & Graph Intelligence (YOU)
- **Folder**: `backend/`
- **Tech**: Python, FastAPI, NetworkX, Neo4j, Cypher, Pydantic, Sentry
- **Job**:
  1. Ingest Member 1's JSON and construct the Knowledge Graph (`backend/app/graph/builder.py`).
  2. Implement graph algorithms (`backend/app/graph/`):
     - **Degree Centrality**: Finds busy communication hubs.
     - **Betweenness Centrality**: Finds brokers bridging two separate gangs.
     - **PageRank**: Finds hidden kingpins.
     - **Louvain Communities**: Groups suspects into colored sub-gangs.
     - **Multi-Hop Pathfinder**: Traces the shortest path between any two suspects.
  3. Expose REST endpoints under `/api/v1/` (`backend/app/api/`).
  4. Ensure **Hybrid Fail-Safe**: If Neo4j is offline, instantly serve from in-memory NetworkX!
- **Deliverable**: High-speed, robust REST API deployed on Render.

### 👤 Member 3: UI / UX & Visualization
- **Folder**: `frontend/`
- **Tech**: React 18, Vite, TailwindCSS, Cytoscape.js, Recharts, Lucide Icons
- **Job**:
  1. Render the interactive network graph using Cytoscape.js (`frontend/src/graph/`).
  2. Implement physics layout (`fcose`) so nodes don't overlap.
  3. Color-code nodes by entity type (Person = Blue, Phone = Purple, Vehicle = Orange, etc.).
  4. Build the **"Find Connection"** feature: select 2 suspects $\to$ highlight the glowing path.
  5. Build the **Evidence Drawer**: click any edge $\to$ pop up the exact FIR or CDR snippet.
  6. Render analytics charts (PageRank leaderboards and community distribution).
- **Deliverable**: Smooth, modern, cyber-investigative dark-mode dashboard deployed on Render.

---

## 3. The Hackathon Demo Story: "Operation Shadow Syndicate"

To impress the judges, our demo tells **one continuous, gripping investigation story** in 5 minutes:

```text
                                  [ THE INVESTIGATIVE CHAIN ]

 [Arjun Verma]  ──(SUPERVISES)──►  [Rajesh Kumar]  ──(COORDINATES)──►  [Kabir Mirza]
  Street Courier                    Logistics Handler                    Enforcer / Cell Leader
  (Arrested at border)              (Okhla Warehouse)                    (Burner Phones)
                                                                               │
                                                                               ▼ (USES)
 [Vikram Singhania] ◄──(CALLED)── [Secure Line] ◄────(CALLED)──── [Burner Phone]
  SYNDICATE MASTERMIND             PH001 (Vasant Vihar)            PH004 (Aerocity)
  (Hidden Kingpin)
```

1. **The Hook**: Police arrest driver **Arjun Verma (P006)** with 14kg contraband at Singhu border (FIR #104). Arjun claims he is just a hired driver and doesn't know the boss.
2. **The Exploration**: The analyst opens VERITAS, searches for `Arjun Verma`, and expands his neighborhood. We see his phone connected to logistics coordinator **Rajesh Kumar (P003)**.
3. **The Hidden Link (Pathfinder)**: The analyst selects `Arjun Verma` $\to$ `Vikramaditya Singhania` and clicks **Find Connection**.
4. **The "Aha!" Moment**: VERITAS instantly illuminates the 5-hop path through encrypted burner phones and logistics handlers, proving that this street arrest ties directly to the syndicate kingpin!
5. **The Proof (Evidence Drawer)**: The judge asks: *"How do you know Rajesh coordinates with Kabir?"* — The presenter clicks the edge, and the screen pops up the exact excerpt from *Surveillance Report INT-DEL-2026-409*.
6. **The Financial Laundering**: Open the Analytics tab to show **Tariq Sheikh (P002)** scoring the highest **Betweenness Centrality**, acting as the vital Hawala broker laundering money into shell company *Astra Logistics Ltd*.

---

## 4. Key Data Entities & Graph Schema

When writing code or building UI components, use these standard labels:

### The 6 Entity (Node) Types
| Entity Type | Description | Color Code Recommendation | Example ID |
| :--- | :--- | :--- | :--- |
| `Person` | Suspects, couriers, kingpins, directors | `#3B82F6` (Electric Blue) | `P001` (Vikram Singhania) |
| `Phone` | Mobile phones, burner SIMs, secure lines | `#8B5CF6` (Purple) | `PH001` (+919811010001) |
| `Vehicle` | Trucks, cars, transport vans | `#F59E0B` (Amber / Orange) | `V001` (DL-1C-0001) |
| `Organization` | Corporate shells, Hawala counters | `#10B981` (Emerald Green) | `ORG001` (Astra Logistics) |
| `Location` | Warehouses, safehouses, vaults | `#EC4899` (Pink) | `LOC001` (Okhla Godown) |
| `BankAccount` | Smurfing accounts, Hawala ledgers | `#06B6D4` (Cyan) | `BA001` (ACC-SINGH-9901) |

### The Core Relationship (Edge) Types
- `CALLED`: Telecom voice call or SMS between two phones.
- `TRANSACTED_WITH`: Financial fund transfer between accounts.
- `USES_PHONE`: A person operating a mobile device.
- `OWNS` / `OPERATES`: A person owning or driving a vehicle.
- `SUPERVISES` / `COORDINATES_WITH`: Criminal hierarchy and operational coordination.
- `CONTROLS` / `MEMBER_OF`: Corporate ownership or syndicate membership.
- `LOCATED_AT`: Presence at a physical address.

---

## 5. API Endpoints Quick-Reference

All endpoints are hosted at `/api/v1`:

| Method | Endpoint | What it Returns |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service status & confirms if backend is using Neo4j or in-memory NetworkX. |
| `GET` | `/api/v1/graph` | Full Cytoscape-formatted nodes and edges for the graph canvas. |
| `GET` | `/api/v1/entities` | Searchable, paginated list of all entities. |
| `GET` | `/api/v1/entities/{id}` | Dossier with risk score, metrics, direct connections, and citations. |
| `GET` | `/api/v1/paths/shortest` | Shortest path between `?source=...` and `?target=...` with full node/edge chain. |
| `GET` | `/api/v1/communities` | Detected criminal gangs/clusters and their member suspect IDs. |
| `GET` | `/api/v1/analytics/centrality`| Top rankings by `degree`, `betweenness`, or `pagerank`. |

---

## 6. How to Run & Test Everything Locally

### 1. Generate / Reset the Demo Data
```bash
python scripts/seed_demo.py
```
This generates 5 FIR text reports, 64 CDRs, 51 transactions, 29 entities, and 33 edges into `data/demo/`.

### 2. Verify Everything with the Automated Audit
```bash
python scripts/test_pipeline.py
```
Should output: `INTEGRITY AUDIT SCORE: 6/6 PASSED`.

### 3. Run the Backend (FastAPI)
```bash
python -m venv .venv
# Activate: Windows (.\.venv\Scripts\Activate.ps1) | Mac/Linux (source .venv/bin/activate)
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```
- Swagger API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 4. Run the Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

---

## 7. Golden Rules for Winning the Hackathon

1. **Never Depend on Live Heavy AI During the Presentation**: Live extraction of huge documents can lag. Use the pre-computed dataset in `data/demo/graph.json` so queries respond in **100 milliseconds**.
2. **Neo4j Fail-Safe is Active**: If Neo4j AuraDB experiences cloud latency, the backend will automatically fall back to **in-memory NetworkX** without throwing any errors to the user.
3. **Explainability Wins Judges Over**: When showing any connection or score, always emphasize: *"Here is the FIR paragraph and timestamp that proves this connection."*
4. **Stick to the Contracts**: All API responses and data formats are frozen in [`docs/API_CONTRACT.md`](file:///C:/Users/amanp/OneDrive/Desktop/Detective/docs/API_CONTRACT.md). If you follow the contract, our code will integrate on the first try!

---

### Questions or Deep-Dive Specs?
Check the other docs in `docs/`:
- Technical Architecture: [`docs/ARCHITECTURE.md`](file:///C:/Users/amanp/OneDrive/Desktop/Detective/docs/ARCHITECTURE.md)
- Complete Blueprint: [`docs/Blueprint.md`](file:///C:/Users/amanp/OneDrive/Desktop/Detective/docs/Blueprint.md)
- Development Roadmap: [`docs/Devlopment.md`](file:///C:/Users/amanp/OneDrive/Desktop/Detective/docs/Devlopment.md)
- Presentation Rehearsal Script: [`docs/DEMO_FLOW.md`](file:///C:/Users/amanp/OneDrive/Desktop/Detective/docs/DEMO_FLOW.md)
