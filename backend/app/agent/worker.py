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

INTERVAL_SECONDS = 30 * 60


def run_forever(settings: Settings, *, interval_seconds: int = INTERVAL_SECONDS) -> None:
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
        time.sleep(interval_seconds)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run_forever(Settings())
