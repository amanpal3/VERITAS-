"""
VERITAS - Graph Centrality Algorithms
Computes Degree, Betweenness, and PageRank metrics using NetworkX algorithms,
normalizes scores, and provides ranked entity listings for investigator prioritization.
"""
import logging
from typing import Any, Dict, List
import networkx as nx

from backend.app.core.exceptions import InvalidAlgorithmMetricException
from backend.app.models.responses import CentralityRankingItem

logger = logging.getLogger("veritas.graph.centrality")

SUPPORTED_METRICS = ["degree", "betweenness", "pagerank"]


def compute_all_centralities(graph: nx.MultiDiGraph) -> Dict[str, Dict[str, float]]:
    """
    Computes degree, betweenness, and PageRank on the graph,
    updating node attributes with calculated values.
    """
    if graph.number_of_nodes() == 0:
        return {"degree": {}, "betweenness": {}, "pagerank": {}}

    # Create simple DiGraph collapsing parallel edges for algorithmic stability
    simple_di = nx.DiGraph()
    for n, data in graph.nodes(data=True):
        simple_di.add_node(n, **data)
    for u, v, data in graph.edges(data=True):
        weight = float(data.get("weight", 1.0))
        if simple_di.has_edge(u, v):
            simple_di[u][v]["weight"] = simple_di[u][v].get("weight", 1.0) + weight
        else:
            simple_di.add_edge(u, v, weight=weight)

    # Degree Centrality (total in+out)
    simple_undirected = simple_di.to_undirected()
    raw_degree = nx.degree_centrality(simple_undirected)

    # Betweenness Centrality
    try:
        raw_betweenness = nx.betweenness_centrality(simple_undirected, normalized=True)
    except Exception as e:
        logger.warning(f"Error computing betweenness: {e}")
        raw_betweenness = {n: 0.0 for n in graph.nodes()}

    # PageRank
    try:
        raw_pagerank = nx.pagerank(simple_di, alpha=0.85, max_iter=200)
    except Exception as e:
        logger.warning(f"Error computing PageRank: {e}")
        raw_pagerank = {n: 1.0 / max(1, graph.number_of_nodes()) for n in graph.nodes()}

    # Decorate nodes on original multigraph (preserve existing pre-seeded values if present)
    for n in graph.nodes():
        node_dict = graph.nodes[n]
        # Degree
        if "degree" not in node_dict or node_dict["degree"] == 0:
            node_dict["degree"] = graph.degree(n)

        # Betweenness
        if "betweenness" not in node_dict or node_dict["betweenness"] == 0.0:
            node_dict["betweenness"] = round(float(raw_betweenness.get(n, 0.0)), 4)

        # PageRank
        if "pagerank" not in node_dict or node_dict["pagerank"] == 0.0:
            node_dict["pagerank"] = round(float(raw_pagerank.get(n, 0.0)), 4)

    return {
        "degree": raw_degree,
        "betweenness": raw_betweenness,
        "pagerank": raw_pagerank,
    }


def get_centrality_rankings(
    graph: nx.MultiDiGraph,
    metric: str,
    limit: int = 10,
) -> List[CentralityRankingItem]:
    """
    Returns top entities ranked by the requested centrality metric.
    """
    normalized_metric = metric.lower().strip()
    if normalized_metric not in SUPPORTED_METRICS:
        raise InvalidAlgorithmMetricException(metric, SUPPORTED_METRICS)

    # Ensure centralities are populated
    compute_all_centralities(graph)

    rankings: List[CentralityRankingItem] = []
    for node_id, data in graph.nodes(data=True):
        name = data.get("name") or data.get("label") or node_id
        ent_type = data.get("type", "Entity")
        role = data.get("role")

        if normalized_metric == "degree":
            score = float(data.get("degree", graph.degree(node_id)))
        elif normalized_metric == "betweenness":
            score = float(data.get("betweenness", 0.0))
        elif normalized_metric == "pagerank":
            score = float(data.get("pagerank", 0.0))
        else:
            score = 0.0

        rankings.append(
            CentralityRankingItem(
                id=str(node_id),
                name=str(name),
                type=str(ent_type),
                role=role,
                score=round(score, 4),
            )
        )

    # Sort descending by score
    rankings.sort(key=lambda item: item.score, reverse=True)
    return rankings[:limit]
