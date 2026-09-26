"""
VERITAS - Paths Router
Multi-hop shortest path computation with human-readable analytical step explanations
and supporting evidence citations.
"""
from fastapi import APIRouter, Query
from backend.app.graph.pathfinder import find_shortest_path
from backend.app.models.responses import PathResponse
from backend.app.services.graph_service import graph_service

router = APIRouter(tags=["Pathfinder & Traversal"])


@router.get("/paths/shortest", response_model=PathResponse, summary="Find Shortest Investigative Path")
@router.get("/path", response_model=PathResponse, summary="Path Alias Endpoint", include_in_schema=False)
async def get_shortest_path(
    source: str = Query(..., description="Source entity ID (e.g. P006)"),
    target: str = Query(..., description="Target entity ID (e.g. P001)"),
):
    """
    Computes shortest connecting path between source and target entities,
    returning intermediate nodes, edges, and step-by-step forensic evidence citations.
    """
    return find_shortest_path(
        graph=graph_service.graph,
        source_id=source,
        target_id=target,
    )
