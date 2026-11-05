"""Закрытая публикация новостей."""

from conftest import NEWS_TOKEN, make_agent, publish_news

from app.models import News
from sqlalchemy import select
from sqlalchemy.orm import Session


def test_publish_without_token_is_rejected(client):
    assert publish_news(client, token=None).status_code == 403


def test_publish_with_wrong_token_is_rejected(client):
    assert publish_news(client, token="not-the-token").status_code == 403


def test_publish_requires_a_source(client):
    assert publish_news(client, sources=[]).status_code == 422


def test_repeat_publish_does_not_duplicate(client, db: Session):
    first = publish_news(client, slug="dup", external_id="ext-dup")
    second = publish_news(client, slug="dup", external_id="ext-dup")

    assert first.status_code == 201
    assert second.status_code == 200
    assert db.scalar(select(News).where(News.external_id == "ext-dup")).id is not None
    assert len(list(db.scalars(select(News)))) == 1


def test_agent_key_cannot_publish_news(client, db: Session, settings):
    _, token = make_agent(db, settings)

    response = client.post(
        "/api/internal/news",
        json={
            "external_id": "ext-agent",
            "slug": "agent-news",
            "title": "Попытка агента",
            "body": "текст",
            "topic": "ai",
            "event_date": "2026-01-01",
            "sources": [{"url": "https://example.org/a", "title": None}],
        },
        headers={"X-News-Token": token},
    )

    assert response.status_code == 403


def test_published_news_appears_in_public_list(client):
    assert publish_news(client, slug="ok-news", external_id="ext-ok").status_code == 201

    assert client.get("/api/news/ok-news").status_code == 200
    assert NEWS_TOKEN
