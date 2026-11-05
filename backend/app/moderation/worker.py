"""Цикл модерации. Запускается отдельной службой рядом с API."""

import logging
import time

from sqlalchemy.orm import Session

from app.config import Settings
from app.db import create_engine_for
from app.moderation.policy import AlwaysUndecided, Moderator
from app.moderation.queue import process_batch

log = logging.getLogger("moderation")


def build_moderator(settings: Settings) -> Moderator:
    """Точка расширения: рабочая проверка подключается отдельной спецификацией.

    Пока ничего не одобряет, чтобы случайная настройка не публиковала текст.
    """
    return AlwaysUndecided()


def run(settings: Settings, *, interval_seconds: int = 20, batch: int = 20) -> None:
    engine = create_engine_for(settings.database_url)
    moderator = build_moderator(settings)
    while True:
        with Session(engine) as session:
            handled = process_batch(session, settings, moderator, limit=batch)
        if handled:
            log.info("обработано комментариев: %s", handled)
            continue
        time.sleep(interval_seconds)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run(Settings())
