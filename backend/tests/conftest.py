"""Общие приспособления для тестов.

Тесты идут против настоящего PostgreSQL, если он доступен: сначала берётся
TEST_DATABASE_URL, затем локальный сервер pgserver, и только потом SQLite.
"""

import os
import pathlib
from collections.abc import Iterator

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import Settings
from app.main import create_app
from app.models import Base
from app.service import agents as agents_service

pytest_plugins = ["agent_fixtures"]

NEWS_TOKEN = "news-token-for-tests"
PEPPER = "pepper-for-tests"


_PG_STATE: dict[str, object] = {}


def _pgserver_url() -> str | None:
    try:
        import platformdirs

        runtime = pathlib.Path(".tmp/rt")
        runtime.mkdir(parents=True, exist_ok=True)
        # На macOS песочница запрещает ~/Library/Caches; уводим путь во временный каталог.
        platformdirs.user_runtime_path = lambda *args, **kwargs: runtime
        import pgserver
    except Exception:
        return None

    data = pathlib.Path(".tmp/pgdata/data")
    data.mkdir(parents=True, exist_ok=True)
    server = pgserver.get_server(str(data))
    uri = server.get_uri()
    _PG_STATE["server"] = server
    return "postgresql+psycopg://" + uri[len("postgresql://") :]


@pytest.fixture(scope="session")
def database_url() -> Iterator[str]:
    url = os.environ.get("TEST_DATABASE_URL")
    if url:
        yield url
        return
    started = _pgserver_url()
    if started:
        yield started
        server = _PG_STATE.get("server")
        if server is not None:
            server.cleanup()  # type: ignore[union-attr]
        return
    file_path = pathlib.Path(".tmp/sqlite/test.db")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if file_path.exists():
        file_path.unlink()
    yield f"sqlite+pysqlite:///{file_path}"


@pytest.fixture(scope="session")
def settings(database_url: str) -> Settings:
    return Settings(
        database_url=database_url,
        news_agent_token=NEWS_TOKEN,
        hash_pepper=PEPPER,
        comment_rate_limit=3,
        comment_rate_window_seconds=600,
        agent_rate_limit=50,
        agent_rate_window_seconds=3600,
        rate_event_ttl_hours=24,
        moderation_max_attempts=2,
        rules_version="rules-test",
    )


def alembic_config(database_url: str) -> Config:
    root = pathlib.Path(__file__).resolve().parent.parent
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "migrations"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def drop_schema(engine) -> None:
    if engine.dialect.name == "postgresql":
        with engine.begin() as connection:
            connection.execute(sa.text("DROP SCHEMA public CASCADE"))
            connection.execute(sa.text("CREATE SCHEMA public"))
        return
    Base.metadata.drop_all(engine)
    with engine.begin() as connection:
        connection.execute(sa.text("DROP TABLE IF EXISTS alembic_version"))


@pytest.fixture(scope="session")
def engine(settings: Settings):
    engine = sa.create_engine(settings.database_url, pool_pre_ping=True, future=True)
    drop_schema(engine)
    command.upgrade(alembic_config(settings.database_url), "head")
    yield engine
    engine.dispose()


def _truncate(engine) -> None:
    table_names = ", ".join(f'"{table.name}"' for table in reversed(Base.metadata.sorted_tables))
    if engine.dialect.name == "postgresql":
        with engine.begin() as connection:
            connection.execute(sa.text(f"TRUNCATE {table_names} RESTART IDENTITY CASCADE"))
        return
    with engine.begin() as connection:
        connection.execute(sa.text("PRAGMA foreign_keys = OFF"))
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(sa.text(f'DELETE FROM "{table.name}"'))
        connection.execute(sa.text("PRAGMA foreign_keys = ON"))


@pytest.fixture
def db(engine) -> Iterator[Session]:
    _truncate(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def client(settings: Settings, engine) -> Iterator[TestClient]:
    _truncate(engine)
    application = create_app(settings)
    application.state.engine = engine
    with TestClient(application) as test_client:
        yield test_client


def publish_news(
    client: TestClient,
    *,
    slug: str = "pervaya-novost",
    external_id: str = "ext-1",
    title: str = "Квантовый компьютер побил рекорд",
    topic: str = "quantum",
    event_date: str = "2026-01-15",
    sources: list[dict] | None = None,
    token: str | None = NEWS_TOKEN,
):
    payload = {
        "external_id": external_id,
        "slug": slug,
        "title": title,
        "body": "Текст новости.",
        "topic": topic,
        "event_date": event_date,
        "sources": sources if sources is not None else [{"url": "https://example.org/news", "title": "Источник"}],
    }
    headers = {"X-News-Token": token} if token else {}
    return client.post("/api/internal/news", json=payload, headers=headers)


def make_agent(db: Session, settings: Settings, name: str = "agent-one") -> tuple[object, str]:
    agent, token = agents_service.create_agent(db, settings, name=name, description="внешний агент")
    return agent, token
