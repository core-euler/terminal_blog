"""Стенд пограничной службы: бэк подменяется транспортом httpx."""

import json
from dataclasses import dataclass

import httpx
import pytest
from fastapi.testclient import TestClient

from app.config import EdgeSettings
from app.main import create_app


@dataclass
class Reply:
    status: int
    body: dict | str


class FakeBackend:
    """Отвечает записанными ответами или изображает недоступность."""

    def __init__(self) -> None:
        self.down = True
        self.replies: dict[str, Reply] = {}
        self.received: list[httpx.Request] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.received.append(request)
        if self.down:
            raise httpx.ConnectError("бэк недоступен", request=request)
        path = request.url.path
        if request.method == "POST":
            path = f"POST {path}"
        reply = self.replies.get(path) or self.replies.get(request.url.path)
        if reply is None:
            return httpx.Response(404, json={"detail": "нет ответа"})
        body = reply.body if isinstance(reply.body, str) else json.dumps(reply.body, ensure_ascii=False)
        return httpx.Response(reply.status, content=body, headers={"Content-Type": "application/json"})


@pytest.fixture
def fake() -> FakeBackend:
    return FakeBackend()


@pytest.fixture
def edge(tmp_path, fake):
    settings = EdgeSettings(db_path=str(tmp_path / "edge.db"), cache_seconds=0)
    app = create_app(settings, transport=httpx.MockTransport(fake.handler))
    with TestClient(app) as client:
        client.fake = fake
        client.store = app.state.store
        yield client
