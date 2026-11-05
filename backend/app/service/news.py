"""Публикация и чтение новостей."""

from datetime import date, datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm import Session, selectinload

from app.config import Settings
from app.errors import Forbidden, InvalidPayload, NotFound
from app.models import News, NewsSource, NewsStatus
from app.security import secrets_equal


def check_news_token(settings: Settings, provided: str | None) -> None:
    """Публиковать новости может только агент владельца."""
    if not settings.news_agent_token:
        raise Forbidden("публикация новостей отключена")
    if not provided or not secrets_equal(provided, settings.news_agent_token):
        raise Forbidden("неверный секрет агента новостей")


def publish_news(
    session: Session,
    settings: Settings,
    *,
    external_id: str,
    slug: str,
    title: str,
    body: str,
    topic: str,
    event_date: date,
    sources: list[tuple[str, str | None]],
) -> tuple[News, bool]:
    """Публикует новость. Повтор с тем же внешним идентификатором возвращает прежнюю запись."""
    if not sources:
        raise InvalidPayload("нужен хотя бы один источник")

    existing = session.scalar(sa.select(News).where(News.external_id == external_id))
    if existing is not None:
        return existing, False

    if session.scalar(sa.select(News.id).where(News.slug == slug)) is not None:
        raise InvalidPayload("адрес новости уже занят")

    news = News(
        external_id=external_id,
        slug=slug,
        title=title,
        body=body,
        topic=topic,
        event_date=event_date,
        status=NewsStatus.published,
        published_at=datetime.now(timezone.utc),
    )
    news.sources = [NewsSource(url=url, title=source_title) for url, source_title in sources]
    session.add(news)
    session.commit()
    return news, True


def list_published(session: Session, *, limit: int, offset: int) -> list[News]:
    """Опубликованные новости в устойчивом порядке: свежие сверху."""
    stmt = (
        sa.select(News)
        .where(News.status == NewsStatus.published)
        .options(selectinload(News.sources))
        .order_by(News.published_at.desc(), News.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(stmt))


def count_published(session: Session) -> int:
    return session.scalar(sa.select(sa.func.count()).select_from(News).where(News.status == NewsStatus.published)) or 0


def get_published(session: Session, slug: str) -> News:
    """Опубликованная новость по адресу. Черновик и скрытая считаются отсутствующими."""
    news = session.scalar(
        sa.select(News).where(News.slug == slug).options(selectinload(News.sources))
    )
    if news is None or news.status is not NewsStatus.published:
        raise NotFound("новость не найдена")
    return news
