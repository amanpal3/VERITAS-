"""
VERITAS - Community Detection Algorithms
Detects criminal sub-cells using Louvain Modularity and assigns descriptive cell labels.
"""
import logging
from collections import defaultdict
from typing import Any, Dict, List
import networkx as nx

from backend.app.models.responses import CommunityItem

logger = logging.getLogger("veritas.graph.communities")

CELL_LABEL_MAP = {
    1: "Logistics & Smuggling Cell",
    2: "Financial & Hawala Laundering Cell",
    3: "Enforcement & Tactical Security Cell",
}


def label_community(community_id: int, members: List[str], graph: nx.MultiDiGraph) -> str:
    """
    Derives an analytical cell label based on the operational roles of member entities.
    """
    if community_id in CELL_LABEL_MAP:
        return CELL_LABEL_MAP[community_id]

    roles = [str(graph.nodes[m].get("role", "")).lower() for m in members if m in graph.nodes]
    roles_str = " ".join(roles)

    if "hawala" in roles_str or "financial" in roles_str or "broker" in roles_str:
        return "Financial & Hawala Laundering Cell"
    elif "courier" in roles_str or "transport" in roles_str or "logistics" in roles_str or "smuggling" in roles_str:
        return "Logistics & Smuggling Cell"
    elif "enforcer" in roles_str or "security" in roles_str or "arms" in roles_str:
        return "Enforcement & Tactical Security Cell"

    return f"Tactical Syndicate Cell {community_id}"


def detect_and_assign_communities(graph: nx.MultiDiGraph) -> List[CommunityItem]:
    """
    Runs Louvain Modularity community detection on an undirected projection of the graph,
    assigns community_id to all nodes, and returns the aggregated cell clusters.
    """
    if graph.number_of_nodes() == 0:
        return []

    # Check if pre-seeded community_id exists on nodes
    has_preseeded = any(graph.nodes[n].get("community_id") is not None for n in graph.nodes)

    clusters: Dict[int, List[str]] = defaultdict(list)

    if has_preseeded:
        # Group by pre-seeded ID
        for n in graph.nodes:
            cid = graph.nodes[n].get("community_id", 1)
            clusters[cid].append(str(n))
    else:
        # Compute using Louvain
        undirected_g = graph.to_undirected()
        try:
            partition_sets = nx.community.louvain_communities(undirected_g, seed=42)
            for idx, member_set in enumerate(partition_sets, start=1):
                for node_id in member_set:
                    graph.nodes[node_id]["community_id"] = idx
                    clusters[idx].append(str(node_id))
        except Exception as e:
            logger.warning(f"Error calculating Louvain modularity: {e}")
            for idx, node_id in enumerate(graph.nodes, start=1):
                graph.nodes[node_id]["community_id"] = 1
                clusters[1].append(str(node_id))

    # Build response list
    community_items: List[CommunityItem] = []
    for cid in sorted(clusters.keys()):
        member_list = sorted(clusters[cid])
        label = label_community(cid, member_list, graph)
        community_items.append(
            CommunityItem(
                community_id=cid,
                label=label,
                size=len(member_list),
                members=member_list,
            )
        )

    return community_items
