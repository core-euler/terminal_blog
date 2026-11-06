"""Цикл сбора новостей: опрос лент, отбор, написание текста, публикация."""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.agent.feeds import FeedParseError, parse_feed
from app.agent.http import Fetcher, FetchError
from app.agent.sources import Source, load_sources, topics
from app.agent.text import looks_like_digest, page_text, same_event, slugify, title_fingerprint
from app.agent.writer import DraftedNews, EditorialSkip, Writer, WriterError
from app.config import Settings
from app.models import (
    AgentLock,
    AgentRun,
    FeedItem,
    FeedItemStatus,
    FeedSourceState,
    News,
    NewsSource,
    NewsStatus,
)

LOCK_NAME = "news-agent"
LOCK_MINUTES = 30
PAUSE_AFTER_ERRORS = 3
PAUSE_MINUTES = 60
MAX_CANDIDATES = 200


class AgentDisabled(Exception):
    """Агент выключен владельцем."""


class CycleBusy(Exception):
    """Предыдущий цикл ещё не закончился."""


@dataclass
class CycleReport:
    sources_polled: int = 0
    items_received: int = 0
    items_selected: int = 0
    drafted: int = 0
    published: int = 0
    skipped: list[str] = field(default_factory=list)

    def as_line(self) -> str:
        return (
            f"источников {self.sources_polled}, записей {self.items_received}, "
            f"отобрано {self.items_selected}, черновиков {self.drafted}, опубликовано {self.published}"
        )


def _aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


def _state(session: Session, key: str, now: datetime) -> FeedSourceState:
    state = session.get(FeedSourceState, key)
    if state is None:
        state = FeedSourceState(key=key, updated_at=now)
        session.add(state)
        session.flush()
    return state


def _state_failure(state: FeedSourceState, message: str, now: datetime) -> None:
    state.consecutive_errors += 1
    state.last_error = message[:300]
    state.updated_at = now
    if state.consecutive_errors >= PAUSE_AFTER_ERRORS:
        state.paused_until = now + timedelta(minutes=PAUSE_MINUTES)


def acquire(session: Session, name: str, owner: str, *, now: datetime) -> bool:
    """Берёт замок цикла. Просроченный замок можно забрать."""
    lock = session.get(AgentLock, name)
    if lock is None:
        session.add(AgentLock(name=name, owner=owner, expires_at=now + timedelta(minutes=LOCK_MINUTES)))
        session.commit()
        return True
    expires_at = _aware(lock.expires_at)
    assert expires_at is not None
    if expires_at <= now:
        lock.owner = owner
        lock.expires_at = now + timedelta(minutes=LOCK_MINUTES)
        session.commit()
        return True
    return False


def release(session: Session, name: str, owner: str) -> None:
    session.execute(sa.delete(AgentLock).where(AgentLock.name == name, AgentLock.owner == owner))
    session.commit()


def poll_source(
    session: Session,
    source: Source,
    fetcher: Fetcher,
    *,
    now: datetime,
) -> tuple[int, str | None]:
    """Опрашивает один источник. Возвращает число новых записей и текст ошибки."""
    state = _state(session, source.key, now)

    paused_until = _aware(state.paused_until)
    if paused_until is not None and paused_until > now:
        session.commit()
        return 0, "пауза после ошибок"

    last_ok_at = _aware(state.last_ok_at)
    if last_ok_at is not None and now - last_ok_at < timedelta(minutes=source.poll_minutes):
        session.commit()
        return 0, None

    try:
        result = fetcher.get(source.url, etag=state.etag, last_modified=state.last_modified)
    except FetchError as error:
        _state_failure(state, str(error), now)
        session.commit()
        return 0, str(error)

    if result.unchanged:
        state.last_ok_at = now
        state.consecutive_errors = 0
        state.last_error = None
        state.updated_at = now
        session.commit()
        return 0, None

    try:
        items = parse_feed(result.body)
    except FeedParseError as error:
        _state_failure(state, str(error), now)
        session.commit()
        return 0, str(error)

    state.etag = result.etag
    state.last_modified = result.last_modified
    state.last_ok_at = now
    state.consecutive_errors = 0
    state.last_error = None
    state.updated_at = now

    received = 0
    for raw in items:
        exists = session.scalar(
            sa.select(FeedItem.id).where(
                FeedItem.source_key == source.key, FeedItem.external_id == raw.external_id
            )
        )
        if exists is not None:
            continue
        session.add(
            FeedItem(
                source_key=source.key,
                external_id=raw.external_id,
                url=raw.url,
                canonical_url=raw.canonical,
                title=raw.title,
                summary=raw.summary,
                fingerprint=title_fingerprint(raw.title),
                published_at=raw.published_at,
                seen_at=now,
                status=FeedItemStatus.new,
            )
        )
        received += 1
        session.flush()
    session.commit()
    return received, None


def _skip(session: Session, item: FeedItem, reason: str) -> None:
    item.status = FeedItemStatus.skipped
    item.skip_reason = reason
    session.commit()


def _fail(session: Session, item: FeedItem, message: str) -> None:
    item.attempts += 1
    item.last_error = message[:300]
    session.commit()


def _sibling(session: Session, item: FeedItem, *, now: datetime) -> FeedItem | None:
    """Ищет уже описанное событие среди свежих записей с готовой новостью."""
    recent = session.scalars(
        sa.select(FeedItem)
        .where(FeedItem.news_id.is_not(None))
        .order_by(FeedItem.seen_at.desc())
        .limit(300)
    )
    for candidate in recent:
        if candidate.id == item.id or candidate.source_key == item.source_key:
            continue
        if not same_event(item.title, candidate.title):
            continue
        first, second = _aware(candidate.published_at), _aware(item.published_at)
        if first is not None and second is not None and abs((first - second).days) > 1:
            continue
        return candidate
    return None


def _unique_slug(session: Session, title: str) -> str:
    base = slugify(title)
    candidate = base
    index = 2
    while session.scalar(sa.select(News.id).where(News.slug == candidate)) is not None:
        candidate = f"{base}-{index}"
        index += 1
    return candidate


def _used_today(session: Session, now: datetime) -> tuple[int, dict[str, int]]:
    day_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    rows = session.execute(
        sa.select(News.topic, sa.func.count())
        .where(News.created_at >= day_start, News.external_id.like("agent:%"))
        .group_by(News.topic)
    ).all()
    per_topic = {topic: count for topic, count in rows}
    return sum(per_topic.values()), per_topic


def _store(
    session: Session,
    settings: Settings,
    item: FeedItem,
    source: Source,
    drafted: DraftedNews,
    *,
    now: datetime,
) -> News:
    auto_publish = settings.news_auto_publish
    slug = _unique_slug(session, drafted.title)
    event_date = (_aware(item.published_at) or now).date()
    news = News(
        external_id=f"agent:{source.key}:{item.external_id}"[:200],
        slug=slug,
        title=drafted.title[:300],
        body=drafted.body,
        topic=source.topic,
        event_date=event_date,
        status=NewsStatus.published if auto_publish else NewsStatus.draft,
        published_at=now if auto_publish else None,
        created_at=now,
    )
    news.sources = [NewsSource(url=item.canonical_url, title=source.title)]
    session.add(news)
    session.flush()

    item.news_id = news.id
    item.status = FeedItemStatus.published if auto_publish else FeedItemStatus.drafted
    session.flush()
    return news


def _attach_sibling(session: Session, item: FeedItem, sibling: FeedItem, source: Source) -> None:
    """Событие уже описано: добавляем ссылку к готовой новости, второй не создаём."""
    if sibling.news_id is None:
        _skip(session, item, "дубликат")
        return
    news = session.get(News, sibling.news_id)
    if news is None:
        _skip(session, item, "дубликат")
        return
    known = {source_row.url.rstrip("/") for source_row in news.sources}
    if item.canonical_url.rstrip("/") not in known:
        news.sources.append(NewsSource(url=item.canonical_url, title=source.title))
    item.news_id = news.id
    item.status = sibling.status
    session.commit()


def run_cycle(
    session: Session,
    settings: Settings,
    *,
    fetcher: Fetcher,
    writer: Writer,
    sources: list[Source] | None = None,
    now: datetime | None = None,
) -> CycleReport:
    """Один полный цикл. Повтор после сбоя не создаёт дублей."""
    moment = now or datetime.now(timezone.utc)
    if not settings.news_agent_enabled:
        raise AgentDisabled("агент новостей выключен")

    owner = uuid.uuid4().hex
    if not acquire(session, LOCK_NAME, owner, now=moment):
        raise CycleBusy("предыдущий цикл ещё идёт")

    report = CycleReport()
    run = AgentRun(started_at=moment, details=None)
    session.add(run)
    session.commit()

    try:
        configured = sources if sources is not None else load_sources(settings.news_sources_path)
        allowed_topics = set(settings.news_allowed_topics) or topics(configured)
        enabled = [source for source in configured if source.enabled]

        for source in enabled:
            received, error = poll_source(session, source, fetcher, now=moment)
            report.sources_polled += 1
            report.items_received += received
            if error:
                report.skipped.append(f"{source.key}: {error}")

        by_key = {source.key: source for source in configured}
        candidates = list(
            session.scalars(
                sa.select(FeedItem)
                .where(FeedItem.status == FeedItemStatus.new)
                .order_by(FeedItem.published_at.desc().nullslast(), FeedItem.seen_at.desc())
                .limit(MAX_CANDIDATES)
            )
        )
        candidates.sort(key=lambda row: -by_key.get(row.source_key, enabled[0]).priority if row.source_key in by_key else 0)

        used_total, used_topic = _used_today(session, moment)
        age_limit = timedelta(hours=settings.news_item_max_age_hours)

        for item in candidates:
            source = by_key.get(item.source_key)
            if source is None:
                _skip(session, item, "источник убран")
                continue

            published_at = _aware(item.published_at)
            if published_at is not None and moment - published_at > age_limit:
                _skip(session, item, "старое")
                continue
            if looks_like_digest(item.title, item.summary):
                _skip(session, item, "подборка")
                continue
            if source.topic not in allowed_topics:
                _skip(session, item, "тема")
                continue
            if len(item.summary) < settings.news_min_summary_chars:
                _skip(session, item, "короткая аннотация")
                continue
            if used_total >= settings.news_daily_limit:
                break
            if used_topic.get(source.topic, 0) >= settings.news_topic_daily_limit:
                _skip(session, item, "лимит темы")
                continue

            sibling = _sibling(session, item, now=moment)
            if sibling is not None:
                _attach_sibling(session, item, sibling, source)
                continue

            try:
                page = fetcher.get(item.canonical_url)
            except FetchError as error:
                _fail(session, item, f"источник страницы: {error}")
                continue

            text = page_text(page.body)
            if len(text) < settings.news_min_source_chars:
                _fail(session, item, "первоисточник пуст или закрыт")
                continue

            try:
                drafted = writer.write(
                    title=item.title, url=item.canonical_url, page_text=text, topic=source.topic
                )
            except EditorialSkip as error:
                item.last_error = str(error)[:300]
                report.skipped.append(f"{item.source_key}: {error}")
                _skip(session, item, "редакционный отбор")
                continue
            except WriterError as error:
                _fail(session, item, f"текст: {error}")
                continue

            report.items_selected += 1
            news = _store(session, settings, item, source, drafted, now=moment)
            used_total += 1
            used_topic[source.topic] = used_topic.get(source.topic, 0) + 1
            if news.status is NewsStatus.published:
                report.published += 1
            else:
                report.drafted += 1
            session.commit()

        run.finished_at = datetime.now(timezone.utc)
        run.sources_polled = report.sources_polled
        run.items_received = report.items_received
        run.items_selected = report.items_selected
        run.items_drafted = report.drafted
        run.items_published = report.published
        run.details = json.dumps({"skipped": report.skipped}, ensure_ascii=False)[:4000]
        session.commit()
    except Exception as error:  # цикл падает целиком: итог всё равно должен остаться
        session.rollback()
        run.error = f"{type(error).__name__}: {error}"[:300]
        run.finished_at = datetime.now(timezone.utc)
        session.commit()
        raise
    finally:
        release(session, LOCK_NAME, owner)

    return report


def publish_draft(session: Session, slug: str, *, now: datetime | None = None) -> News:
    """Публикует черновик агента. Видимость меняет только владелец."""
    from app.errors import NotFound

    news = session.scalar(sa.select(News).where(News.slug == slug))
    if news is None:
        raise NotFound("новость не найдена")
    news.status = NewsStatus.published
    news.published_at = news.published_at or (now or datetime.now(timezone.utc))
    session.commit()
    return news
