"""
VERITAS Backend - Graph Endpoints Test Suite
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_get_global_graph(client: TestClient):
    response = client.get("/api/v1/graph")
    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
    assert "nodes" in data
    assert "edges" in data
    assert data["metadata"]["total_nodes"] >= 29
    assert data["metadata"]["total_edges"] >= 33

    # Validate Cytoscape node shape
    first_node = data["nodes"][0]
    assert "data" in first_node
    assert "id" in first_node["data"]
    assert "label" in first_node["data"]
    assert "type" in first_node["data"]


def test_get_graph_filter_by_type(client: TestClient):
    response = client.get("/api/v1/graph?entity_type=Person")
    assert response.status_code == 200
    data = response.json()
    for node in data["nodes"]:
        assert node["data"]["type"] == "Person"


def test_get_graph_filter_by_risk(client: TestClient):
    response = client.get("/api/v1/graph?min_risk=85")
    assert response.status_code == 200
    data = response.json()
    for node in data["nodes"]:
        assert node["data"]["risk_score"] >= 85


def test_get_ego_network(client: TestClient):
    response = client.get("/api/v1/graph/ego/P001?hops=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["nodes"]) > 1
    node_ids = [n["data"]["id"] for n in data["nodes"]]
    assert "P001" in node_ids


def test_get_ego_network_not_found(client: TestClient):
    response = client.get("/api/v1/graph/ego/P99999")
    assert response.status_code == 404
    error = response.json().get("error", {})
    assert error.get("code") == "ENTITY_NOT_FOUND"
