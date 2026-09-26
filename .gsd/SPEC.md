# SPEC — Member 2: Backend & Graph Analytics Service

## 1. Objective
Implement the complete, production-grade Member 2 Backend for Project VERITAS: a FastAPI application with dual-mode graph database capabilities (Neo4j with automatic in-memory NetworkX fallback), high-performance graph algorithms (Centrality, Louvain Community Detection, Multi-Hop Shortest Path finding with evidence provenance), Sentry exception monitoring, and 100% compliance with `docs/API_CONTRACT.md`.

## 2. Dependencies & Runtime Environment
- Python 3.14+
- FastAPI, Uvicorn, Pydantic v2, Pydantic-Settings
- NetworkX 3.7+ (Graph algorithms & in-memory graph engine)
- Neo4j Python Driver 6.3+ (Bolt connection & Cypher queries with graceful offline fallback)
- Sentry SDK (Configured via `SENTRY_DSN` with graceful degradation)
- Pytest & HTTPX (Test suite)

## 3. Data Sources & Ingestion
- Ingests from `data/demo/` (`graph.json`, `entities.json`, `relationships.json`) or directly from Member 1's `ai.pipeline.IntelligencePipeline` output.
- Normalizes nodes and directed multigraph edges conforming to `docs/GRAPH_SCHEMA.md` and `docs/MEMBER1_BACKEND_HANDOFF.md`.

## 4. Endpoints & API Contract Compliance
- `GET /api/v1/health`
- `GET /api/v1/graph` (Supports `entity_type`, `min_risk`, `min_weight`, formatted for Cytoscape.js)
- `GET /api/v1/graph/ego/{entity_id}` & `GET /api/v1/entities/{entity_id}/connections` (Supports `depth`/`hops`)
- `GET /api/v1/entities` (Supports search `q`, `type`, pagination `limit`, `offset`)
- `GET /api/v1/entities/{entity_id}` (Returns suspect dossier with metrics and connections)
- `GET /api/v1/paths/shortest` & `GET /api/v1/path` (Multi-hop path with step-by-step evidence citations)
- `GET /api/v1/analytics/centrality` (Supports `degree`, `betweenness`, `pagerank` rankings)
- `GET /api/v1/analytics/communities` & `GET /api/v1/communities` (Louvain community detection groupings)

## 5. Non-Functional Requirements
- **Resilience**: Operates in full headless/in-memory mode if Neo4j is offline, so the demo and frontend work immediately without requiring a running Docker Neo4j instance.
- **Observability**: Sentry error tracking integrated via environment variables with try/catch exception capturing in critical paths.
- **Auditability**: Golden Principle — all graph metrics and paths cite source evidence records and provenance snippets.
- **Testing**: 100% endpoint test coverage with Pytest.
