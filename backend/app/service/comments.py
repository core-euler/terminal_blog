"""Приём и чтение комментариев."""

import sqlalchemy as sa
from sqlalchemy.orm import Session, selectinload

from app.config import Settings
from app.errors import InvalidPayload, NotFound
from app.models import AuthorKind, Comment, CommentStatus, News, NewsStatus
from app.security import hash_secret
from app.service import agents as agents_service
from app.service import rate_limit


def _clean_name(raw: str | None, settings: Settings) -> str | None:
    if raw is None:
        return None
    name = raw.strip()
    if not name:
        return None
    if len(name) > settings.name_max_length:
        raise InvalidPayload("слишком длинное имя")
    return name


def _clean_text(raw: str, settings: Settings) -> str:
    text = (raw or "").strip()
    if not text:
        raise InvalidPayload("пустой комментарий")
    if len(text) > settings.comment_max_length:
        raise InvalidPayload("слишком длинный комментарий")
    return text


def create_comment(
    session: Session,
    settings: Settings,
    *,
    slug: str,
    text: str,
    name: str | None,
    agent_token: str | None,
    client_ip: str | None,
) -> Comment:
    """Принимает комментарий и оставляет его в ожидании проверки."""
    news = session.scalar(sa.select(News).where(News.slug == slug))
    if news is None or news.status is not NewsStatus.published:
        raise NotFound("новость не найдена")

    cleaned_text = _clean_text(text, settings)
    cleaned_name = _clean_name(name, settings)

    agent = None
    if agent_token:
        agent = agents_service.authenticate(session, settings, agent_token)

    # Люди ограничены по адресу, агенты — по своему ключу: квоты не пересекаются.
    if agent is None:
        rate_limit.consume(
            session,
            actor_hash=hash_secret(client_ip or "unknown", settings.hash_pepper),
            kind="comment_ip",
            limit=settings.comment_rate_limit,
            window_seconds=settings.comment_rate_window_seconds,
        )
    else:
        rate_limit.consume(
            session,
            actor_hash=hash_secret(str(agent.id), settings.hash_pepper),
            kind="comment_agent",
            limit=settings.agent_rate_limit,
            window_seconds=settings.agent_rate_window_seconds,
        )

    comment = Comment(
        news_id=news.id,
        kind=AuthorKind.agent if agent is not None else AuthorKind.human,
        display_name=None if agent is not None else cleaned_name,
        agent_id=agent.id if agent is not None else None,
        text=cleaned_text,
        status=CommentStatus.pending,
    )
    session.add(comment)
    session.commit()
    return comment


def list_approved(session: Session, *, slug: str, limit: int, offset: int) -> list[Comment]:
    """Одобренные комментарии к опубликованной новости."""
    news = session.scalar(sa.select(News).where(News.slug == slug))
    if news is None or news.status is not NewsStatus.published:
        raise NotFound("новость не найдена")
    stmt = (
        sa.select(Comment)
        .where(Comment.news_id == news.id, Comment.status == CommentStatus.approved)
        .options(selectinload(Comment.agent))
        .order_by(Comment.created_at.asc(), Comment.id.asc())
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(stmt))


def hide_news(session: Session, slug: str) -> News:
    news = session.scalar(sa.select(News).where(News.slug == slug))
    if news is None:
        raise NotFound("новость не найдена")
    news.status = NewsStatus.hidden
    session.commit()
    return news
