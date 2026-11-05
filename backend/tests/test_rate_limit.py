"""Ограничение частоты и сроки хранения сигналов."""

from datetime import datetime, timedelta, timezone

from conftest import make_agent, publish_news

from app.models import RateEvent
from app.service import rate_limit
from sqlalchemy import func, select
from sqlalchemy.orm import Session


def test_ip_limit_blocks_extra_comments(client, db: Session, settings):
    publish_news(client, slug="r1", external_id="ext-r1")

    for index in range(settings.comment_rate_limit):
        assert client.post("/api/news/r1/comments", json={"text": f"текст {index}"}).status_code == 202

    blocked = client.post("/api/news/r1/comments", json={"text": "лишний"})
    assert blocked.status_code == 429
    assert db.scalar(select(func.count()).select_from(RateEvent)) == settings.comment_rate_limit


def test_agent_limit_is_separate_from_ip(client, db: Session, settings):
    publish_news(client, slug="r2", external_id="ext-r2")
    _, token = make_agent(db, settings)

    for index in range(settings.comment_rate_limit):
        assert client.post("/api/news/r2/comments", json={"text": f"t{index}"}).status_code == 202

    # Адрес исчерпан, но у агента своя квота.
    assert client.post("/api/news/r2/comments", json={"text": "агент"}, headers={"X-Agent-Key": token}).status_code == 202


def test_stale_rate_events_are_purged(db: Session, settings):
    old_moment = datetime.now(timezone.utc) - timedelta(hours=settings.rate_event_ttl_hours + 1)
    db.add(RateEvent(actor_hash="old", kind="comment_ip", created_at=old_moment))
    db.add(RateEvent(actor_hash="fresh", kind="comment_ip", created_at=datetime.now(timezone.utc)))
    db.commit()

    removed = rate_limit.purge(db, ttl_hours=settings.rate_event_ttl_hours)

    assert removed == 1
    assert db.scalar(select(func.count()).select_from(RateEvent)) == 1
