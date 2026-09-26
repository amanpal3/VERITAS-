# PLAN — Member 2 Implementation Waves

## Wave 1: Core Configuration, Schemas & Models
- `backend/app/core/config.py`: Pydantic settings loading `.env` (`NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `SENTRY_DSN`, `CORS_ORIGINS`, `API_V1_STR`, `ENVIRONMENT`).
- `backend/app/core/exceptions.py`: Standardized API exceptions with `{ "error": { "code": str, "message": str } }` format.
- `backend/app/models/entity.py`: Pydantic models for Entities and Node data matching Member 1 and Cytoscape formats.
- `backend/app/models/relationship.py`: Pydantic models for Relationships, Provenance, and Edge data.
- `backend/app/models/responses.py`: Pydantic response models for all API endpoints (`HealthResponse`, `GraphResponse`, `EntityListResponse`, `EntityDetailResponse`, `PathResponse`, `CentralityResponse`, `CommunityResponse`).

## Wave 2: Graph Engine & Algorithmic Analysis (NetworkX)
- `backend/app/graph/builder.py`: MultiDiGraph / DiGraph construction from demo JSON or Member 1 PipelineResult.
- `backend/app/graph/metrics.py`: Graph-level and node-level basic degree and density calculations.
- `backend/app/graph/centrality.py`: Degree, Betweenness, and PageRank computation with score normalization.
- `backend/app/graph/communities.py`: Louvain community detection with human-friendly tactical cell labeling.
- `backend/app/graph/pathfinder.py`: Breadth-First / Dijkstra shortest path calculation with multi-hop narrative explanations and evidence provenance attribution.

## Wave 3: Database & Persistence Layer (Neo4j with NetworkX Fallback)
- `backend/app/database/neo4j.py`: Neo4j driver connection lifecycle, ping check, and graceful fallback to in-memory mode.
- `backend/app/database/queries.py`: Cypher queries for node retrieval, edge retrieval, shortest path, and ego graphs in Neo4j.

## Wave 4: Business Services & API Routers
- `backend/app/services/graph_service.py`: Orchestrates graph querying, filtering, Cytoscape transformation, and ego-graph generation.
- `backend/app/services/entity_service.py`: Entity search, filtering, and dossier compilation.
- `backend/app/services/analytics_service.py`: Centrality rankings and community distribution.
- `backend/app/api/health.py`: Health check reporting backend status (`neo4j` vs `in_memory_networkx`), total nodes, total edges.
- `backend/app/api/graph.py`: Graph visualization and ego network routes.
- `backend/app/api/entities.py`: Entity search and entity dossier routes.
- `backend/app/api/paths.py`: Shortest pathfinder routes.
- `backend/app/api/communities.py`: Community detection routes.
- `backend/app/api/analytics.py`: Centrality rankings routes.
- `backend/app/main.py`: Main FastAPI app wiring CORS, Sentry error monitoring, startup graph pre-loading, and routers.

## Wave 5: Comprehensive Backend Test Suite & Verification
- `tests/backend/test_health.py`: Health endpoint verification.
- `tests/backend/test_graph.py`: Graph & ego network endpoints.
- `tests/backend/test_entities.py`: Entities directory & dossier endpoints.
- `tests/backend/test_paths.py`: Pathfinding algorithm & provenance verification.
- `tests/backend/test_analytics.py`: Centrality & communities endpoints.
- `tests/backend/test_sentry_resilience.py`: Verify graceful error capturing without crashing.
- Execute full test suite with `python -m pytest tests/backend/` and record empirical evidence.
