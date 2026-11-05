"""Очередь модерации: решения, ошибки, повторы, идемпотентность."""

import pytest
from conftest import publish_news

from app.models import Comment, CommentStatus, ModerationEvent
from app.moderation import queue
from app.moderation.policy import Decision, Review
from sqlalchemy import func, select
from sqlalchemy.orm import Session


class ScriptedModerator:
    def __init__(self, review: Review | None = None, error: Exception | None = None) -> None:
        self._review = review
        self._error = error
        self.calls = 0

    def review(self, text: str) -> Review:
        self.calls += 1
        if self._error is not None:
            raise self._error
        assert self._review is not None
        return self._review


def _pending_comment(db: Session) -> Comment:
    return db.scalar(select(Comment))


def test_approval_publishes_comment(client, db: Session, settings):
    publish_news(client, slug="m1", external_id="ext-m1")
    client.post("/api/news/m1/comments", json={"text": "нормальный текст"})

    queue.process_once(db, settings, ScriptedModerator(Review(Decision.approved, "ок", "v1")))

    assert _pending_comment(db).status is CommentStatus.approved
    assert len(client.get("/api/news/m1/comments").json()["items"]) == 1


def test_rejection_keeps_comment_hidden(client, db: Session, settings):
    publish_news(client, slug="m2", external_id="ext-m2")
    client.post("/api/news/m2/comments", json={"text": "плохой текст"})

    queue.process_once(db, settings, ScriptedModerator(Review(Decision.rejected, "запрещено", "v1")))

    assert _pending_comment(db).status is CommentStatus.rejected
    assert client.get("/api/news/m2/comments").json()["items"] == []


def test_undecided_keeps_comment_pending(client, db: Session, settings):
    publish_news(client, slug="m3", external_id="ext-m3")
    client.post("/api/news/m3/comments", json={"text": "спорный"})

    queue.process_once(db, settings, ScriptedModerator(Review(Decision.undecided, "не уверен", "v1")))

    comment = _pending_comment(db)
    assert comment.status is CommentStatus.pending
    assert comment.attempts == 1
    assert client.get("/api/news/m3/comments").json()["items"] == []


def test_moderator_error_keeps_comment_pending_and_counts_attempt(client, db: Session, settings):
    publish_news(client, slug="m4", external_id="ext-m4")
    client.post("/api/news/m4/comments", json={"text": "текст"})

    queue.process_once(db, settings, ScriptedModerator(error=RuntimeError("сеть")))

    comment = _pending_comment(db)
    assert comment.status is CommentStatus.pending
    assert comment.attempts == 1
    assert comment.last_error is not None


def test_attempts_are_capped(client, db: Session, settings):
    publish_news(client, slug="m5", external_id="ext-m5")
    client.post("/api/news/m5/comments", json={"text": "текст"})
    moderator = ScriptedModerator(error=RuntimeError("сеть"))

    for _ in range(settings.moderation_max_attempts + 2):
        queue.process_once(db, settings, moderator)

    comment = _pending_comment(db)
    assert comment.status is CommentStatus.pending
    assert comment.attempts == settings.moderation_max_attempts


def test_second_pass_does_not_duplicate_decision(client, db: Session, settings):
    publish_news(client, slug="m6", external_id="ext-m6")
    client.post("/api/news/m6/comments", json={"text": "текст"})
    moderator = ScriptedModerator(Review(Decision.approved, "ок", "v1"))

    queue.process_once(db, settings, moderator)
    queue.process_once(db, settings, moderator)

    assert db.scalar(select(func.count()).select_from(ModerationEvent)) == 1
    assert len(client.get("/api/news/m6/comments").json()["items"]) == 1


def test_decision_records_reason_and_rules_version(client, db: Session, settings):
    publish_news(client, slug="m7", external_id="ext-m7")
    client.post("/api/news/m7/comments", json={"text": "текст"})

    queue.process_once(db, settings, ScriptedModerator(Review(Decision.rejected, "политика", "rules-42")))

    event = db.scalar(select(ModerationEvent))
    assert event.decision.value == "rejected"
    assert event.reason == "политика"
    assert event.rules_version == "rules-42"


def test_batch_processes_all_pending(client, db: Session, settings):
    publish_news(client, slug="m8", external_id="ext-m8")
    for index in range(3):
        client.post("/api/news/m8/comments", json={"text": f"текст {index}"})

    handled = queue.process_batch(db, settings, ScriptedModerator(Review(Decision.approved, "ок", "v1")))

    assert handled == 3
    assert len(client.get("/api/news/m8/comments").json()["items"]) == 3
