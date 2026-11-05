"""Досылка очереди на домашний бэк."""

import json

import httpx

from app.backend import Backend
from app.store import Store

PERMANENT = {401, 403, 404, 409, 422}


def deliver_once(store: Store, backend: Backend, *, limit: int = 50) -> dict[str, int]:
    """Отправляет накопленное. Возвращает счётчики для журнала."""
    sent = rejected = failed = 0
    for row in store.pending(limit=limit):
        body = json.loads(row["body"])
        headers = json.loads(row["headers"])
        headers["x-idempotency-key"] = row["client_id"]
        try:
            status, text = backend.post(row["path"], body, headers)
        except httpx.HTTPError as error:
            store.failed(row["client_id"], f"сеть: {type(error).__name__}")
            failed += 1
            continue

        if status < 400:
            store.sent(row["client_id"])
            sent += 1
        elif status in PERMANENT:
            store.rejected(row["client_id"], f"{status}: {text[:200]}")
            rejected += 1
        else:
            store.failed(row["client_id"], f"{status}: {text[:200]}")
            failed += 1
    return {"sent": sent, "rejected": rejected, "failed": failed}
