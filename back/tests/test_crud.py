import pytest

from tests.conftest import VALID_PAYLOAD
from app.models import Category, Criticality, Status


def test_create_incident_generates_code_and_defaults(client):
    response = client.post("/api/v1/incidents", json=VALID_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert body["code"] == f"INC-{body['id']:05d}"
    assert body["status"] == "Aberto"
    assert body["version"] == 1
    assert body["created_at"].endswith("Z")
    assert body["updated_at"] == body["created_at"]


@pytest.mark.parametrize(
    "override",
    [
        {"unknown": "campo extra"},
        {"title": "   "},
        {"title": "x" * 121},
        {"category": "Categoria Inexistente"},
        {"criticality": "Crítica"},
        {"status": "Resolvido"},
        {"description": 123},
    ],
)
def test_create_incident_rejects_invalid_payload(client, override):
    response = client.post("/api/v1/incidents", json={**VALID_PAYLOAD, **override})

    assert response.status_code == 422


def test_get_incident_by_id(client):
    created = client.post("/api/v1/incidents", json=VALID_PAYLOAD).json()

    response = client.get(f"/api/v1/incidents/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_unknown_incident_returns_404(client):
    assert client.get("/api/v1/incidents/999").status_code == 404


def test_list_filters_by_criticality_category_and_status(client, insert_incident):
    insert_incident(criticality=Criticality.HIGH, category=Category.ROAD_BLOCKAGE, status=Status.OPEN)
    insert_incident(criticality=Criticality.HIGH, category=Category.MECHANICAL_PROBLEM, status=Status.CLOSED)
    insert_incident(criticality=Criticality.LOW, category=Category.ROAD_BLOCKAGE, status=Status.OPEN)

    def ids(**params):
        response = client.get("/api/v1/incidents", params=params)
        assert response.status_code == 200
        return {item["id"] for item in response.json()}

    assert len(ids()) == 3
    assert len(ids(criticality="Alta")) == 2
    assert len(ids(category="Bloqueio de Pista")) == 2
    assert len(ids(status="Fechado")) == 1
    assert len(ids(criticality="Alta", category="Bloqueio de Pista", status="Aberto")) == 1
    assert ids(criticality="Baixa", status="Fechado") == set()


def test_list_rejects_invalid_filter_value(client):
    assert client.get("/api/v1/incidents", params={"criticality": "Urgente"}).status_code == 422


def test_health(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_cors_allows_local_dev_origin_only(client):
    headers = {"Access-Control-Request-Method": "PATCH"}

    allowed = client.options("/api/v1/incidents/1", headers={**headers, "Origin": "http://localhost:5173"})
    denied = client.options("/api/v1/incidents/1", headers={**headers, "Origin": "http://evil.example"})

    assert allowed.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "access-control-allow-origin" not in denied.headers
