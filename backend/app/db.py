"""Движок базы данных."""

from sqlalchemy import Engine, create_engine


def create_engine_for(database_url: str) -> Engine:
    """Создаёт движок. Для SQLite в тестах нужен общий доступ между потоками."""
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(database_url, pool_pre_ping=True, future=True, connect_args=connect_args)
