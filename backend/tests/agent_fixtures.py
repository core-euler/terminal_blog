"""Стенд агента новостей: записанные ответы источников и заглушка модели."""

from datetime import datetime, timezone

import pytest

from app.agent.http import FetchError, FetchResult
from app.agent.sources import Source
from app.agent.writer import DraftedNews, Writer, WriterError
from app.config import Settings

FIXTURES = __import__("pathlib").Path(__file__).parent / "fixtures"
NOW = datetime(2026, 3, 4, 12, 0, tzinfo=timezone.utc)


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


class FakeFetcher:
    """Отдаёт заранее записанные ответы. Последний ответ повторяется."""

    def __init__(self, routes: dict[str, list[object]]) -> None:
        self.routes = routes
        self.calls: list[tuple[str, str | None, str | None]] = []

    def get(self, url: str, *, etag: str | None = None, last_modified: str | None = None) -> FetchResult:
        self.calls.append((url, etag, last_modified))
        queue = self.routes.get(url)
        if not queue:
            raise FetchError("нет записанного ответа")
        answer = queue[0] if len(queue) == 1 else queue.pop(0)
        if isinstance(answer, Exception):
            raise answer
        assert isinstance(answer, FetchResult)
        return answer

    def polled(self, url: str) -> int:
        return sum(1 for call in self.calls if call[0] == url)


class StubWriter(Writer):
    def __init__(self, title: str = "PostgreSQL 18 вышел с асинхронным вводом-выводом", body: str | None = None,
                 error: Exception | None = None) -> None:
        self.title = title
        self.body = body or (
            "PostgreSQL 18 выпущен 4 марта. Асинхронный ввод-вывод включён по умолчанию.\n\n"
            "VACUUM больше не сканирует индексы целиком. Заявлено ускорение аналитических запросов на 40 процентов."
        )
        self.error = error
        self.requests: list[dict[str, str]] = []

    def write(self, *, title: str, url: str, page_text: str, topic: str) -> DraftedNews:
        self.requests.append({"title": title, "url": url, "topic": topic, "chars": str(len(page_text))})
        if self.error is not None:
            raise self.error
        return DraftedNews(title=self.title, body=self.body)


@pytest.fixture
def agent_settings(settings: Settings) -> Settings:
    return settings.model_copy(
        update={
            "news_min_source_chars": 60,
            "news_min_summary_chars": 80,
            "news_daily_limit": 5,
            "news_topic_daily_limit": 2,
            "news_auto_publish": False,
            "news_agent_enabled": True,
            "news_item_max_age_hours": 72,
        }
    )


def make_source(key: str = "alpha", **overrides) -> Source:
    values = {
        "key": key,
        "title": key.title(),
        "url": f"https://{key}.example/feed",
        "topic": "databases",
        "lang": "en",
        "priority": 2,
        "poll_minutes": 30,
        "enabled": True,
    }
    values.update(overrides)
    return Source(**values)
