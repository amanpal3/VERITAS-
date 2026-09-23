# VERITAS Developer Setup & Contributing Guide

Welcome to the VERITAS development guide. This document provides clear, step-by-step instructions for setting up the local development environment for all three sub-teams (AI/NLP, Backend, and Frontend).

---

## 1. Prerequisites
Before beginning, ensure your system has the following tools installed:
- **Python**: Version `3.10` or higher (`python --version`)
- **Node.js**: Version `18.x` or higher (`node -v`) & `npm` (`npm -v`)
- **Git**: For version control
- **Docker** (Optional, for local Neo4j): Docker Desktop or container engine

---

## 2. Repository Layout Overview
```
VERITAS/
├── ai/                # Member 1: AI, NLP, Entity Resolution, Ingestion Pipeline
├── backend/           # Member 2: FastAPI, Graph Engine (NetworkX/Neo4j), REST API
├── frontend/          # Member 3: React 18, Vite, TailwindCSS, Cytoscape.js UI
├── data/              # Raw, processed, and stable demo datasets
├── docs/              # System architecture, API contracts, blueprints, schemas
├── scripts/           # Data generation, database loaders, pipeline testing
└── tests/             # Pytest test suites across AI, backend, and integration
```

---

## 3. Backend Setup (Member 2 — YOU)

### Step 3.1: Create & Activate Virtual Environment
Open your terminal at the project root (`Detective/`):

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

### Step 3.2: Install Backend Dependencies
```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### Step 3.3: Configure Environment Variables
Create a local `.env` inside `backend/` by copying the example:
```bash
cp backend/.env.example backend/.env
```
Default `.env` configuration:
```ini
# Neo4j Graph Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=veritas_password

# API Settings
API_V1_STR=/api/v1
PROJECT_NAME="VERITAS Backend"
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Monitoring & Fallback
SENTRY_DSN=
ENVIRONMENT=development
USE_IN_MEMORY_FALLBACK=true
```

### Step 3.4: Run the FastAPI Development Server
```bash
uvicorn backend.app.main:app --reload --port 8000
```
- Interactive Swagger API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 4. Frontend Setup (Member 3 — UI/UX)

### Step 4.1: Install Node Dependencies
From the repository root:
```bash
cd frontend
npm install
```

### Step 4.2: Configure Frontend Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Ensure the API base URL matches your backend:
```ini
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Step 4.3: Start the Vite Development Server
```bash
npm run dev
```
Open your browser at [http://localhost:5173](http://localhost:5173). The Vite proxy forwards `/api` calls directly to `http://localhost:8000`.

---

## 5. AI / NLP Pipeline Setup (Member 1 — AI/Data)

### Step 5.1: Install spaCy Linguistic Model
Ensure your `.venv` is active, then download the language model:
```bash
python -m spacy download en_core_web_sm
```

### Step 5.2: Run Pipeline Smoke Test
```bash
python scripts/test_pipeline.py
```
This tests raw file ingestion, entity extraction, deduplication, and JSON generation.

---

## 6. Neo4j Local Database (Optional)

If you wish to run a dedicated Neo4j instance locally via Docker:
```bash
docker run \
    --name veritas-neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/veritas_password \
    -v neo4j_data:/data \
    -d neo4j:5-community
```
- Neo4j Browser Web Console: [http://localhost:7474](http://localhost:7474)
- Bolt Connection URI: `bolt://localhost:7687`

> **Note on In-Memory Fallback:** If you do not have Neo4j installed or Docker running, VERITAS will automatically operate in **In-Memory Mode** using `NetworkX` and `data/demo/graph.json`. You do not need to install Neo4j to develop or demo the system!

---

## 7. Generating & Loading Demo Data
To regenerate the judging dataset and populate the graph store:
```bash
# 1. Generate synthetic CDRs, FIRs, and financial transactions
python scripts/seed_demo.py

# 2. Ingest demo records into the graph
python scripts/load_neo4j.py
```

---

## 8. Branching & Git Workflow
1. Never commit broken code directly to `main`.
2. Name branches by capability:
   - `feat/ai-entity-extraction`
   - `feat/backend-centrality-api`
   - `feat/frontend-cytoscape-graph`
3. Always verify tests pass before submitting a Pull Request:
   ```bash
   pytest tests/ -v
   ```
