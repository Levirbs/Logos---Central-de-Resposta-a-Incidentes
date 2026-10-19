from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum, Integer, String, Text, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Category(str, Enum):
    VEHICLE_ACCIDENT = "Acidente com Veículo"
    ACCIDENT_WITH_VICTIMS = "Acidente com Vítimas"
    ATYPICAL_WEATHER = "Condição Climática Atípica na Pista"
    MECHANICAL_PROBLEM = "Problema Mecânico"
    ROAD_BLOCKAGE = "Bloqueio de Pista"


class Criticality(str, Enum):
    HIGH = "Alta"
    MEDIUM = "Média"
    LOW = "Baixa"


class Status(str, Enum):
    OPEN = "Aberto"
    INVESTIGATING = "Em Investigação"
    INCONCLUSIVE = "Inconclusivo"
    CLOSED = "Fechado"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UTCDateTime(TypeDecorator):
    """SQLite não guarda fuso; grava UTC e devolve datetimes com tzinfo para o JSON sair com 'Z'."""

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("Datetime sem fuso horário não é aceito")
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    def process_result_value(self, value: datetime | None, dialect) -> datetime | None:
        return value.replace(tzinfo=timezone.utc) if value is not None else None


def _enum_column(enum_cls: type[Enum]) -> SAEnum:
    # Persiste os valores ("Média") e não os nomes dos membros, e cria CHECK no banco.
    return SAEnum(
        enum_cls,
        values_callable=lambda members: [member.value for member in members],
        native_enum=False,
        create_constraint=True,
        validate_strings=True,
        length=40,
        name=f"ck_{enum_cls.__name__.lower()}",
    )


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Preenchido com INC-{id:05d} logo após o INSERT, quando o id já existe.
    code: Mapped[str] = mapped_column(String(20), index=True, unique=True)
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[Category] = mapped_column(_enum_column(Category), index=True)
    criticality: Mapped[Criticality] = mapped_column(_enum_column(Criticality), index=True)
    status: Mapped[Status] = mapped_column(_enum_column(Status), index=True)
    location: Mapped[str] = mapped_column(String(200))
    reporter: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utcnow)
    version: Mapped[int] = mapped_column(Integer, default=1)
