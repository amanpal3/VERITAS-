# VERITAS — Engineering Blueprint & System Architecture

> **Technical Specification** // Component decomposition, subsystem interfaces, repository layout, and technology stack.

---

## 1. System Overview & Architectural Vision

VERITAS is an enterprise-grade criminal network intelligence platform designed to ingest multi-source forensic data (police FIRs, Call Detail Records, financial transactions, and surveillance reports), extract entities and semantic relationships, construct an explainable knowledge graph, and perform advanced graph analytics to empower law enforcement investigators.

```text
+-------------------------------------------------------------------------------+
|                                DATA INGESTION                                 |
|  FIR Documents (PDF/TXT) | Telecom CDRs (CSV) | Banking / Financial Logs (CSV) |
+-------------------------------------------------------------------------------+
                                        │
                                        ▼
+-------------------------------------------------------------------------------+
|                          AI / NLP PIPELINE (`ai/`)                             |
|  ┌───────────────────┐   ┌────────────────────┐   ┌───────────────────────┐   |
|  │ Document Parsers  │──►│ NER & Extraction   │──►│ Entity Resolution     │   |
|  │ & Preprocessing   │   │ (spaCy/Regex/Rules)│   │ (Fuzzy/Phone Normal.) │   |
|  └───────────────────┘   └────────────────────┘   └───────────────────────┘   |
+-------------------------------------------------------------------------------+
                                        │
                                        ▼
+-------------------------------------------------------------------------------+
|                       GRAPH STORAGE & PERSISTENCE                             |
|   Primary: Neo4j Graph Database (AuraDB / Local Bolt)                         |
|   Fail-Safe: In-Memory NetworkX Graph Cache & Demo Fixtures                   |
+-------------------------------------------------------------------------------+
                                        │
                                        ▼
+-------------------------------------------------------------------------------+
|                      BACKEND GRAPH INTELLIGENCE (`backend/`)                  |
|  ┌──────────────────────┐  ┌─────────────────────┐  ┌──────────────────────┐  |
|  │ Centrality Engine    │  │ Community Detection │  │ Multi-Hop Pathfinder │  |
|  │ (PageRank/Degree/Bet)│  │ (Louvain Partition) │  │ (Dijkstra / BFS)     │  |
|  └──────────────────────┘  └─────────────────────┘  └──────────────────────┘  |
|  ┌─────────────────────────────────────────────────────────────────────────┐  |
|  │ FastAPI REST Interface (/api/v1/graph, /entities, /paths, /analytics)   │  |
|  │ Sentry Monitoring & Robust Error Boundary Handlers                      │  |
|  └─────────────────────────────────────────────────────────────────────────┘  |
+-------------------------------------------------------------------------------+
                                        │
                                        ▼
+-------------------------------------------------------------------------------+
|                       INVESTIGATOR DASHBOARD (`frontend/`)                    |
|  ┌───────────────────┐  ┌────────────────────┐  ┌──────────────────────────┐  |
|  │ Cytoscape.js      │  │ Suspect Dossier    │  │ Evidence / Provenance    │  |
|  │ Interactive Graph │  │ Details Panel      │  │ Drawer (Source Records)  │  |
|  └───────────────────┘  └────────────────────┘  └──────────────────────────┘  |
|  ┌─────────────────────────────────────────────────────────────────────────┐  |
|  │ Analytics Charts (Recharts) | Global Search & Entity/Edge Type Filters  │  |
|  └─────────────────────────────────────────────────────────────────────────┘  |
+-------------------------------------------------------------------------------+
```

---

## 2. Complete Repository Blueprint

```text
VERITAS/
├── frontend/                          # Member 3 — UI/UX
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/                # App navbar, header, shell
│   │   │   ├── common/                # Buttons, loaders, badges
│   │   │   ├── filters/               # Type and threshold sliders
│   │   │   └── evidence/              # Evidence drawer and citations modal
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx          # High-level metrics and alerts
│   │   │   ├── NetworkAnalysis.jsx    # Cytoscape graph canvas
│   │   │   ├── EntityDetails.jsx      # Dossier overview
│   │   │   └── Analytics.jsx          # Centrality and community charts
│   │   ├── graph/
│   │   │   ├── NetworkGraph.jsx       # Cytoscape.js component
│   │   │   ├── graphStyles.js         # Node/edge styling rules
│   │   │   └── graphUtils.js          # Cytoscape element transformers
│   │   ├── charts/
│   │   │   ├── CentralityChart.jsx    # Bar chart for PageRank/Betweenness
│   │   │   └── CommunityChart.jsx     # Modularity cluster breakdown
│   │   ├── api/
│   │   │   ├── client.js              # Axios instance
│   │   │   ├── graphApi.js            # Graph endpoints
│   │   │   ├── entityApi.js           # Dossier endpoints
│   │   │   └── analyticsApi.js        # Analytics endpoints
│   │   ├── hooks/
│   │   ├── utils/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── public/
│   ├── .env.example
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
│
├── backend/                           # Member 2 — YOU
│   ├── app/
│   │   ├── api/
│   │   │   ├── graph.py               # /graph & /graph/ego
│   │   │   ├── entities.py            # /entities & /entities/{id}
│   │   │   ├── paths.py               # /paths/shortest
│   │   │   ├── communities.py         # /communities
│   │   │   ├── analytics.py           # /analytics/centrality
│   │   │   └── health.py              # /health
│   │   ├── graph/
│   │   │   ├── builder.py             # NetworkX graph constructor
│   │   │   ├── centrality.py          # Degree, Betweenness, PageRank
│   │   │   ├── communities.py         # Louvain modularity algorithm
│   │   │   ├── pathfinder.py          # Dijkstra shortest paths
│   │   │   └── metrics.py             # Density, diameter, cluster metrics
│   │   ├── database/
│   │   │   ├── neo4j.py               # Neo4j driver & connection pool
│   │   │   └── queries.py             # Cypher query catalog
│   │   ├── services/
│   │   │   ├── graph_service.py       # Graph aggregation logic
│   │   │   ├── entity_service.py      # Dossier retrieval logic
│   │   │   └── analytics_service.py   # Analytics coordination
│   │   ├── models/
│   │   │   ├── entity.py              # Pydantic entity schema
│   │   │   ├── relationship.py        # Pydantic edge schema
│   │   │   └── responses.py           # Cytoscape API response models
│   │   ├── core/
│   │   │   ├── config.py              # Environment configuration
│   │   │   └── exceptions.py          # Custom exception handlers
│   │   └── main.py                    # FastAPI entrypoint & Sentry
│   ├── requirements.txt
│   └── .env.example
│
├── ai/                                # Member 1 — AI/NLP/Data
│   ├── ingestion/
│   │   ├── csv_parser.py              # CDR and banking CSV parser
│   │   ├── document_parser.py         # FIR and surveillance report parser
│   │   └── preprocessing.py           # Text cleaning and phone normalization
│   ├── extraction/
│   │   ├── ner.py                     # spaCy entity extractor
│   │   ├── relation_extractor.py      # Semantic relationship mapper
│   │   └── normalizer.py              # Casing and identifier standardizer
│   ├── resolution/
│   │   ├── entity_resolver.py         # Deduplication & alias resolution
│   │   └── similarity.py              # Fuzzy matching algorithms
│   ├── anomaly/
│   │   └── detector.py                # Burst call & smurfing detector
│   ├── schemas/
│   │   ├── entity.py                  # Internal entity models
│   │   └── relationship.py            # Internal edge models
│   └── pipeline.py                    # Master ingestion pipeline runner
│
├── data/
│   ├── raw/                           # Original demo datasets
│   ├── processed/                     # Cleaned datasets
│   ├── output/                        # AI-generated entities/relations
│   └── demo/                          # Stable judging dataset
│
├── tests/
│   ├── ai/
│   ├── backend/
│   └── integration/
│
├── scripts/
│   ├── seed_demo.py                   # Generates synthetic judging dataset
│   ├── load_neo4j.py                  # Loads demo records into Neo4j
│   └── test_pipeline.py               # Pipeline integrity audit
│
├── docs/                              # Technical Documentation
├── render.yaml                        # Render cloud deployment blueprint
├── .gitignore
├── LICENSE                            # MIT License
└── README.md
```

---

## 3. Technology Stack Reference

- **Frontend**: React 18, Vite, Tailwind CSS, Cytoscape.js (`cytoscape-fcose`, `cytoscape-cola`), Recharts, Lucide Icons, Axios.
- **Backend**: Python 3.10+, FastAPI, Pydantic v2, Uvicorn, Sentry-SDK.
- **Graph Engines**: NetworkX (in-memory fast cache & fallback), Neo4j 5.x (property graph store), Cypher.
- **AI & NLP**: pandas, NumPy, spaCy (`en_core_web_sm`), regex/rules, scikit-learn.
- **Testing**: pytest, pytest-cov, httpx.
- **Cloud Deployment**: Render Web Services & Static Sites, Git / GitHub.
