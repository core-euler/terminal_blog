"""Приём комментариев и чтение при выключенном бэке."""

import json

import httpx
import pytest

from app.backend import Backend
from app.sync import deliver_once

COMMENTS = "/api/news/novost/comments"
NEWS = "/api/news"


def _reply(status: int, body: dict):
    from conftest import Reply

    return Reply(status, body)


def test_comment_is_queued_when_backend_is_down(edge):
    edge.fake.down = True

    response = edge.post(COMMENTS, json={"text": "мысль", "client_id": "queue-0001"})

    assert response.status_code == 202
    assert response.json()["status"] == "queued"
    assert edge.store.count("pending") == 1


def test_comment_goes_to_backend_when_it_is_up(edge):
    edge.fake.down = False
    edge.fake.replies["POST " + COMMENTS] = _reply(202, {"id": "1", "status": "pending", "message": "принят"})

    response = edge.post(COMMENTS, json={"text": "мысль", "client_id": "direct-01"})

    assert response.status_code == 202
    assert response.json()["message"] == "принят"
    assert edge.store.count() == 0


def test_queue_survives_repeat_submission(edge):
    edge.fake.down = True

    edge.post(COMMENTS, json={"text": "мысль", "client_id": "queue-dup"})
    edge.post(COMMENTS, json={"text": "мысль", "client_id": "queue-dup"})

    assert edge.store.count("pending") == 1


def test_rejected_payload_is_not_queued(edge):
    edge.fake.down = False
    edge.fake.replies["POST " + COMMENTS] = _reply(422, {"detail": "пустой комментарий"})

    response = edge.post(COMMENTS, json={"text": " ", "client_id": "bad-00001"})

    assert response.status_code == 422
    assert edge.store.count() == 0


def test_read_is_cached_and_served_when_backend_dies(edge):
    edge.fake.down = False
    edge.fake.replies[NEWS] = _reply(200, {"items": [{"slug": "novost"}], "total": 1})

    first = edge.get(NEWS)
    assert first.status_code == 200 and first.headers["X-Edge"] == "backend"

    edge.fake.down = True
    second = edge.get(NEWS)

    assert second.status_code == 200
    assert second.headers["X-Edge"] == "stale"
    assert second.json()["items"][0]["slug"] == "novost"


def test_read_without_cache_and_without_backend_is_503(edge):
    edge.fake.down = True

    response = edge.get(NEWS)

    assert response.status_code == 503
    assert "недоступны" in response.json()["detail"]


def test_freshness_is_not_served_twice_by_default(edge, tmp_path):
    edge.fake.down = False
    edge.fake.replies[NEWS] = _reply(200, {"items": [], "total": 0})
    edge.get(NEWS)
    calls = len(edge.fake.received)

    edge.app.state.cache_seconds = 3600
    edge.get(NEWS)

    assert len(edge.fake.received) == calls


def test_delivery_sends_queue_with_idempotency_key(edge):
    edge.fake.down = True
    edge.post(COMMENTS, json={"text": "мысль", "client_id": "deliver-01"})
    edge.fake.down = False
    edge.fake.replies["POST " + COMMENTS] = _reply(202, {"id": "1", "status": "pending", "message": "принят"})

    result = deliver_once(edge.store, edge.app.state.backend)

    assert result["sent"] == 1
    assert edge.store.count("pending") == 0
    sent = [request for request in edge.fake.received if request.method == "POST"][-1]
    assert sent.headers["x-idempotency-key"] == "deliver-01"
    assert json.loads(sent.content)["text"] == "мысль"


def test_delivery_keeps_queue_on_network_error(edge):
    edge.fake.down = True
    edge.post(COMMENTS, json={"text": "мысль", "client_id": "retry-01"})

    result = deliver_once(edge.store, edge.app.state.backend)

    assert result["failed"] == 1
    assert edge.store.count("pending") == 1


def test_delivery_marks_rejected_comment_and_stops_retrying(edge):
    edge.fake.down = True
    edge.post(COMMENTS, json={"text": "мысль", "client_id": "reject-01"})
    edge.fake.down = False
    edge.fake.replies["POST " + COMMENTS] = _reply(422, {"detail": "новость не найдена"})

    deliver_once(edge.store, edge.app.state.backend)
    deliver_once(edge.store, edge.app.state.backend)

    assert edge.store.count("pending") == 0
    assert edge.store.count("rejected") == 1


def test_health_shows_queue(edge):
    edge.fake.down = True
    edge.post(COMMENTS, json={"text": "мысль", "client_id": "health-01"})

    body = edge.get("/api/health").json()

    assert body["queued"] == 1
