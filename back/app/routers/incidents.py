from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.models import Category, Criticality, Status
from app.schemas import ConflictResponse, IncidentCreate, IncidentOut, StatusUpdate

router = APIRouter(prefix="/api/v1")


@router.get("/health")
def health(response: Response, db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unavailable", "database": "down"}
    return {"status": "ok", "database": "up"}


@router.get("/incidents", response_model=list[IncidentOut])
def list_incidents(
    criticality: Criticality | None = None,
    category: Category | None = None,
    status: Status | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return crud.list_incidents(db, criticality=criticality, category=category, status=status)


@router.get("/incidents/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = crud.get_incident(db, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incidente não encontrado.")
    return incident


@router.post("/incidents", response_model=IncidentOut, status_code=201)
def create_incident(data: IncidentCreate, db: Session = Depends(get_db)):
    return crud.create_incident(db, data)


@router.patch(
    "/incidents/{incident_id}",
    response_model=IncidentOut,
    responses={409: {"model": ConflictResponse, "description": "Versão desatualizada."}},
)
def update_incident_status(incident_id: int, data: StatusUpdate, db: Session = Depends(get_db)):
    try:
        return crud.update_status(db, incident_id, data.status, data.version)
    except crud.IncidentNotFoundError:
        raise HTTPException(status_code=404, detail="Incidente não encontrado.") from None
