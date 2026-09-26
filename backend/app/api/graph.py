"""
VERITAS - Graph Router
Provides global network graph data and localized ego-network neighborhoods for Cytoscape.js canvas.
"""
from typing import Optional
from fastapi import APIRouter, Query
from backend.app.models.responses import EgoGraphResponse, GraphResponse
from backend.app.services.graph_service import graph_service

router = APIRouter(tags=["Knowledge Graph"])


@router.get("/graph", response_model=GraphResponse, summary="Get Global Knowledge Graph")
async def get_graph(
    entity_type: Optional[str] = Query(
        None,
        description="Filter by type (Person, Phone, Vehicle, Organization, Location, BankAccount)",
    ),
    min_risk: float = Query(
        0.0,
        ge=0.0,
        le=100.0,
        description="Minimum risk score filter [0-100]",
    ),
    min_weight: float = Query(
        0.0,
        ge=0.0,
        description="Minimum relationship weight filter",
    ),
):
    """
    Returns nodes and edges formatted specifically for Cytoscape.js canvas rendering,
    with optional filtering by entity type, risk score, and edge weight.
    """
    return graph_service.get_graph_data(
        entity_type=entity_type,
        min_risk=min_risk,
        min_weight=min_weight,
    )


@router.get("/graph/ego/{entity_id}", response_model=EgoGraphResponse, summary="Get Ego-Network Neighborhood")
async def get_ego_network(
    entity_id: str,
    hops: int = Query(1, ge=1, le=2, description="Neighborhood expansion radius (1 or 2 hops)"),
):
    """
    Returns a localized subgraph centered on the target entity within 1 to 2 hops.
    """
    return graph_service.get_ego_network(entity_id=entity_id, hops=hops)
