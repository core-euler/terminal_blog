"""Браузерные запросы с другого источника разрешаются только по настройке."""

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def _client(settings: Settings, **overrides) -> TestClient:
    values = settings.model_dump() | overrides
    application = create_app(Settings(**values))
    return TestClient(application)


def test_origin_is_allowed_only_when_listed(settings):
    allowed = _client(settings, cors_origins=["http://localhost:4321"])
    denied = _client(settings)

    headers = {"Origin": "http://localhost:4321"}
    assert allowed.get("/api/news", headers=headers).headers.get("access-control-allow-origin") == "http://localhost:4321"
    assert "access-control-allow-origin" not in denied.get("/api/news", headers=headers).headers


def test_preflight_passes_for_post_from_allowed_origin(settings):
    client = _client(settings, cors_origins=["http://localhost:4321"])

    response = client.options(
        "/api/news/любая/comments",
        headers={
            "Origin": "http://localhost:4321",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:4321"
