"""
VERITAS - Analytics Router
Centrality rankings (Degree, Betweenness, PageRank) and structural network statistics.
"""
from fastapi import APIRouter, Query
from backend.app.models.responses import CentralityResponse, CommunityResponse
from backend.app.services.analytics_service import analytics_service

router = APIRouter(prefix="/analytics", tags=["Graph Analytics"])


@router.get("/centrality", response_model=CentralityResponse, summary="Get Centrality Rankings")
async def get_centrality(
    metric: str = Query(
        "betweenness",
        description="Centrality algorithm metric ('degree', 'betweenness', 'pagerank')",
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Number of top entities to return",
    ),
):
    """
    Computes and ranks network entities according to structural importance:
    - degree: High-volume operational hubs
    - betweenness: Key gatekeepers and brokers bridging disparate cells
    - pagerank: Structural masterminds linked to influential lieutenants
    """
    return analytics_service.get_centrality(metric=metric, limit=limit)


@router.get("/communities", response_model=CommunityResponse, summary="Get Community Clusters")
async def get_communities_analytics():
    """
    Returns detected criminal sub-groups and operational cells.
    """
    return analytics_service.get_communities()
