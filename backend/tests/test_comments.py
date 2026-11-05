"""Приём комментариев."""

from conftest import publish_news

from app.models import Comment, CommentStatus, News, NewsStatus
from sqlalchemy import select
from sqlalchemy.orm import Session


def test_comment_is_pending_and_hidden(client):
    publish_news(client, slug="c1", external_id="ext-c1")

    response = client.post("/api/news/c1/comments", json={"text": "  мысль  ", "name": "Николай"})

    assert response.status_code == 202
    assert response.json()["status"] == "pending"
    assert client.get("/api/news/c1/comments").json()["items"] == []


def test_empty_name_means_anonymous(client, db: Session):
    publish_news(client, slug="c2", external_id="ext-c2")

    client.post("/api/news/c2/comments", json={"text": "текст", "name": "   "})

    comment = db.scalar(select(Comment))
    assert comment.display_name is None


def test_text_is_trimmed(client, db: Session):
    publish_news(client, slug="c3", external_id="ext-c3")

    client.post("/api/news/c3/comments", json={"text": "   пробелы по краям   "})

    assert db.scalar(select(Comment)).text == "пробелы по краям"


def test_empty_text_is_rejected(client):
    publish_news(client, slug="c4", external_id="ext-c4")

    assert client.post("/api/news/c4/comments", json={"text": "   "}).status_code == 422


def test_too_long_text_and_name_are_rejected(client, settings):
    publish_news(client, slug="c5", external_id="ext-c5")

    long_text = "я" * (settings.comment_max_length + 1)
    long_name = "я" * (settings.name_max_length + 1)

    assert client.post("/api/news/c5/comments", json={"text": long_text}).status_code == 422
    assert client.post("/api/news/c5/comments", json={"text": "ок", "name": long_name}).status_code == 422


def test_comment_to_unknown_news_is_rejected(client):
    assert client.post("/api/news/net-takoy/comments", json={"text": "текст"}).status_code == 404


def test_comment_to_unpublished_news_is_rejected(client, db: Session):
    db.add(
        News(
            external_id="ext-hidden",
            slug="hidden-news",
            title="Скрытая",
            body="t",
            topic="ai",
            event_date="2026-01-01",
            status=NewsStatus.hidden,
        )
    )
    db.commit()

    assert client.post("/api/news/hidden-news/comments", json={"text": "текст"}).status_code == 404


def test_approved_comment_becomes_visible(client, db: Session):
    publish_news(client, slug="c6", external_id="ext-c6")
    client.post("/api/news/c6/comments", json={"text": "видимый", "name": "Николай"})

    comment = db.scalar(select(Comment))
    comment.status = CommentStatus.approved
    db.commit()

    items = client.get("/api/news/c6/comments").json()["items"]
    assert len(items) == 1
    assert items[0]["text"] == "видимый"
    assert items[0]["author"] == {"kind": "human", "name": "Николай"}


def test_comments_of_hidden_news_are_not_exposed(client, db: Session):
    publish_news(client, slug="c7", external_id="ext-c7")
    client.post("/api/news/c7/comments", json={"text": "текст"})
    comment = db.scalar(select(Comment))
    comment.status = CommentStatus.approved
    news = db.scalar(select(News).where(News.slug == "c7"))
    news.status = NewsStatus.hidden
    db.commit()

    assert client.get("/api/news/c7/comments").status_code == 404
