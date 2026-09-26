"""
VERITAS - Multi-Hop Shortest Path Finder
Finds indirect connections between suspects and kingpins across heterogeneous
multi-relational links, compiling step-by-step evidentiary citations.
"""
import logging
from typing import Any, Dict, List, Optional
import networkx as nx

from backend.app.core.exceptions import EntityNotFoundException
from backend.app.models.responses import PathResponse, PathStep

logger = logging.getLogger("veritas.graph.pathfinder")


def find_shortest_path(
    graph: nx.MultiDiGraph,
    source_id: str,
    target_id: str,
) -> PathResponse:
    """
    Computes shortest connecting chain between source and target entities across
    telecom, financial, and organizational links.
    """
    if source_id not in graph.nodes:
        raise EntityNotFoundException(source_id)
    if target_id not in graph.nodes:
        raise EntityNotFoundException(target_id)

    if source_id == target_id:
        return PathResponse(
            source=source_id,
            target=target_id,
            found=True,
            length=0,
            nodes=[source_id],
            edges=[],
            path_details=[],
        )

    # Use undirected projection for multi-hop forensic navigation
    undirected = graph.to_undirected(as_view=False)

    if not nx.has_path(undirected, source_id, target_id):
        return PathResponse(
            source=source_id,
            target=target_id,
            found=False,
            length=0,
            nodes=[],
            edges=[],
            path_details=[],
        )

    try:
        node_path = nx.shortest_path(undirected, source=source_id, target=target_id)
    except nx.NetworkXNoPath:
        return PathResponse(
            source=source_id,
            target=target_id,
            found=False,
            length=0,
            nodes=[],
            edges=[],
            path_details=[],
        )

    edges_collected: List[str] = []
    path_details: List[PathStep] = []

    for idx in range(len(node_path) - 1):
        u = node_path[idx]
        v = node_path[idx + 1]

        # Extract edge details from either direction in original directed multigraph
        edge_data: Dict[str, Any] = {}
        edge_id = f"edge_{u}_{v}"

        if graph.has_edge(u, v):
            keys = list(graph[u][v].keys())
            edge_data = dict(graph[u][v][keys[0]])
            edge_id = edge_data.get("id") or str(keys[0])
        elif graph.has_edge(v, u):
            keys = list(graph[v][u].keys())
            edge_data = dict(graph[v][u][keys[0]])
            edge_id = edge_data.get("id") or str(keys[0])

        edges_collected.append(edge_id)

        # Build descriptive step labels
        u_data = graph.nodes[u]
        v_data = graph.nodes[v]

        u_name = u_data.get("name") or u_data.get("label") or u
        u_role = u_data.get("role")
        from_str = f"{u_name} ({u_role})" if u_role else str(u_name)

        v_name = v_data.get("name") or v_data.get("label") or v
        v_role = v_data.get("role")
        to_str = f"{v_name} ({v_role})" if v_role else str(v_name)

        rel_type = edge_data.get("type", "ASSOCIATED_WITH")
        prov = edge_data.get("provenance", {})
        if isinstance(prov, dict):
            snippet = prov.get("snippet")
        else:
            snippet = getattr(prov, "snippet", None)

        path_details.append(
            PathStep(
                step=idx + 1,
                from_entity=from_str,
                relation=rel_type,
                to_entity=to_str,
                evidence_snippet=snippet,
            )
        )

    return PathResponse(
        source=source_id,
        target=target_id,
        found=True,
        length=len(node_path) - 1,
        nodes=[str(n) for n in node_path],
        edges=edges_collected,
        path_details=path_details,
    )
