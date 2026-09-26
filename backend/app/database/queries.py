"""
VERITAS - Cypher Query Templates
Standardized Cypher queries for Neo4j property graph operations.
"""

CYPHER_GET_ALL_NODES = """
MATCH (n)
RETURN n.id AS id,
       labels(n)[0] AS type,
       n.label AS label,
       n.name AS name,
       n.role AS role,
       n.risk_score AS risk_score,
       n.degree AS degree,
       n.betweenness AS betweenness,
       n.pagerank AS pagerank,
       n.community_id AS community_id,
       n.aliases AS aliases
"""

CYPHER_GET_ALL_EDGES = """
MATCH (a)-[r]->(b)
RETURN r.id AS id,
       a.id AS source,
       b.id AS target,
       type(r) AS type,
       r.weight AS weight,
       r.timestamp AS timestamp,
       r.provenance AS provenance
"""

CYPHER_GET_ENTITY_BY_ID = """
MATCH (n {id: $entity_id})
RETURN n.id AS id,
       labels(n)[0] AS type,
       n.label AS label,
       n.name AS name,
       n.role AS role,
       n.risk_score AS risk_score,
       n.degree AS degree,
       n.betweenness AS betweenness,
       n.pagerank AS pagerank,
       n.community_id AS community_id,
       n.aliases AS aliases
"""

CYPHER_GET_CONNECTIONS = """
MATCH (n {id: $entity_id})-[r]-(m)
RETURN r.id AS relationship_id,
       type(r) AS type,
       m.id AS target_id,
       coalesce(m.name, m.label, m.id) AS target_name,
       labels(m)[0] AS target_type,
       r.provenance AS provenance,
       coalesce(r.weight, 1.0) AS weight,
       r.timestamp AS timestamp
"""

CYPHER_SHORTEST_PATH = """
MATCH (a {id: $source_id}), (b {id: $target_id})
MATCH p = shortestPath((a)-[*]-(b))
RETURN [n in nodes(p) | n.id] AS node_ids,
       [r in relationships(p) | r.id] AS edge_ids,
       length(p) AS length
"""
