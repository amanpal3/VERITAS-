# VERITAS — Knowledge Graph Schema & Algorithmic Models

> **Graph Ontology & Network Analytics** // Neo4j property graph model, node labels, relationship semantics, and mathematical algorithm definitions.

---

## 1. Property Graph Model

The VERITAS knowledge graph is modeled as a **labeled, attributed, directed multigraph**:
$$G = (V, E)$$
Where vertices $V$ represent real-world entities and edges $E$ represent observed semantic relationships backed by evidence.

---

## 2. Node Labels & Property Definitions

| Node Label | Key Attributes | Analytical Significance |
| :--- | :--- | :--- |
| **`:Person`** | `id`, `name`, `aliases`, `role`, `risk_score`, `community_id`, `degree`, `betweenness`, `pagerank` | Primary suspect dossiers, coordinators, couriers, and kingpins. |
| **`:Phone`** | `id`, `number`, `provider`, `imsi`, `imei`, `is_burner` | Communication nexus used to establish contact networks and burner clusters. |
| **`:Vehicle`** | `id`, `plate`, `model`, `color`, `registered_owner` | Physical logistics links between suspects, border checkpoints, and safehouses. |
| **`:Location`** | `id`, `name`, `address`, `city`, `coordinates`, `location_type` | Convergence hubs (warehouses, safehouses, Hawala counters). |
| **`:Organization`**| `id`, `name`, `type`, `registration_no`, `jurisdiction` | Corporate shells, logistics firms, front businesses, and crime syndicates. |
| **`:BankAccount`** | `id`, `account_no`, `bank_name`, `account_type` | Financial conduits mapping layering, smurfing, and Hawala transfers. |

---

## 3. Relationship Types & Semantic Rules

```text
(:Person)-[:USES_PHONE {since, is_primary}]->(:Phone)
(:Phone)-[:CALLED {calls_count, total_duration, last_timestamp, cell_tower}]->(:Phone)
(:Person)-[:OWNS]->(:Vehicle)
(:Person)-[:OPERATES]->(:Vehicle)
(:Person)-[:LOCATED_AT {timestamp, frequency}]->(:Location)
(:Person)-[:ASSOCIATED_WITH {confidence, source_id}]->(:Person)
(:Person)-[:SUPERVISES {confidence}]->(:Person)
(:Person)-[:COORDINATES_WITH {confidence}]->(:Person)
(:Person)-[:CONTROLS]->(:Organization)
(:Person)-[:MEMBER_OF {role}]->(:Organization)
(:Person)-[:OWNS_ACCOUNT]->(:BankAccount)
(:Organization)-[:OWNS_ACCOUNT]->(:BankAccount)
(:BankAccount)-[:TRANSACTED_WITH {amount, frequency, last_timestamp, channel}]->(:BankAccount)
```

---

## 4. Graph Analytics & Algorithms

### 4.1 Degree Centrality
- **Mathematical Definition**: $C_D(v) = \frac{\text{deg}(v)}{|V| - 1}$
- **Investigative Utility**: Identifies high-volume operational hubs (e.g. logistics dispatchers, high-frequency callers).

### 4.2 Betweenness Centrality
- **Mathematical Definition**: $C_B(v) = \sum_{s \neq v \neq t} \frac{\sigma_{st}(v)}{\sigma_{st}}$
- **Investigative Utility**: Pinpoints critical gatekeepers and brokers bridging disparate cells (e.g. Tariq Sheikh bridging street logistics with corporate Hawala).

### 4.3 PageRank
- **Mathematical Definition**: $PR(v) = \frac{1-d}{|V|} + d \sum_{u \in M(v)} \frac{PR(u)}{L(u)}$
- **Investigative Utility**: Uncovers structural kingpins who have low raw connection counts but are linked only to highly connected lieutenants.

### 4.4 Community Detection (Louvain Modularity)
- **Mathematical Goal**: Maximize modularity index $Q$:
  $$Q = \frac{1}{2m} \sum_{vw} \left[ A_{vw} - \frac{k_v k_w}{2m} \right] \delta(c_v, c_w)$$
- **Investigative Utility**: Automatically groups the overall graph into colored criminal sub-gangs (e.g. *Logistics Cell*, *Hawala Laundering Cell*, *Tactical Security Cell*).

### 4.5 Shortest Path Traversal
- **Mathematical Method**: Breadth-First Search (BFS) / Dijkstra's shortest path.
- **Investigative Utility**: Traces indirect connections between street runners and syndicate bosses across multi-hop chains, returning all intermediate nodes, edges, and supporting citations.

---

## 5. Algorithmic Interpretation Rule

> [!IMPORTANT]
> **Graph metrics are analytical signals, not legal determinations of guilt.**
> In all UI presentations, scores must be accompanied by explicit definitions and links to source evidence records. High centrality indicates structural importance within the dataset, providing prioritization for investigator review.
