"""Очередь модерации: захват, решение, повторные попытки."""

from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import Comment, CommentStatus, ModerationDecision, ModerationEvent
from app.moderation.policy import Decision, Moderator, Review


def claim_pending(session: Session, *, max_attempts: int) -> Comment | None:
    """Забирает один комментарий в обработку, увеличивая счётчик попыток."""
    candidate_id = session.scalar(
        sa.select(Comment.id)
        .where(Comment.status == CommentStatus.pending, Comment.attempts < max_attempts)
        .order_by(Comment.created_at.asc())
        .limit(1)
    )
    if candidate_id is None:
        return None

    updated = session.execute(
        sa.update(Comment)
        .where(
            Comment.id == candidate_id,
            Comment.status == CommentStatus.pending,
            Comment.attempts < max_attempts,
        )
        .values(attempts=Comment.attempts + 1)
    )
    session.commit()
    if not updated.rowcount:
        return None
    return session.get(Comment, candidate_id)


def record_decision(session: Session, comment: Comment, review: Review, *, rules_version: str) -> bool:
    """Применяет решение, если комментарий всё ещё ожидает проверки."""
    if review.decision is Decision.undecided:
        if review.reason:
            session.execute(
                sa.update(Comment).where(Comment.id == comment.id).values(last_error=review.reason[:300])
            )
            session.commit()
        return False

    target = CommentStatus.approved if review.decision is Decision.approved else CommentStatus.rejected
    updated = session.execute(
        sa.update(Comment)
        .where(Comment.id == comment.id, Comment.status == CommentStatus.pending)
        .values(status=target, decided_at=datetime.now(timezone.utc), last_error=None)
    )
    if not updated.rowcount:
        session.rollback()
        return False

    session.add(
        ModerationEvent(
            comment_id=comment.id,
            decision=ModerationDecision(target.value),
            reason=(review.reason or "")[:500],
            rules_version=(review.rules_version or rules_version)[:40],
        )
    )
    session.commit()
    return True


def process_once(session: Session, settings: Settings, moderator: Moderator) -> Comment | None:
    """Обрабатывает один комментарий. Ошибки модератора не публикуют текст."""
    comment = claim_pending(session, max_attempts=settings.moderation_max_attempts)
    if comment is None:
        return None
    try:
        review = moderator.review(comment.text)
    except Exception as error:  # модератор недоступен или вернул мусор
        session.rollback()
        session.execute(
            sa.update(Comment)
            .where(Comment.id == comment.id)
            .values(last_error=f"модератор: {type(error).__name__}"[:300])
        )
        session.commit()
        return comment
    record_decision(session, comment, review, rules_version=settings.rules_version)
    return session.get(Comment, comment.id)


def process_batch(session: Session, settings: Settings, moderator: Moderator, *, limit: int = 20) -> int:
    """Обрабатывает до указанного числа комментариев."""
    handled = 0
    while handled < limit:
        if process_once(session, settings, moderator) is None:
            break
        handled += 1
    return handled
