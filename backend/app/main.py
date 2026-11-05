"""Сборка приложения и зависимости."""

from collections.abc import Iterator

import sqlalchemy as sa
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api import internal, public
from app.config import Settings
from app.db import create_engine_for
from app.errors import DomainError


def get_session(request: Request) -> Iterator[Session]:
    engine = request.app.state.engine
    with Session(engine) as session:
        yield session


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or Settings()
    app = FastAPI(title="coreeuler API", docs_url="/api/docs", openapi_url="/api/openapi.json")
    app.state.settings = resolved
    app.state.engine = create_engine_for(resolved.database_url)

    if resolved.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=resolved.cors_origins,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["Content-Type", "X-Agent-Key"],
            max_age="600",
        )

    app.include_router(public.router, prefix="/api")
    app.include_router(internal.router, prefix="/api")

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, error: DomainError) -> JSONResponse:
        return JSONResponse(status_code=error.status, content={"code": error.code, "message": error.message})

    @app.get("/api/health")
    def health() -> JSONResponse:
        try:
            with app.state.engine.connect() as connection:
                connection.execute(sa.text("select 1"))
        except Exception:
            return JSONResponse(status_code=503, content={"status": "degraded", "database": "unavailable"})
        return JSONResponse(status_code=200, content={"status": "ok", "database": "ok"})

    return app
