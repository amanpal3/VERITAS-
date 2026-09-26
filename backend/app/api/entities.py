"""
VERITAS - Entities Router
Endpoints for entity directory search, suspect dossiers, and direct neighborhood connections.
"""
from typing import Optional
from fastapi import APIRouter, Query
from backend.app.models.responses import EgoGraphResponse, EntityDetailResponse, EntityListResponse
from backend.app.services.entity_service import entity_service
from backend.app.services.graph_service import graph_service

router = APIRouter(prefix="/entities", tags=["Entities & Suspects"])


@router.get("", response_model=EntityListResponse, summary="Search & Directory")
async def list_entities(
    q: Optional[str] = Query(None, description="Text search query across name, role, and aliases"),
    type: Optional[str] = Query(None, description="Filter by entity type"),
    limit: int = Query(50, ge=1, le=500, description="Page size limit"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    """
    Search across entities with text matching, type filtering, and pagination.
    """
    return entity_service.get_entities(
        q=q,
        entity_type=type,
        limit=limit,
        offset=offset,
    )


@router.get("/{entity_id}", response_model=EntityDetailResponse, summary="Suspect Dossier Details")
async def get_entity_by_id(entity_id: str):
    """
    Returns complete suspect dossier including centrality metrics, evidentiary citations,
    and all direct incoming and outgoing graph connections.
    """
    return entity_service.get_entity_dossier(entity_id=entity_id)


@router.get("/{entity_id}/connections", response_model=EgoGraphResponse, summary="Entity Neighborhood Connections")
async def get_entity_connections(
    entity_id: str,
    depth: int = Query(1, ge=1, le=2, alias="depth", description="Traversal depth (1 or 2)"),
    hops: Optional[int] = Query(None, ge=1, le=2, description="Alternative alias for depth"),
):
    """
    Returns a scoped Cytoscape graph centered on entity_id up to depth hops.
    """
    effective_depth = hops if hops is not None else depth
    return graph_service.get_ego_network(entity_id=entity_id, hops=effective_depth)
