"""Административные действия владельца: агенты, ключи, очистка сигналов.

Запуск: python -m app.admin <команда> ...
"""

import argparse
import sys

from sqlalchemy.orm import Session

from app.agent.http import HttpFetcher
from app.agent.run import publish_draft, run_cycle
from app.agent.sources import SourcesError, load_sources
from app.agent.writer import LlmWriter
from app.config import Settings
from app.db import create_engine_for
from app.models import AgentRun, FeedSourceState, News, NewsStatus
from app.service import agents as agents_service
from app.service import rate_limit


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="app.admin", description="Действия владельца над агентами")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create-agent", help="зарегистрировать внешнего агента и выдать ключ")
    create.add_argument("name")
    create.add_argument("--description", default=None)

    revoke = subparsers.add_parser("revoke-token", help="отозвать ключ агента")
    revoke.add_argument("token")

    disable = subparsers.add_parser("disable-agent", help="запретить агенту новые комментарии")
    disable.add_argument("name")

    subparsers.add_parser("purge-signals", help="удалить устаревшие сигналы частоты")

    subparsers.add_parser("agent-run", help="выполнить один цикл сбора новостей")
    subparsers.add_parser("agent-status", help="показать настройки, источники и последние запуски")

    publish = subparsers.add_parser("agent-publish", help="опубликовать черновик агента")
    publish.add_argument("slug")

    hide = subparsers.add_parser("agent-hide", help="скрыть новость")
    hide.add_argument("slug")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    settings = Settings()
    engine = create_engine_for(settings.database_url)

    with Session(engine) as session:
        if arguments.command == "create-agent":
            agent, token = agents_service.create_agent(
                session, settings, name=arguments.name, description=arguments.description
            )
            print(f"агент создан: {agent.name}")
            print(f"ключ (показывается один раз): {token}")
        elif arguments.command == "revoke-token":
            agents_service.revoke_token(session, settings, arguments.token)
            print("ключ отозван")
        elif arguments.command == "disable-agent":
            agent = agents_service.disable_agent(session, arguments.name)
            print(f"агент отключён: {agent.name}")
        elif arguments.command == "purge-signals":
            removed = rate_limit.purge(session, ttl_hours=settings.rate_event_ttl_hours)
            print(f"удалено сигналов: {removed}")
        elif arguments.command == "agent-run":
            writer = LlmWriter(
                base_url=settings.llm_base_url,
                model=settings.llm_model,
                api_key=settings.llm_api_key,
                timeout=float(settings.llm_timeout_seconds),
            )
            try:
                report = run_cycle(session, settings, fetcher=HttpFetcher(), writer=writer)
            except SourcesError as error:
                print(f"источники: {error}")
                return 2
            print(report.as_line())
            for line in report.skipped:
                print(f"  пропущено: {line}")
        elif arguments.command == "agent-status":
            print(f"агент: {'включён' if settings.news_agent_enabled else 'выключен'}")
            print(f"авто-публикация: {'да' if settings.news_auto_publish else 'нет'}")
            print(f"лимиты: {settings.news_daily_limit} в сутки, {settings.news_topic_daily_limit} на тему")
            try:
                configured = load_sources(settings.news_sources_path)
            except SourcesError as error:
                print(f"источники: {error}")
                configured = []
            for source in configured:
                state = session.get(FeedSourceState, source.key)
                status = "не опрашивался" if state is None else (
                    f"ошибок {state.consecutive_errors}, последний успех {state.last_ok_at}"
                )
                print(f"  {source.key}: {source.topic}, {status}")
            drafts = session.query(News).filter(News.status == NewsStatus.draft).count()
            print(f"черновиков: {drafts}")
            runs = session.query(AgentRun).order_by(AgentRun.started_at.desc()).limit(5).all()
            for run in runs:
                print(
                    f"  запуск {run.started_at:%Y-%m-%d %H:%M}: источников {run.sources_polled}, "
                    f"записей {run.items_received}, черновиков {run.items_drafted}, "
                    f"опубликовано {run.items_published}, ошибка {run.error or '-'}"
                )
        elif arguments.command == "agent-publish":
            news = publish_draft(session, arguments.slug)
            print(f"опубликовано: {news.slug}")
        elif arguments.command == "agent-hide":
            news = session.query(News).filter(News.slug == arguments.slug).one_or_none()
            if news is None:
                print("новость не найдена")
                return 2
            news.status = NewsStatus.hidden
            session.commit()
            print(f"скрыто: {news.slug}")
        else:  # pragma: no cover - защита от опечатки в названии команды
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
