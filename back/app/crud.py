from sqlalchemy import case, select, update
from sqlalchemy.orm import Session

from app.models import Category, Criticality, Incident, Status, utcnow
from app.schemas import IncidentCreate

LIST_LIMIT = 200

# Equivale a: CASE criticality WHEN 'Alta' THEN 1 WHEN 'Média' THEN 2 ELSE 3 END
CRITICALITY_RANK = case(
    (Incident.criticality == Criticality.HIGH, 1),
    (Incident.criticality == Criticality.MEDIUM, 2),
    else_=3,
)


class IncidentNotFoundError(Exception):
    pass


class VersionConflictError(Exception):
    """A versão enviada não é a atual; carrega o incidente como está no banco."""

    def __init__(self, current: Incident) -> None:
        super().__init__("O incidente foi atualizado por outro analista.")
        self.current = current


def list_incidents(
    db: Session,
    *,
    criticality: Criticality | None = None,
    category: Category | None = None,
    status: Status | None = None,
) -> list[Incident]:
    statement = select(Incident)
    if criticality is not None:
        statement = statement.where(Incident.criticality == criticality)
    if category is not None:
        statement = statement.where(Incident.category == category)
    if status is not None:
        statement = statement.where(Incident.status == status)
    # `id` desempata incidentes com o mesmo created_at e mantém a ordem estável entre chamadas.
    statement = statement.order_by(
        case((Incident.status == Status.CLOSED, 1), else_=0).asc(),
        CRITICALITY_RANK,
        Incident.created_at.asc(),
        Incident.id.asc(),
    ).limit(LIST_LIMIT)
    return list(db.scalars(statement))


def get_incident(db: Session, incident_id: int) -> Incident | None:
    return db.get(Incident, incident_id)


def create_incident(db: Session, data: IncidentCreate) -> Incident:
    now = utcnow()
    incident = Incident(**data.model_dump(), code=f"PENDING-{now.timestamp()}", created_at=now, updated_at=now, version=1)
    db.add(incident)
    # O código depende do id, que só existe depois do INSERT; ambos ficam na mesma transação.
    db.flush()
    incident.code = f"INC-{incident.id:05d}"
    db.commit()
    return incident


def update_status(db: Session, incident_id: int, status: Status, version: int) -> Incident:
    """Atualiza o status com controle otimista de concorrência.

    O UPDATE é condicionado à versão e incrementa-a na mesma instrução, então dois PATCH
    com a mesma versão nunca vencem juntos. `status != :status` evita incrementar a versão
    quando nada muda (no-op), o que geraria conflitos desnecessários para outros clientes.
    """
    statement = (
        update(Incident)
        .where(Incident.id == incident_id, Incident.version == version, Incident.status != status)
        .values(status=status, version=Incident.version + 1, updated_at=utcnow())
        .execution_options(synchronize_session=False)
    )
    result = db.execute(statement)
    if result.rowcount == 1:
        db.commit()
        return _reload(db, incident_id)

    db.rollback()
    current = _reload(db, incident_id)
    if current is None:
        raise IncidentNotFoundError(incident_id)
    if current.version == version and current.status == status:
        return current
    raise VersionConflictError(current)


def _reload(db: Session, incident_id: int) -> Incident | None:
    # populate_existing força a releitura, ignorando o que o identity map já tenha em memória.
    return db.execute(
        select(Incident).where(Incident.id == incident_id).execution_options(populate_existing=True)
    ).scalar_one_or_none()
