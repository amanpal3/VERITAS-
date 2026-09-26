"""
VERITAS Backend - Entities Endpoints Test Suite
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_list_entities(client: TestClient):
    response = client.get("/api/v1/entities")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "entities" in data
    assert data["total"] >= 29
    assert len(data["entities"]) > 0


def test_search_entities_by_query(client: TestClient):
    response = client.get("/api/v1/entities?q=Vikram")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    names = [e["name"] for e in data["entities"]]
    assert any("Vikram" in n for n in names)


def test_filter_entities_by_type(client: TestClient):
    response = client.get("/api/v1/entities?type=Phone")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    for ent in data["entities"]:
        assert ent["type"] == "Phone"


def test_get_entity_dossier_success(client: TestClient):
    response = client.get("/api/v1/entities/P001")
    assert response.status_code == 200
    data = response.json()
    assert "entity" in data
    entity = data["entity"]
    assert entity["id"] == "P001"
    assert "Vikramaditya Singhania" in entity["name"]
    assert "metrics" in entity
    assert "degree" in entity["metrics"]
    assert "betweenness" in entity["metrics"]
    assert "connections" in entity
    assert len(entity["connections"]) > 0

    first_conn = entity["connections"][0]
    assert "relationship_id" in first_conn
    assert "target_id" in first_conn
    assert "provenance" in first_conn
    assert "source_id" in first_conn["provenance"]


def test_get_entity_dossier_not_found(client: TestClient):
    response = client.get("/api/v1/entities/P_NON_EXISTENT")
    assert response.status_code == 404
    error = response.json().get("error", {})
    assert error.get("code") == "ENTITY_NOT_FOUND"


def test_get_entity_connections_endpoint(client: TestClient):
    response = client.get("/api/v1/entities/P001/connections?depth=1")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) > 1
