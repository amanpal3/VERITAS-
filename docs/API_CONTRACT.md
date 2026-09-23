# VERITAS — REST API Contract

> **Specification Version**: 1.0.0 // **Base URL**: `/api/v1`
> Frozen API contract connecting Backend services to React/Cytoscape frontend components.

---

## 1. Global Specifications

### Standard Success Response
All endpoints return standard HTTP `200 OK` (or `201 Created`) with JSON payloads.

### Standard Error Shape
```json
{
  "error": {
    "code": "ENTITY_NOT_FOUND",
    "message": "Requested entity with ID 'P999' does not exist."
  }
}
```

---

## 2. Endpoints Reference

### 2.1 System Health
`GET /api/v1/health`
- **Description**: Liveness and readiness check. Confirms whether backend is operating in **Neo4j** or **In-Memory NetworkX** mode.
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "service": "veritas-api",
  "version": "1.0.0",
  "graph_backend": "in_memory_networkx",
  "total_nodes": 29,
  "total_edges": 33
}
```

---

### 2.2 Global Network Graph
`GET /api/v1/graph`
- **Query Parameters**:
  - `entity_type` *(optional)*: Filter by type (`Person`, `Phone`, `Vehicle`, `Organization`, `Location`, `BankAccount`).
  - `min_risk` *(optional, default: 0)*: Minimum risk score filter $[0-100]$.
  - `min_weight` *(optional, default: 0.0)*: Minimum relationship weight.
- **Description**: Returns all nodes and edges formatted specifically for Cytoscape.js canvas rendering.
- **Response `200 OK`**:
```json
{
  "metadata": {
    "total_nodes": 29,
    "total_edges": 33,
    "communities_detected": 3
  },
  "nodes": [
    {
      "data": {
        "id": "P001",
        "label": "Vikramaditya Singhania",
        "type": "Person",
        "role": "Syndicate Mastermind",
        "risk_score": 96,
        "aliases": ["Vikram", "The Don"],
        "degree": 9,
        "betweenness": 0.48,
        "pagerank": 0.165,
        "community_id": 1
      }
    }
  ],
  "edges": [
    {
      "data": {
        "id": "R001",
        "source": "P001",
        "target": "PH001",
        "type": "USES_PHONE",
        "weight": 1.0,
        "timestamp": "2026-03-01T00:00:00Z",
        "provenance": {
          "source_id": "INT-DEL-2026-409",
          "source_type": "SURVEILLANCE",
          "snippet": "Phone registered to Vasant Vihar residence.",
          "confidence": 0.95
        }
      }
    }
  ]
}
```

---

### 2.3 Entity Search & Directory
`GET /api/v1/entities`
- **Query Parameters**:
  - `q` *(optional)*: Text search query across name and aliases.
  - `type` *(optional)*: Filter by entity type.
  - `limit` *(optional, default: 50)*: Page size limit.
- **Response `200 OK`**:
```json
{
  "total": 29,
  "entities": [
    {
      "id": "P001",
      "name": "Vikramaditya Singhania",
      "type": "Person",
      "role": "Syndicate Mastermind",
      "risk_score": 96,
      "aliases": ["Vikram", "The Don"],
      "community_id": 1
    }
  ]
}
```

---

### 2.4 Entity Dossier Details
`GET /api/v1/entities/{entity_id}`
- **Description**: Returns detailed suspect dossier, direct connections, centrality metrics, and source citations.
- **Response `200 OK`**:
```json
{
  "entity": {
    "id": "P001",
    "name": "Vikramaditya Singhania",
    "type": "Person",
    "role": "Syndicate Mastermind",
    "risk_score": 96,
    "aliases": ["Vikram", "The Don"],
    "metrics": {
      "degree": 9,
      "betweenness": 0.48,
      "pagerank": 0.165,
      "community_id": 1
    },
    "connections": [
      {
        "relationship_id": "R001",
        "type": "USES_PHONE",
        "target_id": "PH001",
        "target_name": "+919811010001",
        "target_type": "Phone",
        "provenance": {
          "source_id": "INT-DEL-2026-409",
          "source_type": "SURVEILLANCE",
          "snippet": "Phone registered to Vasant Vihar residence.",
          "confidence": 0.95
        }
      }
    ]
  }
}
```

---

### 2.5 Ego-Network Neighborhood
`GET /api/v1/entities/{entity_id}/connections?depth=1`
*(Also accessible via `GET /api/v1/graph/ego/{entity_id}?hops=1`)*
- **Query Parameters**:
  - `depth` / `hops` *(optional, default: 1, max: 2)*: Traversal depth for neighborhood expansion.
- **Response `200 OK`**: Returns a scoped Cytoscape graph `{ "nodes": [...], "edges": [...] }` centered on `entity_id`.

---

### 2.6 Multi-Hop Connection / Path Finder
`GET /api/v1/paths/shortest?source={source_id}&target={target_id}`
*(Also accessible via `GET /api/v1/path?source={source_id}&target={target_id}`)*
- **Query Parameters**:
  - `source`: Source entity ID (e.g. `P006`, Arjun Verma).
  - `target`: Target entity ID (e.g. `P001`, Vikramaditya Singhania).
- **Description**: Computes the shortest connecting path and returns the complete chain of nodes and edges for visual canvas highlighting.
- **Response `200 OK`**:
```json
{
  "source": "P006",
  "target": "P001",
  "found": true,
  "length": 5,
  "nodes": ["P006", "P003", "P004", "PH004", "PH001", "P001"],
  "edges": ["R028", "R030", "R004", "R009", "R001"],
  "path_details": [
    {
      "step": 1,
      "from": "Arjun Verma (Transport Courier)",
      "relation": "SUPERVISES",
      "to": "Rajesh Kumar (Logistics Coordinator)",
      "evidence_snippet": "Verma confirmed Rajesh Kumar as immediate handler."
    },
    {
      "step": 2,
      "from": "Rajesh Kumar (Logistics Coordinator)",
      "relation": "COORDINATES_WITH",
      "to": "Kabir Mirza (Enforcer & Security)",
      "evidence_snippet": "Frequent coordination over encrypted phone lines."
    },
    {
      "step": 3,
      "from": "Kabir Mirza (Enforcer & Security)",
      "relation": "USES_PHONE",
      "to": "PH004 (Burner Device Cluster)",
      "evidence_snippet": "Signals intelligence linked burner cluster to Kabir Mirza."
    },
    {
      "step": 4,
      "from": "PH004 (Burner Device Cluster)",
      "relation": "CALLED",
      "to": "PH001 (Encrypted Terminal)",
      "evidence_snippet": "2 late night encrypted calls with burner device."
    },
    {
      "step": 5,
      "from": "PH001 (Encrypted Terminal)",
      "relation": "USES_PHONE",
      "to": "Vikramaditya Singhania (Syndicate Mastermind)",
      "evidence_snippet": "Phone registered to Vasant Vihar residence."
    }
  ]
}
```

---

### 2.7 Graph Centrality Analytics
`GET /api/v1/analytics/centrality?metric=betweenness&limit=20`
- **Query Parameters**:
  - `metric`: Centrality algorithm (`degree`, `betweenness`, `pagerank`).
  - `limit`: Number of top entities to return (default: 10).
- **Response `200 OK`**:
```json
{
  "metric": "betweenness",
  "rankings": [
    { "id": "P002", "name": "Tariq Sheikh", "type": "Person", "role": "Hawala Broker", "score": 0.62 },
    { "id": "P001", "name": "Vikramaditya Singhania", "type": "Person", "role": "Syndicate Mastermind", "score": 0.48 },
    { "id": "P003", "name": "Rajesh Kumar", "type": "Person", "role": "Logistics Coordinator", "score": 0.44 }
  ]
}
```

---

### 2.8 Community Detection
`GET /api/v1/analytics/communities`
*(Also accessible via `GET /api/v1/communities`)*
- **Response `200 OK`**:
```json
{
  "total_communities": 3,
  "communities": [
    {
      "community_id": 1,
      "label": "Logistics & Smuggling Cell",
      "size": 12,
      "members": ["P001", "P003", "P006", "P007", "P008", "V001", "V002", "V004", "LOC001", "LOC003", "BA001", "PH001"]
    },
    {
      "community_id": 2,
      "label": "Financial & Hawala Laundering Cell",
      "size": 11,
      "members": ["P002", "P005", "P010", "ORG001", "ORG002", "ORG003", "BA002", "BA003", "LOC002", "PH002", "PH005"]
    },
    {
      "community_id": 3,
      "label": "Enforcement & Tactical Security Cell",
      "size": 6,
      "members": ["P004", "P009", "PH004", "V003"]
    }
  ]
}
```
