"""Запуск пограничной службы."""

import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.backend import Backend
from app.config import EdgeSettings
from app.edge import router
from app.store import Store

log = logging.getLogger("edge")


def create_app(settings: EdgeSettings | None = None, *, transport: httpx.BaseTransport | None = None) -> FastAPI:
    config = settings or EdgeSettings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        app.state.store.close()

    app = FastAPI(title="coreeuler edge", docs_url=None, redoc_url=None, lifespan=lifespan)
    app.state.settings = config
    app.state.cache_seconds = config.cache_seconds
    app.state.store = Store(config.db_path)
    app.state.backend = Backend(
        config.backend_url,
        timeout=config.timeout_seconds,
        accept_timeout=config.accept_timeout_seconds,
        transport=transport,
    )
    app.include_router(router)
    return app


app = create_app()
