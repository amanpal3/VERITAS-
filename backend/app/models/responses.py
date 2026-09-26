"""
VERITAS - API Response Schemas
Defines all response bodies strictly matching docs/API_CONTRACT.md.
"""
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from backend.app.models.entity import CytoscapeNode, EntityMetrics, EntitySummary
from backend.app.models.relationship import ConnectionDetail, CytoscapeEdge


class HealthResponse(BaseModel):
    status: str = "healthy"
    service: str = "veritas-api"
    version: str = "1.0.0"
    graph_backend: str = "in_memory_networkx"  # 'neo4j' or 'in_memory_networkx'
    total_nodes: int = 0
    total_edges: int = 0


class GraphMetadata(BaseModel):
    total_nodes: int
    total_edges: int
    communities_detected: int = 0
    title: Optional[str] = None


class GraphResponse(BaseModel):
    metadata: GraphMetadata
    nodes: List[CytoscapeNode]
    edges: List[CytoscapeEdge]


class EgoGraphResponse(BaseModel):
    nodes: List[CytoscapeNode]
    edges: List[CytoscapeEdge]


class EntityListResponse(BaseModel):
    total: int
    entities: List[EntitySummary]


class EntityDossier(BaseModel):
    id: str
    name: str
    type: str
    role: Optional[str] = None
    risk_score: float = 0.0
    aliases: List[str] = Field(default_factory=list)
    metrics: EntityMetrics
    connections: List[ConnectionDetail] = Field(default_factory=list)


class EntityDetailResponse(BaseModel):
    entity: EntityDossier


class PathStep(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    step: int
    from_entity: str = Field(..., alias="from", serialization_alias="from")
    relation: str
    to_entity: str = Field(..., alias="to", serialization_alias="to")
    evidence_snippet: Optional[str] = None


class PathResponse(BaseModel):
    source: str
    target: str
    found: bool
    length: int
    nodes: List[str] = Field(default_factory=list)
    edges: List[str] = Field(default_factory=list)
    path_details: List[PathStep] = Field(default_factory=list)


class CentralityRankingItem(BaseModel):
    id: str
    name: str
    type: str
    role: Optional[str] = None
    score: float


class CentralityResponse(BaseModel):
    metric: str
    rankings: List[CentralityRankingItem]


class CommunityItem(BaseModel):
    community_id: int
    label: str
    size: int
    members: List[str]


class CommunityResponse(BaseModel):
    total_communities: int
    communities: List[CommunityItem]
