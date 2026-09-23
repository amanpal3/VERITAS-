# VERITAS — AI-Powered Criminal Network Analysis & Intelligence Platform

> **KAYA Hackathon 2026** // Transforming fragmented law enforcement records into an explainable relationship graph to uncover hidden syndicates, financial trails, and criminal kingpins.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![Cytoscape.js](https://img.shields.io/badge/Cytoscape.js-3.28%2B-orange.svg)](https://js.cytoscape.org/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.x-blue.svg)](https://neo4j.com/)
[![NetworkX](https://img.shields.io/badge/NetworkX-3.2%2B-lightgrey.svg)](https://networkx.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4%2B-38B2AC.svg)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 1. Executive Summary & Problem Statement

Modern criminal operations are increasingly networked, distributed, and multi-layered. Law enforcement agencies capture massive volumes of data across siloed systems:
- **Unstructured text**: Police FIR reports, interrogation summaries, surveillance logs.
- **Telecom records**: Call Detail Records (CDRs), cell tower triangulations, burner phone bursts.
- **Financial channels**: Banking transactions, Hawala ledgers, structured cash deposits.
- **Physical registries**: Vehicle registrations, safehouses, commercial addresses.

**The Core Challenge**: Investigators struggle to uncover hidden multi-hop connections because data is fragmented and manual spreadsheet analysis fails to reveal indirect links. A relationship that appears trivial in isolation becomes critical when combined across sources.

**The VERITAS Solution**: An automated intelligence system that ingests heterogeneous structured and unstructured records, extracts and resolves entities, constructs a knowledge graph, runs structural network algorithms (Centrality, Louvain Community Detection, Dijkstra Pathfinding), and renders an interactive, explainable investigation dashboard.

---

## 2. Core Capabilities & Architectural Highlights

- 🔍 **Multi-Source Data Ingestion**: Concurrently parses unstructured police complaints (PDF/TXT) and structured CSV records (CDRs, bank ledgers).
- 🧠 **NLP & Named Entity Recognition (NER)**: Extracts key investigative entities: `Person`, `Phone`, `Vehicle`, `Organization`, `Location`, and `BankAccount`.
- 🔗 **Entity Resolution & Alias Disambiguation**: Uses fuzzy matching (Jaro-Winkler, Levenshtein, Metaphone) to unify multiple aliases and phone formats into singular suspect dossiers.
- 🕸️ **Interactive Cytoscape.js Graph Visualization**: High-performance canvas featuring force-directed physics layouts (`fcose`), entity-type styling, and interactive neighborhood expansion.
- 👑 **Structural Influencer Detection**: Computes **PageRank**, **Betweenness Centrality**, and **Degree Centrality** to pinpoint kingpins and cross-gang intermediaries.
- 🧭 **Multi-Hop Path Finder**: Discovers indirect connection paths between any two suspects (e.g., *Street Courier $\to$ Logistics Handler $\to$ Burner Phone $\to$ Hawala Broker $\to$ Syndicate Kingpin*).
- 🏷️ **100% Explainable Provenance**: Every graph edge preserves links to supporting evidence (source document ID, timestamps, confidence scores, and raw sentence snippets).
- 🛡️ **Hybrid Fail-Safe Architecture**: Automatically runs in **In-Memory NetworkX Mode** if Neo4j is offline, guaranteeing 100% uptime during live presentations.

---

## 3. End-to-End System Pipeline

```
+-------------------------------------------------------------------------------+
|                            MULTI-SOURCE RAW DATA                              |
|   Police FIRs (TXT)   |   Telecom CDRs (CSV)   |   Bank / Hawala Ledger (CSV) |
+-------------------------------------------------------------------------------+
                                       │
                                       ▼
+-------------------------------------------------------------------------------+
|                           AI / NLP PIPELINE (`ai/`)                           |
|       [Text Ingestion] ──► [NER & Extraction] ──► [Entity Resolution]         |
+-------------------------------------------------------------------------------+
                                       │
                                       ▼
+-------------------------------------------------------------------------------+
|                         GRAPH STORAGE & ENGINE (`backend/`)                   |
|   Neo4j Knowledge Graph (AuraDB / Bolt)   ◄──►   In-Memory NetworkX Cache     |
|   ┌────────────────────────────────────────────────────────────────────────┐  |
|   │ Algorithms: Degree | Betweenness | PageRank | Louvain | Pathfinding    │  |
|   └────────────────────────────────────────────────────────────────────────┘  |
|   FastAPI REST Engine: /api/v1/graph, /entities, /paths, /communities         |
+-------------------------------------------------------------------------------+
                                       │
                                       ▼
+-------------------------------------------------------------------------------+
|                    INVESTIGATOR VISUAL DASHBOARD (`frontend/`)                |
|   Cytoscape.js Graph Canvas | Suspect Dossier Panel | Evidence Provenance UI  |
+-------------------------------------------------------------------------------+
```

---

## 4. Repository Structure

```
VERITAS/
├── ai/                     # Member 1: AI, NLP, Entity Resolution, Ingestion Pipeline
│   ├── ingestion/          # CSV and document text parsers
│   ├── extraction/         # spaCy NER and relationship extraction
│   ├── resolution/         # Entity deduplication and fuzzy matching
│   ├── anomaly/            # Telecom burst and financial anomaly detection
│   └── pipeline.py         # End-to-end ingestion pipeline runner
│
├── backend/                # Member 2: YOU (Backend, Graph Intelligence & APIs)
│   ├── app/
│   │   ├── api/            # FastAPI routes (/graph, /entities, /paths, /analytics)
│   │   ├── core/           # Settings, configurations, and exception handlers
│   │   ├── database/       # Neo4j driver and Cypher query repositories
│   │   ├── graph/          # NetworkX builder, centrality, communities, pathfinder
│   │   ├── models/         # Pydantic entity, relationship, and response models
│   │   ├── services/       # Graph, entity, and analytics business logic
│   │   └── main.py         # Application entrypoint & CORS middleware
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variable template
│
├── frontend/               # Member 3: UI/UX & Visualization
│   ├── src/
│   │   ├── api/            # Axios API client modules
│   │   ├── charts/         # Recharts centrality & community distributions
│   │   ├── components/     # Evidence drawers, filter bars, suspect dossiers
│   │   ├── graph/          # Cytoscape.js canvas, styles, and graph formatters
│   │   ├── pages/          # Dashboard, NetworkAnalysis, EntityDetails, Analytics
│   │   ├── App.jsx         # App shell and navigation
│   │   └── main.jsx        # React root entrypoint
│   ├── package.json        # Node dependencies (React 18, Vite, Cytoscape, Tailwind)
│   └── vite.config.js      # Vite build and proxy settings
│
├── data/
│   └── demo/               # Stable judging dataset (FIRs, CDRs, Transactions, Graph JSON)
│
├── docs/                   # Complete Technical Documentation
│   ├── PRD.md              # Product Requirements Document
│   ├── ARCHITECTURE.md     # Architecture specifications
│   ├── Blueprint.md        # Technical component blueprint
│   ├── Devlopment.md       # Developer setup and contribution guide
│   ├── Testing.md          # Comprehensive testing strategy
│   ├── Deployment.md       # Render cloud deployment guide
│   ├── VERITAS_PLAN.md     # 36-hour hackathon execution plan
│   ├── API_CONTRACT.md     # REST endpoint contract
│   ├── DATA_SCHEMA.md      # Raw and processed data specifications
│   ├── GRAPH_SCHEMA.md     # Neo4j node and relationship schema
│   └── DEMO_FLOW.md        # Hackathon presentation walkthrough script
│
├── scripts/                # Utility & Loader Scripts
│   ├── seed_demo.py        # Generates synthetic judging dataset
│   ├── load_neo4j.py       # Loads demo dataset into Neo4j
│   └── test_pipeline.py    # Pipeline sanity & integrity audit
│
├── render.yaml             # Render cloud deployment blueprint
├── .gitignore
├── LICENSE                 # MIT License
└── README.md
```

---

## 5. Quickstart & Local Setup

### 5.1 Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Git

### 5.2 Step 1: Clone & Seed Demo Data
```bash
# 1. Generate the demo judging dataset (FIRs, CDRs, Transactions, Graph JSON)
python scripts/seed_demo.py

# 2. Run the integrity audit to verify 6/6 tests pass
python scripts/test_pipeline.py
```

### 5.3 Step 2: Start the Backend (FastAPI)
```bash
# Create and activate virtual environment
python -m venv .venv
# On Windows: .venv\Scripts\Activate.ps1
# On Linux/macOS: source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Start FastAPI server
uvicorn backend.app.main:app --reload --port 8000
```
- API Docs (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 5.4 Step 3: Start the Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

---

## 6. Demo Showcase: "Operation Shadow Syndicate"

The included demo dataset models a realistic organized crime network in Delhi NCR:
1. **The Interception**: Police seize 14 kg of contraband from driver **Arjun Verma (P006)** at Singhu Border.
2. **The CDR Clues**: Verma's phone connects to logistics coordinator **Rajesh Kumar (P003)** and an elusive burner phone operated by **Kabir Mirza (P004)**.
3. **The Hawala Trail**: Financial records link front company **Astra Logistics Ltd (ORG001)** to Hawala broker **Tariq Sheikh (P002)**.
4. **The Discovery**: Running **VERITAS Pathfinding** and **Betweenness Centrality** traces the entire multi-hop chain directly to the syndicate mastermind: **Vikramaditya Singhania (P001)**.

$$\text{Arjun Verma [Runner]} \longrightarrow \text{Rajesh [Logistics]} \longrightarrow \text{Kabir [Enforcer]} \longrightarrow \text{Tariq [Broker]} \longrightarrow \mathbf{\text{Vikram Singhania [Mastermind]}}$$

---

## 7. API Reference Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | System liveness and graph backend status |
| `GET` | `/api/v1/graph` | Returns Cytoscape nodes and edges with threshold/type filters |
| `GET` | `/api/v1/graph/ego/{id}` | Returns $N$-hop neighborhood subgraph centered around an entity |
| `GET` | `/api/v1/entities` | Paginated entity search with filters by type and risk score |
| `GET` | `/api/v1/entities/{id}` | Detailed suspect dossier, linked aliases, and direct edges |
| `GET` | `/api/v1/paths/shortest` | Multi-hop shortest path between source and target entities |
| `GET` | `/api/v1/communities` | Detected criminal clusters using Louvain modularity |
| `GET` | `/api/v1/analytics/centrality` | Influencer leaderboards by PageRank, Betweenness, and Degree |

---

## 8. Team Division & Roles

- **Member 1 (AI / NLP / Data)**: Multi-source ingestion parsers, spaCy entity extraction, relationship extraction, entity resolution, and telecom burst anomaly detection.
- **Member 2 (Backend / Graph Intelligence — YOU)**: Graph builder, NetworkX/Neo4j engine, centrality algorithms, pathfinder, FastAPI REST endpoints, and Sentry monitoring.
- **Member 3 (UI / UX Visualization)**: React 18, TailwindCSS dark-mode interface, Cytoscape.js interactive network graph canvas, and evidentiary provenance modals.

---

## 9. License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
