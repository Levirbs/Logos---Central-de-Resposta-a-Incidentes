from datetime import timedelta

from sqlalchemy import insert

from app.crud import LIST_LIMIT
from app.models import Category, Criticality, Incident, Status
from tests.conftest import BASE_TIME


def test_orders_by_criticality_then_oldest_first(client, insert_incident):
    closed_high = insert_incident(criticality=Criticality.HIGH, status=Status.CLOSED, minutes=0)
    closed_low = insert_incident(criticality=Criticality.LOW, status=Status.CLOSED, minutes=1)
    low_old = insert_incident(criticality=Criticality.LOW, minutes=0)
    high_new = insert_incident(criticality=Criticality.HIGH, minutes=50)
    medium_old = insert_incident(criticality=Criticality.MEDIUM, minutes=5)
    high_old = insert_incident(criticality=Criticality.HIGH, minutes=10)
    medium_new = insert_incident(criticality=Criticality.MEDIUM, minutes=30)
    low_new = insert_incident(criticality=Criticality.LOW, minutes=40)

    response = client.get("/api/v1/incidents")

    assert [item["id"] for item in response.json()] == [
        high_old, high_new, medium_old, medium_new, low_old, low_new, closed_high, closed_low,
    ]


def test_ordering_is_preserved_when_filtering(client, insert_incident):
    newer = insert_incident(criticality=Criticality.HIGH, category=Category.ROAD_BLOCKAGE, minutes=20)
    older = insert_incident(criticality=Criticality.HIGH, category=Category.ROAD_BLOCKAGE, minutes=1)
    insert_incident(criticality=Criticality.LOW, category=Category.ROAD_BLOCKAGE, minutes=0)

    response = client.get("/api/v1/incidents", params={"category": "Bloqueio de Pista"})

    assert [item["id"] for item in response.json()][:2] == [older, newer]


def test_equal_timestamps_have_stable_order(client, insert_incident):
    ids = [insert_incident(criticality=Criticality.HIGH, minutes=0) for _ in range(3)]

    first = [item["id"] for item in client.get("/api/v1/incidents").json()]
    second = [item["id"] for item in client.get("/api/v1/incidents").json()]

    assert first == second == ids


def test_list_is_limited(client, session_factory):
    rows = [
        {
            "code": f"INC-{index:05d}",
            "title": "Incidente de teste",
            "description": "Descrição de teste",
            "category": Category.VEHICLE_ACCIDENT,
            "criticality": Criticality.LOW,
            "status": Status.OPEN,
            "location": "BR-116, km 10",
            "reporter": "Teste",
            "created_at": BASE_TIME + timedelta(minutes=index),
            "updated_at": BASE_TIME + timedelta(minutes=index),
            "version": 1,
        }
        for index in range(1, LIST_LIMIT + 6)
    ]
    with session_factory() as db:
        db.execute(insert(Incident), rows)
        db.commit()

    assert len(client.get("/api/v1/incidents").json()) == LIST_LIMIT
