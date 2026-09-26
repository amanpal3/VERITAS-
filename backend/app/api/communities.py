"""
VERITAS - Communities Router
Detects and retrieves criminal sub-cell groupings and syndicate partitions.
"""
from fastapi import APIRouter
from backend.app.models.responses import CommunityResponse
from backend.app.services.analytics_service import analytics_service

router = APIRouter(tags=["Community Detection"])


@router.get("/communities", response_model=CommunityResponse, summary="Get Criminal Communities")
@router.get("/analytics/communities", response_model=CommunityResponse, summary="Communities Analytics Alias", include_in_schema=False)
async def get_communities():
    """
    Returns detected criminal sub-gangs and tactical syndicates with member listings.
    """
    return analytics_service.get_communities()
