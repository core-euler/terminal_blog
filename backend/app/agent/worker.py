"""Расписание агента новостей: цикл по таймеру."""

import logging
import time

from sqlalchemy.orm import Session

from app.agent.http import HttpFetcher
from app.agent.run import AgentDisabled, CycleBusy, run_cycle
from app.agent.writer import LlmWriter
from app.config import Settings
from app.db import create_engine_for

log = logging.getLogger("news-agent")

def run_forever(settings: Settings, *, interval_seconds: int | None = None) -> None:
    interval = interval_seconds or settings.news_poll_minutes * 60
    engine = create_engine_for(settings.database_url)
    fetcher = HttpFetcher()
    writer = LlmWriter(
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        timeout=float(settings.llm_timeout_seconds),
    )
    while True:
        try:
            with Session(engine) as session:
                report = run_cycle(session, settings, fetcher=fetcher, writer=writer)
            log.info("цикл завершён: %s", report.as_line())
        except AgentDisabled:
            log.warning("агент выключен настройкой, ждём")
        except CycleBusy:
            log.info("предыдущий цикл ещё идёт")
        except Exception as error:  # один сбой не должен убивать расписание
            log.error("цикл упал: %s: %s", type(error).__name__, error)
        time.sleep(interval)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    settings = Settings()
    log.info("цикл каждые %s минут", settings.news_poll_minutes)
    run_forever(settings)
