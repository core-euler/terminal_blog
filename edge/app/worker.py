"""Досылка очереди по расписанию."""

import logging
import time

from app.backend import Backend
from app.config import EdgeSettings
from app.store import Store
from app.sync import deliver_once

log = logging.getLogger("edge-worker")
INTERVAL_SECONDS = 30
COMPACT_EVERY = 120


def run_once(settings: EdgeSettings | None = None) -> dict[str, int]:
    config = settings or EdgeSettings()
    store = Store(config.db_path)
    backend = Backend(
        config.backend_url,
        timeout=config.timeout_seconds,
        accept_timeout=config.accept_timeout_seconds,
    )
    try:
        return deliver_once(store, backend)
    finally:
        store.close()


def run_forever(settings: EdgeSettings | None = None, *, interval_seconds: int = INTERVAL_SECONDS) -> None:
    config = settings or EdgeSettings()
    store = Store(config.db_path)
    backend = Backend(config.backend_url, timeout=config.timeout_seconds)
    ticks = 0
    try:
        while True:
            try:
                result = deliver_once(store, backend)
                if any(result.values()):
                    log.info("очередь: %s", result)
            except Exception as error:  # досылка не должна падать насовсем
                log.error("досылка упала: %s: %s", type(error).__name__, error)
            ticks += 1
            if ticks % COMPACT_EVERY == 0:
                removed = store.compact(retention_days=config.retention_days)
                if removed:
                    log.info("убрано из очереди старого: %s", removed)
            time.sleep(interval_seconds)
    finally:
        store.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run_forever()
