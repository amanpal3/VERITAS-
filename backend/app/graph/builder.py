"""
VERITAS - Graph Builder
Constructs and hydrates NetworkX MultiDiGraph instances from demo datasets
or Member 1 IntelligencePipeline results.
"""
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import networkx as nx

from backend.app.core.config import get_settings
from backend.app.models.entity import CytoscapeNode, CytoscapeNodeData
from backend.app.models.relationship import CytoscapeEdge, CytoscapeEdgeData, Provenance

logger = logging.getLogger("veritas.graph.builder")


def build_networkx_graph_from_demo(demo_path: Optional[Path] = None) -> nx.MultiDiGraph:
    """
    Hydrate a NetworkX MultiDiGraph from demo JSON files.
    Prefers graph.json if present; otherwise joins entities.json and relationships.json.
    """
    settings = get_settings()
    base_dir = demo_path or settings.DEMO_DATA_PATH

    graph = nx.MultiDiGraph()
    graph.graph["title"] = "Operation Shadow Syndicate - Knowledge Graph"
    graph.graph["backend"] = "in_memory_networkx"

    graph_file = base_dir / "graph.json"
    entities_file = base_dir / "entities.json"
    relationships_file = base_dir / "relationships.json"

    if graph_file.exists():
        try:
            with open(graph_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Metadata
            meta = data.get("metadata", {})
            for k, v in meta.items():
                graph.graph[k] = v

            # Nodes
            for node_wrapper in data.get("nodes", []):
                nd = node_wrapper.get("data", {})
                node_id = nd.get("id")
                if node_id:
                    graph.add_node(node_id, **nd)

            # Edges
            for edge_wrapper in data.get("edges", []):
                ed = edge_wrapper.get("data", {})
                src = ed.get("source")
                tgt = ed.get("target")
                if src and tgt:
                    graph.add_edge(src, tgt, key=ed.get("id"), **ed)

            logger.info(f"Loaded graph from {graph_file} with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
            return graph
        except Exception as e:
            logger.error(f"Error loading {graph_file}: {e}, falling back to entity/relationship files")

    # Fallback to entities.json + relationships.json
    if entities_file.exists():
        with open(entities_file, "r", encoding="utf-8") as f:
            entities = json.load(f)
            for e in entities:
                node_id = e.get("id")
                if node_id:
                    # ensure label exists
                    if "label" not in e:
                        e["label"] = e.get("name", node_id)
                    graph.add_node(node_id, **e)

    if relationships_file.exists():
        with open(relationships_file, "r", encoding="utf-8") as f:
            relationships = json.load(f)
            for r in relationships:
                src = r.get("source")
                tgt = r.get("target")
                if src and tgt:
                    graph.add_edge(src, tgt, key=r.get("id"), **r)

    logger.info(f"Loaded graph from entities/relationships with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
    return graph


def build_networkx_graph_from_pipeline_result(pipeline_result: Any) -> nx.MultiDiGraph:
    """
    Hydrate a NetworkX MultiDiGraph from Member 1's PipelineResult object.
    """
    graph = nx.MultiDiGraph()
    graph.graph["title"] = "VERITAS Intelligence Pipeline Knowledge Graph"
    graph.graph["backend"] = "in_memory_networkx"

    # Ingest entities
    for entity in getattr(pipeline_result, "entities", []):
        ent_dict = entity.model_dump() if hasattr(entity, "model_dump") else dict(entity)
        ent_id = ent_dict["id"]
        # Ensure Cytoscape compatible label
        if "label" not in ent_dict or not ent_dict["label"]:
            ent_dict["label"] = ent_dict.get("name") or ent_id
        if "name" not in ent_dict or not ent_dict["name"]:
            ent_dict["name"] = ent_dict.get("label") or ent_id
        graph.add_node(ent_id, **ent_dict)

    # Ingest relationships
    for rel in getattr(pipeline_result, "relationships", []):
        rel_dict = rel.model_dump() if hasattr(rel, "model_dump") else dict(rel)
        src = rel_dict["source"]
        tgt = rel_dict["target"]
        edge_id = rel_dict.get("id")
        graph.add_edge(src, tgt, key=edge_id, **rel_dict)

    return graph


def graph_to_cytoscape_elements(graph: nx.MultiDiGraph) -> Dict[str, Any]:
    """
    Convert a NetworkX MultiDiGraph into Cytoscape.js { nodes: [...], edges: [...] } payload.
    """
    nodes: List[Dict[str, Any]] = []
    for node_id, data in graph.nodes(data=True):
        payload = dict(data)
        payload["id"] = str(node_id)
        if "label" not in payload or not payload["label"]:
            payload["label"] = payload.get("name") or str(node_id)
        node_model = CytoscapeNode(data=CytoscapeNodeData(**payload))
        nodes.append(node_model.model_dump())

    edges: List[Dict[str, Any]] = []
    for u, v, key, data in graph.edges(keys=True, data=True):
        payload = dict(data)
        payload["source"] = str(u)
        payload["target"] = str(v)
        if "id" not in payload or not payload["id"]:
            payload["id"] = str(key) if key else f"edge_{u}_{v}"
        edge_model = CytoscapeEdge(data=CytoscapeEdgeData(**payload))
        edges.append(edge_model.model_dump())

    return {
        "nodes": nodes,
        "edges": edges,
    }
