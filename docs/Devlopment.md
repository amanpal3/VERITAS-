# VERITAS — Developer Setup & Development Plan

> **Engineering Guide** // Environment configuration, local execution, and the phased development execution roadmap.

---

## 1. Prerequisites

Before beginning, ensure your local development machine has:
- **Python**: Version `3.10` or higher (`python --version`)
- **Node.js**: Version `18.x` or higher (`node -v`) & `npm` (`npm -v`)
- **Git**: For version control (`git --version`)
- **Docker** (Optional, for local Neo4j container): Docker Desktop or container engine

---

## 2. Phased Development Roadmap

The development workflow is broken down into 8 sequential execution phases:

### Phase 0 — Contract Freeze
Before writing code, freeze:
- Entity JSON schema (`docs/DATA_SCHEMA.md`)
- Relationship JSON schema
- Cytoscape `/graph` response structure
- Path finding `/paths/shortest` contract
- Controlled vocabulary for entity and relationship types

### Phase 1 — Vertical Slice
Use a deterministic dataset (the 29 entities in `data/demo/`):
$$\text{Static Demo JSON} \longrightarrow \text{NetworkX} \longrightarrow \text{FastAPI /api/v1/graph} \longrightarrow \text{React / Cytoscape Canvas}$$
*Goal*: Prove end-to-end integration across all 3 tiers before building complex features.

### Phase 2 — Graph Intelligence (Member 2 — YOU)
- In-memory graph builder (`backend/app/graph/builder.py`)
- Centrality calculators: Degree, Betweenness, and PageRank (`centrality.py`)
- Community partitioning: Louvain modularity (`communities.py`)
- Pathfinder: BFS/Dijkstra multi-hop shortest paths (`pathfinder.py`)
- Graph summary metrics: density, diameter (`metrics.py`)

### Phase 3 — AI Ingestion Integration (Member 1)
- Ingest unstructured FIR text and structured CDRs/Transactions
- Run spaCy NER and custom rule extractors
- Deduplicate aliases and phone numbers into canonical records
- Validate records against schema before exporting to `data/output/`

### Phase 4 — Neo4j Database Persistence
- Persist nodes and relationships using Cypher `MERGE` statements
- Implement database session manager and connection pooling
- Verify automatic failover to NetworkX if Neo4j is unreachable

### Phase 5 — UX & Visualization Integration (Member 3)
- Connect Cytoscape canvas to live `/api/v1/graph`
- Implement node search and dynamic type filtering
- Wire up **Find Connection** path visualizer
- Implement **Evidence Drawer** showing source FIR/CDR citations on edge click
- Render Recharts centrality leaderboards and community distribution charts

### Phase 6 — Hardening & Resilience
- Standardize error handling and HTTP status codes
- Add loading spinners and empty states
- Verify CORS configuration across origins
- Configure Sentry error boundary tracking

### Phase 7 — Cloud Deployment & Rehearsal
- Deploy both services to Render via `render.yaml`
- Run automated sanity tests against the production URL
- Rehearse the 8-minute presentation story from `docs/DEMO_FLOW.md`

---

## 3. Backend Setup (Member 2 — YOU)

### 3.1 Create & Activate Virtual Environment
From the repository root (`Detective/`):

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3.2 Install Dependencies
```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### 3.3 Configure Environment Variables
Create a local `.env` inside `backend/` by copying the template:
```bash
cp backend/.env.example backend/.env
```
Default `.env` configuration:
```ini
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=veritas_password
API_V1_STR=/api/v1
PROJECT_NAME="VERITAS Backend"
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
SENTRY_DSN=
ENVIRONMENT=development
USE_IN_MEMORY_FALLBACK=true
```

### 3.4 Run FastAPI Development Server
```bash
uvicorn backend.app.main:app --reload --port 8000
```
- Swagger API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 4. Frontend Setup (Member 3 — UI/UX)

### 4.1 Install Node Dependencies
```bash
cd frontend
npm install
```

### 4.2 Configure Environment Variables
```bash
cp .env.example .env
```
Ensure the API base URL matches the backend:
```ini
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 4.3 Start Vite Development Server
```bash
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 5. AI / NLP Pipeline Setup (Member 1 — AI/Data)

### 5.1 Download spaCy Language Model
Ensure your `.venv` is active:
```bash
python -m spacy download en_core_web_sm
```

### 5.2 Run Pipeline Test
```bash
python scripts/test_pipeline.py
```

---

## 6. Neo4j Setup & Hybrid In-Memory Fallback

If you wish to run a dedicated Neo4j database locally via Docker:
```bash
docker run \
    --name veritas-neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/veritas_password \
    -v neo4j_data:/data \
    -d neo4j:5-community
```
- Neo4j Web Console: [http://localhost:7474](http://localhost:7474)

> [!TIP]
> **No Docker? No Problem!**
> If Neo4j is not installed, VERITAS automatically defaults to **In-Memory NetworkX Mode** using `data/demo/graph.json`. You do not need to install Neo4j to develop or demo the system!

---

## 7. Generating & Loading Demo Data
```bash
# 1. Generate synthetic FIRs, CDRs, and financial ledgers
python scripts/seed_demo.py

# 2. Ingest records into Neo4j (if running)
python scripts/load_neo4j.py

# 3. Verify graph connectivity and referential integrity (6/6 checks)
python scripts/test_pipeline.py
```
