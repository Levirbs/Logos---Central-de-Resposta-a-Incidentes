import os
from collections.abc import Iterator
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

BACK_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.getenv("LOGOS_DATABASE_URL", f"sqlite:///{BACK_DIR / 'logos.db'}")


class Base(DeclarativeBase):
    pass


def configure_sqlite(engine: Engine) -> None:
    """WAL permite leituras durante uma escrita; busy_timeout faz a escrita esperar o lock em vez de falhar."""

    @event.listens_for(engine, "connect")
    def set_pragmas(dbapi_connection, _record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()


def create_sqlite_engine(url: str = DATABASE_URL) -> Engine:
    engine = create_engine(url, connect_args={"check_same_thread": False})
    configure_sqlite(engine)
    return engine


engine = create_sqlite_engine()
# expire_on_commit=False evita um SELECT implícito ao serializar a resposta; os dados
# devolvidos pelo CRUD são sempre relidos explicitamente quando precisam estar frescos.
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
