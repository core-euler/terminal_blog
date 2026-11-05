"""Административные действия владельца: агенты, ключи, очистка сигналов.

Запуск: python -m app.admin <команда> ...
"""

import argparse
import sys

from sqlalchemy.orm import Session

from app.config import Settings
from app.db import create_engine_for
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
        else:  # pragma: no cover - защита от опечатки в названии команды
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
