# VERITAS — Member 2 Backend & Graph Service Guide

> **Author**: Member 2 (Backend, Graph Algorithms, FastAPI, Neo4j)  
> **Status**: Verified & Passing (25/25 Backend Tests Passing, 130/130 Total Project Tests Passing)  
> **Base URL**: `/api/v1`

---

## 1. Architecture Overview

Member 2 delivers the core intelligence serving layer connecting Member 1's extracted intelligence to Member 3's interactive React/Cytoscape dashboard:

```
┌─────────────────────────────────┐
│ Member 1 AI Pipeline / Demo Data│
└────────────────┬────────────────┘
                 │ (entities.json & relationships.json)
                 ▼
┌─────────────────────────────────┐
│     GraphService (Singleton)    │
│  - NetworkX MultiDiGraph        │
│  - Degree, Betweenness, PageRank│
│  - Louvain Community Detection  │
│  - Multi-hop Shortest Path      │
└────────┬───────────────┬────────┘
         │               │
         ▼               ▼
┌────────────────┐ ┌──────────────┐
│ Neo4j Database │ │ FastAPI REST │
│ (Auto-Fallback)│ │ + Sentry SDK │
└────────────────┘ └──────────────┘
```

---

## 2. API Endpoints Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/v1/health` | `GET` | System health check reporting node/edge counts and active backend mode (`neo4j` or `in_memory_networkx`). |
| `/api/v1/graph` | `GET` | Cytoscape.js formatted knowledge graph with `entity_type`, `min_risk`, and `min_weight` filtering. |
| `/api/v1/graph/ego/{entity_id}` | `GET` | 1-to-2 hop neighborhood graph centered on a suspect. |
| `/api/v1/entities` | `GET` | Search and paginated directory across suspect names, aliases, and roles. |
| `/api/v1/entities/{entity_id}` | `GET` | Suspect dossier including centrality scores and direct connections with provenance. |
| `/api/v1/entities/{entity_id}/connections` | `GET` | Scoped Cytoscape graph of immediate neighbors. |
| `/api/v1/paths/shortest` | `GET` | Multi-hop connecting path between two entities with step-by-step forensic evidence citations. |
| `/api/v1/analytics/centrality` | `GET` | Priority rankings by `degree`, `betweenness`, or `pagerank`. |
| `/api/v1/communities` | `GET` | Detected criminal sub-cells grouped by Louvain Modularity with tactical labels. |

---

## 3. Starting the Server

```bash
# Start FastAPI with Uvicorn
python -m uvicorn backend.app.main:app --reload --port 8000
```

Interactive OpenAPI documentation is accessible at:
* Swagger UI: `http://localhost:8000/docs`
* ReDoc: `http://localhost:8000/redoc`

---

## 4. Error Handling & Sentry Monitoring

* Standardized error shape:
  ```json
  {
    "error": {
      "code": "ENTITY_NOT_FOUND",
      "message": "Requested entity with ID 'P999' does not exist."
    }
  }
  ```
* Sentry is initialized using `SENTRY_DSN` from `.env`. If unset, it gracefully logs locally without failing.
