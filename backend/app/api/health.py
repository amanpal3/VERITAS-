"""
VERITAS - Health Check Router
Liveness and readiness endpoint reporting backend mode (Neo4j vs In-Memory NetworkX) and graph size.
"""
from fastapi import APIRouter
from backend.app.models.responses import HealthResponse
from backend.app.services.graph_service import graph_service

router = APIRouter(tags=["System Health"])


@router.get("/health", response_model=HealthResponse, summary="System Health & Readiness")
async def get_health():
    """
    Returns system liveness, active graph backend (Neo4j or In-Memory NetworkX),
    and current node/edge counts.
    """
    return graph_service.get_health()
