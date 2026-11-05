"""Внешние агенты: ключи, авторство, отзыв."""

from conftest import make_agent, publish_news

from app.models import AgentToken, Comment, CommentStatus
from app.service import agents as agents_service
from sqlalchemy import select
from sqlalchemy.orm import Session


def test_valid_key_marks_comment_as_agent(client, db: Session, settings):
    publish_news(client, slug="a1", external_id="ext-a1")
    agent, token = make_agent(db, settings, name="scout")

    response = client.post("/api/news/a1/comments", json={"text": "сигнал"}, headers={"X-Agent-Key": token})

    assert response.status_code == 202
    comment = db.scalar(select(Comment))
    assert comment.kind.value == "agent"
    assert comment.agent_id == agent.id
    assert comment.display_name is None


def test_revoked_key_is_rejected_immediately(client, db: Session, settings):
    publish_news(client, slug="a2", external_id="ext-a2")
    _, token = make_agent(db, settings)
    agents_service.revoke_token(db, settings, token)

    response = client.post("/api/news/a2/comments", json={"text": "текст"}, headers={"X-Agent-Key": token})

    assert response.status_code == 403


def test_disabled_agent_is_rejected(client, db: Session, settings):
    publish_news(client, slug="a3", external_id="ext-a3")
    _, token = make_agent(db, settings, name="to-disable")
    agents_service.disable_agent(db, "to-disable")

    response = client.post("/api/news/a3/comments", json={"text": "текст"}, headers={"X-Agent-Key": token})

    assert response.status_code == 403


def test_wrong_key_is_rejected(client, db: Session):
    publish_news(client, slug="a4", external_id="ext-a4")

    response = client.post("/api/news/a4/comments", json={"text": "текст"}, headers={"X-Agent-Key": "garbage-token"})

    assert response.status_code == 403


def test_token_is_stored_hashed_only(db: Session, settings):
    make_agent(db, settings, name="hashed")

    tokens = db.scalars(select(AgentToken)).all()
    assert len(tokens) == 1
    assert len(tokens[0].token_hash) == 64
    assert "scout" not in tokens[0].token_hash


def test_agent_comment_shows_agent_name_when_approved(client, db: Session, settings):
    publish_news(client, slug="a5", external_id="ext-a5")
    _, token = make_agent(db, settings, name="scout")
    client.post("/api/news/a5/comments", json={"text": "сигнал"}, headers={"X-Agent-Key": token})

    comment = db.scalar(select(Comment))
    comment.status = CommentStatus.approved
    db.commit()

    items = client.get("/api/news/a5/comments").json()["items"]
    assert items[0]["author"] == {"kind": "agent", "name": "scout"}
