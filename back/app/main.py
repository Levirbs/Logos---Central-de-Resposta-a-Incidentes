import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import OperationalError

from app import crud
from app.database import Base, SessionLocal, engine
from app.routers import incidents
from app.schemas import IncidentOut
from app.seed import seed_if_empty

logger = logging.getLogger("logos")

DEFAULT_CORS_ORIGINS = "http://localhost:5173"
DEFAULT_STATIC_DIR = Path(__file__).resolve().parents[2] / "front" / "dist"


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if seed_if_empty(db):
            logger.info("Banco vazio: incidentes de exemplo criados.")
    yield


def create_app(*, static_dir: Path | None = None) -> FastAPI:
    app = FastAPI(title="Logos API", version="1.0.0", lifespan=lifespan)

    origins = [origin.strip() for origin in os.getenv("LOGOS_CORS_ORIGINS", DEFAULT_CORS_ORIGINS).split(",") if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["GET", "POST", "PATCH"],
        allow_headers=["Content-Type"],
    )

    @app.exception_handler(crud.VersionConflictError)
    async def version_conflict_handler(_request: Request, error: crud.VersionConflictError) -> JSONResponse:
        # Resposta na raiz (e não em `detail`) para o cliente ler `current` diretamente.
        current = IncidentOut.model_validate(error.current)
        return JSONResponse(
            status_code=409,
            content={"code": "VERSION_CONFLICT", "message": str(error), "current": jsonable_encoder(current)},
        )

    @app.exception_handler(OperationalError)
    async def database_unavailable_handler(_request: Request, error: OperationalError) -> JSONResponse:
        logger.error("Falha no banco de dados: %s", error)
        return JSONResponse(
            status_code=503,
            content={"code": "DATABASE_UNAVAILABLE", "message": "Banco de dados temporariamente indisponível."},
            headers={"Retry-After": "2"},
        )

    app.include_router(incidents.router)

    static_path = static_dir if static_dir is not None else Path(os.getenv("LOGOS_STATIC_DIR", DEFAULT_STATIC_DIR))
    if static_path.is_dir():
        # Registrado por último para não sobrepor as rotas /api.
        app.mount("/", StaticFiles(directory=static_path, html=True), name="front")

    return app


app = create_app()
