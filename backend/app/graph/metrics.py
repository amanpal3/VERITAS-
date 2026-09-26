"""
VERITAS - Graph Structural Metrics
Calculates node degrees, network density, and structural connectivity statistics.
"""
import logging
from typing import Any, Dict
import networkx as nx

logger = logging.getLogger("veritas.graph.metrics")


def compute_graph_metrics(graph: nx.MultiDiGraph) -> Dict[str, Any]:
    """
    Computes global graph metrics and decorates nodes with individual degree metrics.
    """
    total_nodes = graph.number_of_nodes()
    total_edges = graph.number_of_edges()

    if total_nodes == 0:
        return {
            "total_nodes": 0,
            "total_edges": 0,
            "density": 0.0,
            "avg_degree": 0.0,
        }

    # Populate degree on each node
    for node in graph.nodes():
        deg = graph.degree(node)
        in_deg = graph.in_degree(node)
        out_deg = graph.out_degree(node)
        graph.nodes[node]["degree"] = deg
        graph.nodes[node]["in_degree"] = in_deg
        graph.nodes[node]["out_degree"] = out_deg

    # Simple DiGraph view for density
    simple_g = nx.DiGraph(graph)
    density = nx.density(simple_g)
    avg_deg = (total_edges * 2.0) / total_nodes if total_nodes > 0 else 0.0

    return {
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "density": round(float(density), 4),
        "avg_degree": round(float(avg_deg), 2),
    }
