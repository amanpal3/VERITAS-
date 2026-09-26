"""
VERITAS - Analytics Service
Dispatches graph centrality rankings and Louvain community partitions.
"""
import logging
from backend.app.graph.centrality import get_centrality_rankings
from backend.app.graph.communities import detect_and_assign_communities
from backend.app.models.responses import CentralityResponse, CommunityResponse
from backend.app.services.graph_service import graph_service

logger = logging.getLogger("veritas.services.analytics")


class AnalyticsService:
    """Service providing graph intelligence analytics."""

    def get_centrality(self, metric: str = "betweenness", limit: int = 20) -> CentralityResponse:
        """Fetch ranked entity list for requested centrality metric."""
        rankings = get_centrality_rankings(graph_service.graph, metric=metric, limit=limit)
        return CentralityResponse(metric=metric, rankings=rankings)

    def get_communities(self) -> CommunityResponse:
        """Fetch Louvain detected criminal syndicates and cell clusters."""
        communities = detect_and_assign_communities(graph_service.graph)
        return CommunityResponse(total_communities=len(communities), communities=communities)


# Global singleton instance
analytics_service = AnalyticsService()
