"""Публичное чтение новостей."""

from conftest import publish_news
from sqlalchemy.orm import Session

from app.models import News, NewsStatus


def test_public_list_shows_only_published(client, db: Session):
    assert publish_news(client, slug="a", external_id="ext-a").status_code == 201
    draft = News(external_id="ext-b", slug="b", title="Черновик", body="t", topic="ai", event_date="2026-02-01")
    hidden = News(
        external_id="ext-c",
        slug="c",
        title="Скрытая",
        body="t",
        topic="ai",
        event_date="2026-02-02",
        status=NewsStatus.hidden,
    )
    db.add_all([draft, hidden])
    db.commit()

    response = client.get("/api/news")

    assert response.status_code == 200
    assert [item["slug"] for item in response.json()["items"]] == ["a"]
    assert response.json()["total"] == 1


def test_draft_and_hidden_are_not_reachable_by_slug(client, db: Session):
    db.add(
        News(
            external_id="ext-d",
            slug="draft-one",
            title="Черновик",
            body="t",
            topic="ai",
            event_date="2026-02-01",
            status=NewsStatus.draft,
        )
    )
    db.commit()

    assert client.get("/api/news/draft-one").status_code == 404
    assert client.get("/api/news/net-takoy").status_code == 404


def test_list_is_ordered_and_paginated(client):
    for index in range(3):
        assert (
            publish_news(
                client,
                slug=f"n{index}",
                external_id=f"ext-{index}",
                event_date=f"2026-03-0{index + 1}",
            ).status_code
            == 201
        )

    first = client.get("/api/news", params={"limit": 2}).json()
    second = client.get("/api/news", params={"limit": 2, "offset": 2}).json()

    assert first["total"] == 3
    assert len(first["items"]) == 2
    assert len(second["items"]) == 1
    assert {item["slug"] for item in first["items"]} | {item["slug"] for item in second["items"]} == {
        "n0",
        "n1",
        "n2",
    }


def test_news_published_in_the_same_second_keep_a_stable_order(client, db: Session):
    from datetime import date, datetime, timezone

    moment = datetime(2026, 11, 6, 9, 0, 0, tzinfo=timezone.utc)
    for slug, event in (("old-event", date(2026, 10, 1)), ("new-event", date(2026, 11, 6))):
        db.add(
            News(
                external_id=f"ext-{slug}",
                slug=slug,
                title=slug,
                body="t",
                topic="ai",
                event_date=event,
                status=NewsStatus.published,
                published_at=moment,
                created_at=moment,
            )
        )
    db.commit()

    items = client.get("/api/news").json()["items"]

    assert [item["slug"] for item in items] == ["new-event", "old-event"]


def test_late_published_old_event_stays_below_fresh_news(client, db: Session):
    from datetime import date, datetime, timedelta, timezone

    moment = datetime(2026, 11, 6, 9, 0, 0, tzinfo=timezone.utc)
    db.add_all([
        News(external_id="ext-fresh", slug="fresh", title="fresh", body="t", topic="ai",
             event_date=date(2026, 11, 6), status=NewsStatus.published,
             published_at=moment - timedelta(days=1), created_at=moment - timedelta(days=1)),
        News(external_id="ext-late", slug="late", title="late", body="t", topic="ai",
             event_date=date(2026, 9, 1), status=NewsStatus.published,
             published_at=moment, created_at=moment),
    ])
    db.commit()

    items = client.get("/api/news").json()["items"]

    assert [item["slug"] for item in items] == ["fresh", "late"]


def test_published_news_exposes_sources(client):
    publish_news(client, slug="so-sources", external_id="ext-s")
    payload = client.get("/api/news/so-sources").json()

    assert payload["sources"][0]["url"] == "https://example.org/news"
    assert payload["published_at"] is not None
