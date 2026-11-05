"""Пограничная служба: кэш чтения и приём комментариев в очередь."""

import json

import httpx
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from app.backend import Backend
from app.store import Store

router = APIRouter()

READ_PATHS = ("/api/news",)
SKIP_HEADERS = {"host", "content-length", "connection", "accept-encoding"}


def _store(request: Request) -> Store:
    return request.app.state.store


def _backend(request: Request) -> Backend:
    return request.app.state.backend


def _query(request: Request) -> str:
    return request.url.query


def _age_seconds(stored_at: str) -> float:
    from datetime import datetime, timezone

    try:
        moment = datetime.fromisoformat(stored_at)
    except ValueError:
        return float("inf")
    return (datetime.now(timezone.utc) - moment).total_seconds()


@router.get("/api/news")
def read_news(request: Request) -> Response:
    return _read(request, "/api/news")


@router.get("/api/news/{slug}")
def read_news_item(slug: str, request: Request) -> Response:
    return _read(request, f"/api/news/{slug}")


@router.get("/api/news/{slug}/comments")
def read_comments(slug: str, request: Request) -> Response:
    return _read(request, f"/api/news/{slug}/comments")


def _read(request: Request, path: str) -> Response:
    """Читает у бэка, при недоступности отдаёт последний удачный ответ."""
    store = _store(request)
    query = _query(request)
    key = f"{path}?{query}" if query else path
    cached = store.cached(key)

    if cached is not None and _age_seconds(cached["stored_at"]) < request.app.state.cache_seconds:
        return _answer(cached["body"], cached["status"], "fresh")

    try:
        status, body = _backend(request).get(path, query)
    except httpx.HTTPError:
        if cached is not None:
            return _answer(cached["body"], cached["status"], "stale")
        return JSONResponse(
            {"detail": "данные временно недоступны, попробуйте позже"},
            status_code=503,
            headers={"X-Edge": "empty"},
        )

    if status < 400:
        store.remember(key, body, status)
    return _answer(body, status, "backend")


def _answer(body: str, status: int, source: str) -> Response:
    return Response(
        content=body,
        status_code=status,
        media_type="application/json",
        headers={"X-Edge": source, "Cache-Control": "no-cache"},
    )


@router.post("/api/news/{slug}/comments")
async def post_comment(slug: str, request: Request) -> Response:
    """Сразу отдаёт бэку; если тот недоступен — кладёт в очередь и отвечает принятым."""
    path = f"/api/news/{slug}/comments"
    payload = json.loads(await request.body() or b"{}")
    headers = {key: value for key, value in request.headers.items() if key.lower() not in SKIP_HEADERS}
    client_id = (
        request.headers.get("x-idempotency-key")
        or payload.get("client_id")
    )

    try:
        status, body = _backend(request).post(path, payload, headers)
    except httpx.HTTPError:
        status, body = 0, ""

    if status and status < 400:
        return Response(content=body, status_code=status, media_type="application/json",
                        headers={"X-Edge": "backend"})
    if status and status in (401, 403, 404, 422, 429):
        return Response(content=body, status_code=status, media_type="application/json",
                        headers={"X-Edge": "backend"})

    key = _store(request).enqueue(path, payload, headers, client_id=client_id)
    return JSONResponse(
        {
            "id": key,
            "status": "queued",
            "message": "комментарий принят и отправится на проверку позже",
        },
        status_code=202,
        headers={"X-Edge": "queued"},
    )


@router.get("/api/health")
def health(request: Request) -> Response:
    store = _store(request)
    return JSONResponse(
        {
            "status": "ok",
            "queued": store.count("pending"),
            "rejected": store.count("rejected"),
        }
    )
