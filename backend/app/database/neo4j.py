"""
VERITAS - Neo4j Database Connection Manager
Manages driver lifecycle, connection pooling, and seamless fallback to In-Memory NetworkX.
"""
import logging
from typing import Any, Dict, List, Optional
import networkx as nx

from backend.app.core.config import get_settings

logger = logging.getLogger("veritas.database.neo4j")


class Neo4jDatabase:
    """Manages connection to Neo4j graph database with graceful fallback."""

    def __init__(self):
        self.driver = None
        self.is_connected = False
        self._initialized = False

    def connect(self) -> bool:
        """Attempt connection to Neo4j database."""
        if self.is_connected and self.driver:
            return True

        settings = get_settings()
        try:
            from neo4j import GraphDatabase
            from neo4j.exceptions import ServiceUnavailable, AuthError

            logger.info(f"Attempting Neo4j connection at {settings.NEO4J_URI}...")
            driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                max_connection_lifetime=settings.NEO4J_MAX_CONNECTION_LIFETIME,
                max_connection_pool_size=settings.NEO4J_MAX_CONNECTION_POOL_SIZE,
                connection_timeout=settings.NEO4J_CONNECTION_TIMEOUT,
            )
            # Test connectivity
            with driver.session() as session:
                session.run("RETURN 1 AS ping")

            self.driver = driver
            self.is_connected = True
            logger.info("Successfully connected to Neo4j graph database.")
            return True

        except Exception as e:
            logger.warning(
                f"Neo4j offline or unavailable ({e}). Operating in resilient In-Memory NetworkX mode."
            )
            self.driver = None
            self.is_connected = False
            return False

    def close(self):
        """Close Neo4j driver connection."""
        if self.driver:
            try:
                self.driver.close()
            except Exception as e:
                logger.warning(f"Error closing Neo4j driver: {e}")
            finally:
                self.driver = None
                self.is_connected = False

    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute Cypher query if connected; returns empty list if disconnected."""
        if not self.is_connected or not self.driver:
            return []

        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Error executing Cypher query '{query}': {e}")
            return []

    def sync_from_networkx(self, graph: nx.MultiDiGraph) -> bool:
        """Synchronize in-memory graph into Neo4j database if available."""
        if not self.is_connected or not self.driver:
            return False

        try:
            with self.driver.session() as session:
                # 1. Constraints
                for label in ["Person", "Phone", "Vehicle", "Organization", "Location", "BankAccount"]:
                    try:
                        session.run(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.id IS UNIQUE")
                    except Exception:
                        pass

                # 2. Nodes
                for node_id, data in graph.nodes(data=True):
                    label = data.get("type", "Entity")
                    cypher = f"""
                    MERGE (n:{label} {{id: $id}})
                    SET n.label = $label,
                        n.name = $name,
                        n.role = $role,
                        n.risk_score = $risk_score,
                        n.degree = $degree,
                        n.betweenness = $betweenness,
                        n.pagerank = $pagerank,
                        n.community_id = $community_id,
                        n.aliases = $aliases
                    """
                    session.run(
                        cypher,
                        id=str(node_id),
                        label=data.get("label", str(node_id)),
                        name=data.get("name") or data.get("label") or str(node_id),
                        role=data.get("role"),
                        risk_score=float(data.get("risk_score", 0.0)),
                        degree=int(data.get("degree", 0)),
                        betweenness=float(data.get("betweenness", 0.0)),
                        pagerank=float(data.get("pagerank", 0.0)),
                        community_id=data.get("community_id"),
                        aliases=data.get("aliases", []),
                    )

                # 3. Edges
                import json
                for u, v, key, data in graph.edges(keys=True, data=True):
                    rel_type = data.get("type", "ASSOCIATED_WITH")
                    prov = data.get("provenance", {})
                    if hasattr(prov, "model_dump"):
                        prov_str = json.dumps(prov.model_dump())
                    elif isinstance(prov, dict):
                        prov_str = json.dumps(prov)
                    else:
                        prov_str = str(prov)

                    edge_cypher = f"""
                    MATCH (a {{id: $src}})
                    MATCH (b {{id: $tgt}})
                    MERGE (a)-[rel:{rel_type} {{id: $edge_id}}]->(b)
                    SET rel.weight = $weight,
                        rel.timestamp = $timestamp,
                        rel.provenance = $provenance
                    """
                    session.run(
                        edge_cypher,
                        src=str(u),
                        tgt=str(v),
                        edge_id=data.get("id", str(key)),
                        weight=float(data.get("weight", 1.0)),
                        timestamp=str(data.get("timestamp", "")),
                        provenance=prov_str,
                    )

            logger.info("Successfully synced graph to Neo4j store.")
            return True
        except Exception as e:
            logger.error(f"Failed to sync graph to Neo4j: {e}")
            return False


# Singleton instance
neo4j_db = Neo4jDatabase()
