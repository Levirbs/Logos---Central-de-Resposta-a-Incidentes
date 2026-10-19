from collections.abc import Callable, Iterator
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, create_sqlite_engine, get_db
from app.main import create_app
from app.models import Category, Criticality, Incident, Status

BASE_TIME = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)


@pytest.fixture()
def engine(tmp_path: Path) -> Iterator[Engine]:
    # Arquivo temporário (e não :memory:) para exercitar WAL e conexões simultâneas de verdade.
    test_engine = create_sqlite_engine(f"sqlite:///{tmp_path / 'test.db'}")
    Base.metadata.create_all(test_engine)
    yield test_engine
    test_engine.dispose()


@pytest.fixture()
def session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture()
def make_client(session_factory: sessionmaker[Session], tmp_path: Path) -> Callable[[], TestClient]:
    """Cada chamada devolve um cliente novo sobre o mesmo banco (um por thread nos testes de concorrência)."""

    def override_get_db() -> Iterator[Session]:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app = create_app(static_dir=tmp_path / "sem-front")
    app.dependency_overrides[get_db] = override_get_db
    return lambda: TestClient(app)


@pytest.fixture()
def client(make_client: Callable[[], TestClient]) -> TestClient:
    return make_client()


@pytest.fixture()
def insert_incident(session_factory: sessionmaker[Session]) -> Callable[..., int]:
    def insert(
        *,
        criticality: Criticality = Criticality.MEDIUM,
        category: Category = Category.VEHICLE_ACCIDENT,
        status: Status = Status.OPEN,
        minutes: int = 0,
    ) -> int:
        created_at = BASE_TIME + timedelta(minutes=minutes)
        with session_factory() as db:
            incident = Incident(
                code="TMP",
                title="Incidente de teste",
                description="Descrição de teste",
                category=category,
                criticality=criticality,
                status=status,
                location="BR-116, km 10",
                reporter="Teste",
                created_at=created_at,
                updated_at=created_at,
                version=1,
            )
            db.add(incident)
            db.flush()
            incident.code = f"INC-{incident.id:05d}"
            db.commit()
            return incident.id

    return insert


VALID_PAYLOAD = {
    "title": "Colisão na BR-116",
    "description": "Colisão entre dois veículos na pista norte.",
    "category": "Acidente com Veículo",
    "criticality": "Alta",
    "location": "BR-116, km 214 — Pista norte",
    "reporter": "Central de Operações 02",
}
