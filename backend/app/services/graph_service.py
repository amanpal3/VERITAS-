"""
VERITAS - Graph Service
Orchestrates graph data hydration, Cytoscape transformations, ego-network filtering,
and system health reporting.
"""
import logging
from typing import Any, Dict, List, Optional, Set
import networkx as nx

from backend.app.core.config import get_settings
from backend.app.core.exceptions import EntityNotFoundException
from backend.app.database.neo4j import neo4j_db
from backend.app.graph.builder import build_networkx_graph_from_demo
from backend.app.graph.centrality import compute_all_centralities
from backend.app.graph.communities import detect_and_assign_communities
from backend.app.graph.metrics import compute_graph_metrics
from backend.app.models.entity import CytoscapeNode, CytoscapeNodeData
from backend.app.models.relationship import CytoscapeEdge, CytoscapeEdgeData, Provenance
from backend.app.models.responses import (
    EgoGraphResponse,
    GraphMetadata,
    GraphResponse,
    HealthResponse,
)

logger = logging.getLogger("veritas.services.graph")


class GraphService:
    """Singleton service maintaining master graph state and query dispatch."""

    def __init__(self):
        self.graph: nx.MultiDiGraph = nx.MultiDiGraph()
        self._is_hydrated: bool = False

    def initialize(self):
        """Load data, calculate algorithms, and attempt Neo4j sync."""
        logger.info("Initializing VERITAS Graph Service...")
        self.graph = build_networkx_graph_from_demo()

        # Compute structural metrics, centralities, and communities
        compute_graph_metrics(self.graph)
        compute_all_centralities(self.graph)
        detect_and_assign_communities(self.graph)

        self._is_hydrated = True

        # Attempt Neo4j connection and sync
        connected = neo4j_db.connect()
        if connected:
            neo4j_db.sync_from_networkx(self.graph)

        logger.info(
            f"GraphService initialized with {self.graph.number_of_nodes()} nodes, "
            f"{self.graph.number_of_edges()} edges. Neo4j connected: {connected}"
        )

    def get_health(self) -> HealthResponse:
        """Return system health status and backend mode."""
        backend_mode = "neo4j" if neo4j_db.is_connected else "in_memory_networkx"
        return HealthResponse(
            status="healthy",
            service="veritas-api",
            version=get_settings().VERSION,
            graph_backend=backend_mode,
            total_nodes=self.graph.number_of_nodes(),
            total_edges=self.graph.number_of_edges(),
        )

    def get_graph_data(
        self,
        entity_type: Optional[str] = None,
        min_risk: float = 0.0,
        min_weight: float = 0.0,
    ) -> GraphResponse:
        """
        Return Cytoscape-formatted graph with optional filtering by entity type,
        minimum risk score, and minimum relationship weight.
        """
        # Filter nodes
        filtered_node_ids: Set[str] = set()
        cytoscape_nodes: List[CytoscapeNode] = []

        for node_id, data in self.graph.nodes(data=True):
            ent_type = data.get("type", "")
            risk_score = float(data.get("risk_score", 0.0))

            if entity_type and ent_type.lower() != entity_type.lower():
                continue
            if risk_score < min_risk:
                continue

            filtered_node_ids.add(str(node_id))
            payload = dict(data)
            payload["id"] = str(node_id)
            if "label" not in payload or not payload["label"]:
                payload["label"] = payload.get("name") or str(node_id)
            cytoscape_nodes.append(CytoscapeNode(data=CytoscapeNodeData(**payload)))

        # Filter edges: both endpoints must be in filtered_node_ids and weight >= min_weight
        cytoscape_edges: List[CytoscapeEdge] = []
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            u_str = str(u)
            v_str = str(v)
            weight = float(data.get("weight", 1.0))

            if u_str in filtered_node_ids and v_str in filtered_node_ids and weight >= min_weight:
                payload = dict(data)
                payload["source"] = u_str
                payload["target"] = v_str
                if "id" not in payload or not payload["id"]:
                    payload["id"] = str(key) if key else f"edge_{u}_{v}"
                cytoscape_edges.append(CytoscapeEdge(data=CytoscapeEdgeData(**payload)))

        communities_detected = len(set(
            self.graph.nodes[n].get("community_id")
            for n in self.graph.nodes
            if self.graph.nodes[n].get("community_id") is not None
        ))

        meta = GraphMetadata(
            total_nodes=len(cytoscape_nodes),
            total_edges=len(cytoscape_edges),
            communities_detected=communities_detected,
            title=self.graph.graph.get("title", "VERITAS Network Graph"),
        )

        return GraphResponse(
            metadata=meta,
            nodes=cytoscape_nodes,
            edges=cytoscape_edges,
        )

    def get_ego_network(self, entity_id: str, hops: int = 1) -> EgoGraphResponse:
        """
        Extract an ego-network neighborhood around an entity up to specified hops (1-2).
        """
        if entity_id not in self.graph:
            raise EntityNotFoundException(entity_id)

        hops = max(1, min(2, hops))
        undirected_g = self.graph.to_undirected(as_view=False)
        ego_subgraph = nx.ego_graph(undirected_g, entity_id, radius=hops)

        ego_node_ids = set(ego_subgraph.nodes())

        nodes: List[CytoscapeNode] = []
        for nid in ego_node_ids:
            nd = dict(self.graph.nodes[nid])
            nd["id"] = str(nid)
            if "label" not in nd or not nd["label"]:
                nd["label"] = nd.get("name") or str(nid)
            nodes.append(CytoscapeNode(data=CytoscapeNodeData(**nd)))

        edges: List[CytoscapeEdge] = []
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            if str(u) in ego_node_ids and str(v) in ego_node_ids:
                payload = dict(data)
                payload["source"] = str(u)
                payload["target"] = str(v)
                if "id" not in payload or not payload["id"]:
                    payload["id"] = str(key) if key else f"edge_{u}_{v}"
                edges.append(CytoscapeEdge(data=CytoscapeEdgeData(**payload)))

        return EgoGraphResponse(nodes=nodes, edges=edges)


# Global singleton instance
graph_service = GraphService()
