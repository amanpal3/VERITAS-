# API Contract - VERITAS

## Base URL
`/api/v1`

## Endpoints
- `GET /health`: Health status check
- `GET /graph`: Return network nodes and edges with optional filters (threshold, date range, entity types)
- `GET /graph/ego/{entity_id}`: Subgraph centered around a specific entity up to N hops
- `GET /entities`: Paginated list of entities with search and filtering
- `GET /entities/{id}`: Detailed entity dossier and direct connections
- `GET /paths/shortest`: Shortest path between two entities
- `GET /communities`: Detected clusters / gang communities with membership
- `GET /analytics/centrality`: Top ranked influencers by PageRank, Degree, and Betweenness
- `GET /analytics/anomalies`: Flagged suspicious transactions and rapid communication bursts
