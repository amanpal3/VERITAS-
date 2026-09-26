"""
VERITAS - Entity Service
Manages suspect search, directory queries, and detailed forensic dossiers.
"""
import logging
from typing import Any, Dict, List, Optional
import networkx as nx

from backend.app.core.exceptions import EntityNotFoundException
from backend.app.models.entity import EntityMetrics, EntitySummary
from backend.app.models.relationship import ConnectionDetail, Provenance
from backend.app.models.responses import EntityDetailResponse, EntityDossier, EntityListResponse
from backend.app.services.graph_service import graph_service

logger = logging.getLogger("veritas.services.entity")


class EntityService:
    """Service providing suspect search and dossier compilation."""

    def get_entities(
        self,
        q: Optional[str] = None,
        entity_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> EntityListResponse:
        """Search and list entities with text query, type filtering, and pagination."""
        graph = graph_service.graph
        matched: List[EntitySummary] = []

        query = q.lower().strip() if q else None
        filter_type = entity_type.lower().strip() if entity_type else None

        for node_id, data in graph.nodes(data=True):
            nid = str(node_id)
            name = str(data.get("name") or data.get("label") or nid)
            etype = str(data.get("type", "Entity"))
            role = data.get("role")
            aliases = data.get("aliases", [])

            # Filter by type
            if filter_type and etype.lower() != filter_type:
                continue

            # Filter by search query
            if query:
                text_corpus = f"{nid} {name} {role or ''} {' '.join(aliases)}".lower()
                if query not in text_corpus:
                    continue

            summary = EntitySummary(
                id=nid,
                name=name,
                type=etype,
                role=role,
                risk_score=float(data.get("risk_score", 0.0)),
                aliases=aliases,
                community_id=data.get("community_id"),
            )
            matched.append(summary)

        # Sort by risk score descending by default
        matched.sort(key=lambda e: e.risk_score, reverse=True)

        total = len(matched)
        paginated = matched[offset : offset + limit]

        return EntityListResponse(total=total, entities=paginated)

    def get_entity_dossier(self, entity_id: str) -> EntityDetailResponse:
        """Compile complete investigative dossier for an entity including metrics and connections."""
        graph = graph_service.graph
        if entity_id not in graph.nodes:
            raise EntityNotFoundException(entity_id)

        data = graph.nodes[entity_id]
        name = str(data.get("name") or data.get("label") or entity_id)
        etype = str(data.get("type", "Entity"))
        role = data.get("role")
        risk_score = float(data.get("risk_score", 0.0))
        aliases = data.get("aliases", [])

        # Metrics
        metrics = EntityMetrics(
            degree=int(data.get("degree", graph.degree(entity_id))),
            betweenness=float(data.get("betweenness", 0.0)),
            pagerank=float(data.get("pagerank", 0.0)),
            community_id=data.get("community_id"),
        )

        # Connections (both outgoing and incoming edges)
        connections: List[ConnectionDetail] = []

        # Outgoing edges
        for _, target, key, edge_data in graph.out_edges(entity_id, keys=True, data=True):
            tgt_id = str(target)
            tgt_node = graph.nodes.get(tgt_id, {})
            tgt_name = str(tgt_node.get("name") or tgt_node.get("label") or tgt_id)
            tgt_type = str(tgt_node.get("type", "Entity"))

            prov_raw = edge_data.get("provenance", {})
            prov = prov_raw if isinstance(prov_raw, Provenance) else Provenance(**(prov_raw or {}))

            connections.append(
                ConnectionDetail(
                    relationship_id=edge_data.get("id") or str(key),
                    type=edge_data.get("type", "ASSOCIATED_WITH"),
                    target_id=tgt_id,
                    target_name=tgt_name,
                    target_type=tgt_type,
                    provenance=prov,
                    weight=float(edge_data.get("weight", 1.0)),
                    timestamp=edge_data.get("timestamp"),
                )
            )

        # Incoming edges
        for source, _, key, edge_data in graph.in_edges(entity_id, keys=True, data=True):
            src_id = str(source)
            src_node = graph.nodes.get(src_id, {})
            src_name = str(src_node.get("name") or src_node.get("label") or src_id)
            src_type = str(src_node.get("type", "Entity"))

            prov_raw = edge_data.get("provenance", {})
            prov = prov_raw if isinstance(prov_raw, Provenance) else Provenance(**(prov_raw or {}))

            connections.append(
                ConnectionDetail(
                    relationship_id=edge_data.get("id") or str(key),
                    type=edge_data.get("type", "ASSOCIATED_WITH"),
                    target_id=src_id,
                    target_name=src_name,
                    target_type=src_type,
                    provenance=prov,
                    weight=float(edge_data.get("weight", 1.0)),
                    timestamp=edge_data.get("timestamp"),
                )
            )

        dossier = EntityDossier(
            id=entity_id,
            name=name,
            type=etype,
            role=role,
            risk_score=risk_score,
            aliases=aliases,
            metrics=metrics,
            connections=connections,
        )

        return EntityDetailResponse(entity=dossier)


# Global singleton instance
entity_service = EntityService()
