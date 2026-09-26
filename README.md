# VERITAS — AI-Powered Criminal Network Analysis & Intelligence Platform

> **KAYA Hackathon 2026** // Transforming fragmented law enforcement records into an explainable relationship graph to uncover hidden syndicates, financial trails, and criminal networks.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![Cytoscape.js](https://img.shields.io/badge/Cytoscape.js-3.28%2B-orange.svg)](https://js.cytoscape.org/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.x-blue.svg)](https://neo4j.com/)
[![NetworkX](https://img.shields.io/badge/NetworkX-3.2%2B-lightgrey.svg)](https://networkx.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4%2B-38B2AC.svg)](https://tailwindcss.com/)
[![Tests: 130 Passed](https://img.shields.io/badge/Tests-130%20Passed%20(100%25)-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 1. Executive Summary & Problem Statement

Modern criminal operations are increasingly networked, distributed, and multi-layered. Law enforcement agencies capture massive volumes of data across siloed systems:
- **Unstructured text**: Police FIR reports, interrogation summaries, surveillance logs.
- **Telecom records**: Call Detail Records (CDRs), cell tower triangulations, burner phone bursts.
- **Financial channels**: Banking transactions, Hawala ledgers, structured cash deposits.
- **Physical registries**: Vehicle registrations, safehouses, commercial addresses.

**The Core Challenge**: Investigators struggle to uncover hidden multi-hop connections because data is fragmented and manual spreadsheet analysis fails to reveal indirect links. A relationship that appears trivial in isolation becomes critical when combined across sources.

**The VERITAS Solution**: An automated intelligence system that ingests heterogeneous structured and unstructured records, extracts and resolves entities, constructs an explainable multigraph knowledge graph, runs structural network algorithms (Centrality, Louvain Community Detection, Dijkstra Pathfinding), and renders an interactive, professional investigation workspace.

---

## 2. Core Capabilities & Architectural Highlights

- 🔍 **Multi-Source Data Ingestion**: Concurrently parses unstructured police complaints (PDF/TXT) and structured CSV records (CDRs, bank ledgers).
- 🧠 **NLP & Named Entity Recognition (NER)**: Extracts key investigative entities: `Person`, `Phone`, `Vehicle`, `Organization`, `Location`, and `BankAccount`.
- 🔗 **Entity Resolution & Alias Disambiguation**: Uses fuzzy matching (Jaro-Winkler, Levenshtein, Metaphone) to unify multiple aliases and phone formats into singular suspect dossiers.
- 🏛️ **Bureau Landing Deck (`/`)**: Institutional home portal showcasing active operations (`Operation Cerberus`), syndicate telemetry, algorithmic pillars, and specialized crime divisions.
- 📊 **Overview Dashboard (`/dashboard`)**: Minimalist KPI metric cards, stabilized Cytoscape hero network preview, and prioritized evidentiary review signals.
- 🕸️ **Interactive Cytoscape.js Network Explorer (`/network`)**: High-performance canvas featuring force-directed physics, node/edge tap listeners, 72%/28% canvas-to-inspector split, and multi-hop connection tracing.
- 👑 **Structural Influencer Detection**: Computes **PageRank**, **Betweenness Centrality**, and **Degree Centrality** to pinpoint gatekeepers, brokers, and influential coordinators.
- 🧭 **Multi-Hop Path Finder**: Discovers indirect connection paths between any two suspects (e.g., *Street Courier $\to$ Logistics Handler $\to$ Burner Phone $\to$ Hawala Broker $\to$ Syndicate Core*).
- 🏷️ **100% Explainable Provenance**: Every graph edge preserves links to supporting evidence (source document ID, timestamps, confidence scores, and verbatim primary citations).
- 🛡️ **Hybrid Fail-Safe Architecture**: Operates on a high-speed **In-Memory NetworkX Engine** out-of-the-box (with optional Neo4j Aura sync), guaranteeing zero downtime.
- 🏅 **Detective Badges Suite**: Handcrafted SVG forensic insignias and institutional seals (`DetectiveBadge`, `CrimeIntelligenceSeal`, `FinancialCrimesBadge`, `EvidenceVaultSeal`).
- 📜 **Institutional Footer on Every View**: Complete workspace navigation, judicial standards (`NIST SP 800-86`, `FED Rule 902(14)`, `FIPS 140-3`, `CJIS v5.9`), legal disclaimer, and **TeamMETX** accreditation.

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
|   Cytoscape Canvas | Suspect Dossier Panel | Evidence Provenance UI | Recharts|
+-------------------------------------------------------------------------------+
```

---

## 4. Visual Workspace & Platform Showcase

### 🏛️ Bureau Landing Deck (`/`)
The primary entrypoint for intelligence analysts, featuring live operation metrics, algorithmic architecture pillars, and specialized crime enforcement divisions.

![Bureau Landing Deck](docs/images/veritas_home.png)

---

### 📊 Investigation Overview Dashboard (`/dashboard`)
Operational control center featuring real-time KPI metrics, force-directed hero knowledge graph, and prioritized evidentiary review signals.

![Overview Dashboard](docs/images/veritas_dashboard.png)

---

### 📈 Network Topology & Syndicate Analytics (`/analytics`)
Deep structural graph metrics, horizontal centrality leaderboards (PageRank, Betweenness, Degree), and Louvain modularity sub-cell clustering.

![Syndicate Analytics](docs/images/veritas_analytics.png)

---

### 👥 Engineering Squad Accreditation & Institutional Footer
Persistent footer rendering across every dashboard view, highlighting judicial evidentiary compliance standards, legal disclaimers, and **TeamMETX** core engineers.

![TeamMETX Footer](docs/images/veritas_footer_teammetx.png)

---

## 5. Quickstart & Local Setup

### 5.1 Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Git

### 5.2 Step 1: Start the Backend (FastAPI)
```bash
# Create and activate virtual environment
python -m venv .venv
# On Windows: .venv\Scripts\activate
# On Linux/macOS: source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Start FastAPI server
python -m uvicorn backend.app.main:app --reload --port 8000
```
- API Documentation (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)
- System Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 5.3 Step 2: Start the Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

### 5.4 Step 3: Run the Automated Test Suite
```bash
# Run all 130 tests across AI, Backend, and Integration tiers
python -m pytest tests/
```

---

## 6. Cloud Deployment (Render.com)

The project includes a production-ready infrastructure blueprint in [`render.yaml`](render.yaml):

1. Go to [dashboard.render.com](https://dashboard.render.com/) and click **New +** ➔ **Blueprint**.
2. Connect repository **`amanpal3/VERITAS-`** and branch **`main`**.
3. Render automatically provisions:
   - **`veritas-backend`** (Python Web Service running FastAPI on Uvicorn).
   - **`veritas-frontend`** (Static Site with SPA rewrite rules).
4. See [`docs/DEPLOYMENT_GUIDE.md`](docs/DEPLOYMENT_GUIDE.md) for full instructions.

---

## 7. Demo Showcase: "Operation Shadow Syndicate"

The included demo dataset models a realistic organized crime network:
1. **The Interception**: Police seize contraband from driver **Arjun Verma (P006)** at Singhu Border.
2. **The CDR Clues**: Verma's phone connects to logistics coordinator **Rajesh Kumar (P003)** and a burner phone operated by **Kabir Mirza (P004)**.
3. **The Hawala Trail**: Financial records link front company **Astra Logistics Ltd (ORG001)** to Hawala broker **Tariq Sheikh (P002)**.
4. **The Discovery**: Running **VERITAS Pathfinding** and **Betweenness Centrality** traces the entire multi-hop chain directly to the syndicate mastermind: **Vikramaditya Singhania (P001)**.

$$\text{Arjun Verma [Runner]} \longrightarrow \text{Rajesh [Logistics]} \longrightarrow \text{Kabir [Enforcer]} \longrightarrow \text{Tariq [Broker]} \longrightarrow \mathbf{\text{Vikram Singhania [Mastermind]}}$$

---

## 8. Engineering Team — TeamMETX

| # | Name | Core Responsibilities |
| :-: | :--- | :--- |
| **1** | **Aman Pal** | **AI Pipeline & NLP Architecture** — Data ingestion parsers, spaCy Named Entity Recognition, relationship extraction, fuzzy entity resolution, and telecom burst anomaly detection. |
| **2** | **Armaan Dwivedi** | **Backend & Graph Intelligence** — FastAPI REST engine, NetworkX multigraph, Louvain modularity clustering, PageRank/Betweenness ranking, Dijkstra shortest-path discovery, and Sentry monitoring. |
| **3** | **Om Upadhyay** | **UI/UX & Forensic Frontend** — React 18, Cytoscape.js interactive graph workspace, Recharts analytics, Light/Night themes, evidence dossiers, and detective insignia suite. |

---

## 9. License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
