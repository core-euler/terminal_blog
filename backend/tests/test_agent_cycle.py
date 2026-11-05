"""Полный цикл агента: от ленты до черновика или публикации."""

import pytest
from agent_fixtures import NOW, FakeFetcher, StubWriter, fixture, make_source

from app.agent import run as agent
from app.agent.http import FetchError, FetchResult
from app.agent.sources import parse_sources
from app.agent.writer import WriterError
from app.models import (
    AgentRun,
    FeedItem,
    FeedItemStatus,
    FeedSourceState,
    News,
    NewsStatus,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session

PAGE = "https://alpha.example/news/postgres-18"
BETA_PAGE = "https://beta.example/posts/pg18"


def _fetcher(*, alpha_etag: str | None = "v1", extra_page: bool = True) -> FakeFetcher:
    routes: dict[str, list[object]] = {
        "https://alpha.example/feed": [FetchResult(200, fixture("feed_alpha.xml"), alpha_etag)],
        "https://beta.example/feed": [FetchResult(200, fixture("feed_beta.xml"), "b1")],
        PAGE: [FetchResult(200, fixture("page_postgres.html"))],
        BETA_PAGE: [FetchResult(200, fixture("page_postgres.html"))],
    }
    if not extra_page:
        routes[PAGE] = [FetchError("ответ 404")]
    return FakeFetcher(routes)


def _cycle(db: Session, settings, *, fetcher, writer, sources=None):
    return agent.run_cycle(
        db,
        settings,
        fetcher=fetcher,
        writer=writer,
        sources=sources or [make_source(), make_source("beta")],
        now=NOW,
    )


def test_cycle_creates_draft_from_feed(db: Session, agent_settings):
    writer = StubWriter()

    report = _cycle(db, agent_settings, fetcher=_fetcher(), writer=writer, sources=[make_source()])

    news = db.scalar(select(News))
    assert news is not None
    assert news.status is NewsStatus.draft
    assert news.published_at is None
    assert news.topic == "databases"
    assert [source.url for source in news.sources] == ["https://alpha.example/news/postgres-18"]
    assert report.drafted == 1 and report.published == 0


def test_draft_is_invisible_in_public_list_and_readable_by_slug(client, db: Session, agent_settings):
    _cycle(db, agent_settings, fetcher=_fetcher(), writer=StubWriter(), sources=[make_source()])

    news = db.scalar(select(News))
    assert client.get("/api/news").json()["items"] == []

    agent.publish_draft(db, news.slug)
    assert [item["slug"] for item in client.get("/api/news").json()["items"]] == [news.slug]


def test_second_cycle_does_not_duplicate_news(db: Session, agent_settings):
    fetcher = _fetcher()
    _cycle(db, agent_settings, fetcher=fetcher, writer=StubWriter(), sources=[make_source()])
    _cycle(db, agent_settings, fetcher=fetcher, writer=StubWriter(), sources=[make_source()])

    assert db.scalar(select(func.count()).select_from(News)) == 1


def test_conditional_request_sends_etag(db: Session, agent_settings):
    fetcher = _fetcher()
    _cycle(db, agent_settings, fetcher=fetcher, writer=StubWriter(), sources=[make_source()])
    agent.run_cycle(
        db,
        agent_settings,
        fetcher=fetcher,
        writer=StubWriter(),
        sources=[make_source()],
        now=NOW.replace(minute=45),
    )

    etags = [etag for url, etag, _ in fetcher.calls if url == "https://alpha.example/feed"]
    assert etags[0] is None
    assert etags[-1] == "v1"


def test_not_modified_does_not_create_items(db: Session, agent_settings):
    routes = {
        "https://alpha.example/feed": [FetchResult(200, fixture("feed_alpha.xml"), "v1"), FetchResult(304)],
        PAGE: [FetchResult(200, fixture("page_postgres.html"))],
    }
    fetcher = FakeFetcher(routes)
    _cycle(db, agent_settings, fetcher=fetcher, writer=StubWriter(), sources=[make_source()])
    before = db.scalar(select(func.count()).select_from(FeedItem))

    _cycle(db, agent_settings, fetcher=fetcher, writer=StubWriter(), sources=[make_source()])

    assert db.scalar(select(func.count()).select_from(FeedItem)) == before


def test_same_event_from_two_sources_gives_one_news_with_two_links(db: Session, agent_settings):
    limited = agent_settings.model_copy(update={"news_topic_daily_limit": 10, "news_daily_limit": 10})

    _cycle(db, limited, fetcher=_fetcher(), writer=StubWriter())

    with_postgres = [row for row in db.scalars(select(News)) if "PostgreSQL 18" in row.title]
    assert len(with_postgres) == 1
    assert {source.url for source in with_postgres[0].sources} == {
        "https://alpha.example/news/postgres-18",
        "https://beta.example/posts/pg18",
    }


def test_failed_page_fetch_does_not_create_news(db: Session, agent_settings):
    fetcher = _fetcher(extra_page=False)

    report = _cycle(db, agent_settings, fetcher=fetcher, writer=StubWriter(), sources=[make_source()])

    assert report.drafted == 0
    assert db.scalar(select(func.count()).select_from(News)) == 0
    item = db.scalar(select(FeedItem).where(FeedItem.title.like("PostgreSQL%")))
    assert item.attempts == 1
    assert item.status is FeedItemStatus.new


def test_short_page_does_not_create_news(db: Session, agent_settings):
    fetcher = _fetcher()
    fetcher.routes[PAGE] = [FetchResult(200, fixture("page_short.html"))]

    _cycle(db, agent_settings, fetcher=fetcher, writer=StubWriter(), sources=[make_source()])

    assert db.scalar(select(func.count()).select_from(News)) == 0


def test_writer_error_keeps_material_for_retry(db: Session, agent_settings):
    writer = StubWriter(error=WriterError("модель недоступна"))

    report = _cycle(db, agent_settings, fetcher=_fetcher(), writer=writer, sources=[make_source()])

    assert report.drafted == 0
    assert db.scalar(select(func.count()).select_from(News)) == 0
    item = db.scalar(select(FeedItem).where(FeedItem.title.like("PostgreSQL%")))
    assert item.status is FeedItemStatus.new
    assert item.attempts == 1
    assert "модель" in (item.last_error or "")


def test_old_material_is_skipped(db: Session, agent_settings):
    tight = agent_settings.model_copy(update={"news_item_max_age_hours": 1})

    _cycle(db, tight, fetcher=_fetcher(), writer=StubWriter(), sources=[make_source()])

    item = db.scalar(select(FeedItem).where(FeedItem.title.like("PostgreSQL%")))
    assert item.status is FeedItemStatus.skipped
    assert item.skip_reason == "старое"


def test_digest_is_skipped(db: Session, agent_settings):
    _cycle(db, agent_settings, fetcher=_fetcher(), writer=StubWriter(), sources=[make_source()])

    digest = db.scalar(select(FeedItem).where(FeedItem.title.like("Weekly%")))
    assert digest.status is FeedItemStatus.skipped
    assert digest.skip_reason == "подборка"


def test_foreign_topic_is_skipped(db: Session, agent_settings):
    narrow = agent_settings.model_copy(update={"news_allowed_topics": ["ai"]})

    _cycle(db, narrow, fetcher=_fetcher(), writer=StubWriter(), sources=[make_source()])

    item = db.scalar(select(FeedItem).where(FeedItem.title.like("PostgreSQL%")))
    assert item.status is FeedItemStatus.skipped
    assert item.skip_reason == "тема"
    assert db.scalar(select(func.count()).select_from(News)) == 0


def test_daily_limit_stops_publication(db: Session, agent_settings):
    limited = agent_settings.model_copy(update={"news_daily_limit": 1})

    _cycle(db, limited, fetcher=_fetcher(), writer=StubWriter())

    assert db.scalar(select(func.count()).select_from(News)) == 1


def test_topic_limit_stops_publication(db: Session, agent_settings):
    limited = agent_settings.model_copy(update={"news_topic_daily_limit": 1, "news_daily_limit": 5})

    _cycle(db, limited, fetcher=_fetcher(), writer=StubWriter())

    assert db.scalar(select(func.count()).select_from(News)) == 1


def test_auto_publish_creates_visible_news(db: Session, agent_settings):
    publishing = agent_settings.model_copy(update={"news_auto_publish": True})

    report = _cycle(db, publishing, fetcher=_fetcher(), writer=StubWriter(), sources=[make_source()])

    news = db.scalar(select(News))
    assert news.status is NewsStatus.published
    assert news.published_at is not None
    assert report.published == 1


def test_run_journal_records_result(db: Session, agent_settings):
    _cycle(db, agent_settings, fetcher=_fetcher(), writer=StubWriter(), sources=[make_source()])

    run = db.scalar(select(AgentRun))
    assert run.sources_polled == 1
    assert run.items_received == 2
    assert run.items_drafted == 1
    assert run.finished_at is not None
    assert run.error is None


def test_three_errors_pause_the_source(db: Session, agent_settings):
    routes = {"https://alpha.example/feed": [FetchError("ответ 500")]}
    fetcher = FakeFetcher(routes)

    for shift in range(3):
        moment = NOW.replace(hour=12 + shift)
        agent.run_cycle(
            db, agent_settings, fetcher=fetcher, writer=StubWriter(), sources=[make_source()], now=moment
        )

    state = db.get(FeedSourceState, "alpha")
    assert state is not None and state.paused_until is not None
    calls_before = fetcher.polled("https://alpha.example/feed")

    agent.run_cycle(
        db, agent_settings, fetcher=fetcher, writer=StubWriter(), sources=[make_source()], now=NOW.replace(hour=14, minute=30)
    )
    assert fetcher.polled("https://alpha.example/feed") == calls_before
    assert state.consecutive_errors >= agent.PAUSE_AFTER_ERRORS


def test_broken_source_does_not_block_others(db: Session, agent_settings):
    fetcher = _fetcher()
    fetcher.routes["https://alpha.example/feed"] = [FetchError("сеть")]

    report = _cycle(db, agent_settings, fetcher=fetcher, writer=StubWriter())

    assert report.sources_polled == 2
    assert report.drafted == 1


def test_disabled_source_is_not_polled(db: Session, agent_settings):
    fetcher = _fetcher()

    agent.run_cycle(
        db,
        agent_settings,
        fetcher=fetcher,
        writer=StubWriter(),
        sources=[make_source(enabled=False)],
        now=NOW,
    )

    assert fetcher.polled("https://alpha.example/feed") == 0


def test_disabled_agent_stops_everything(db: Session, agent_settings):
    stopped = agent_settings.model_copy(update={"news_agent_enabled": False})
    fetcher = _fetcher()

    with pytest.raises(agent.AgentDisabled):
        _cycle(db, stopped, fetcher=fetcher, writer=StubWriter())

    assert fetcher.calls == []
    assert db.scalar(select(func.count()).select_from(News)) == 0


def test_second_cycle_is_refused_while_lock_is_held(db: Session, agent_settings):
    assert agent.acquire(db, agent.LOCK_NAME, "first", now=NOW) is True
    fetcher = _fetcher()

    with pytest.raises(agent.CycleBusy):
        agent.run_cycle(
            db, agent_settings, fetcher=fetcher, writer=StubWriter(), sources=[make_source()], now=NOW
        )

    assert fetcher.calls == []
    agent.release(db, agent.LOCK_NAME, "first")
    assert agent.acquire(db, agent.LOCK_NAME, "second", now=NOW) is True


def test_repeated_title_gets_unique_slug(db: Session, agent_settings):
    _cycle(db, agent_settings, fetcher=_fetcher(), writer=StubWriter(), sources=[make_source()])
    second = db.scalar(select(FeedItem).where(FeedItem.title.like("Hacker News%")))
    assert second is None or second.status is FeedItemStatus.new


def test_config_with_bad_url_stops_the_cycle(db: Session, agent_settings):
    with pytest.raises(Exception) as error:
        parse_sources({"sources": [{"key": "bad", "url": "not-a-url", "topic": "dev"}]})

    assert "not-a-url" in str(error.value)


def test_empty_config_is_rejected():
    with pytest.raises(Exception) as error:
        parse_sources({"sources": []})

    assert "источник" in str(error.value)
