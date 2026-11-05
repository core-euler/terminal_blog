"""Ограничение частоты и сроки хранения сигналов."""

from datetime import datetime, timedelta, timezone

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.errors import RateLimited
from app.models import RateEvent


def _window_start(now: datetime, seconds: int) -> datetime:
    return now - timedelta(seconds=seconds)


def consume(
    session: Session,
    *,
    actor_hash: str,
    kind: str,
    limit: int,
    window_seconds: int,
    now: datetime | None = None,
) -> None:
    """Списывает одну попытку. Превышение лимита — отказ без записи события."""
    moment = now or datetime.now(timezone.utc)
    used = session.scalar(
        sa.select(sa.func.count())
        .select_from(RateEvent)
        .where(
            RateEvent.actor_hash == actor_hash,
            RateEvent.kind == kind,
            RateEvent.created_at >= _window_start(moment, window_seconds),
        )
    )
    if (used or 0) >= limit:
        raise RateLimited("слишком много попыток, попробуйте позже")
    session.add(RateEvent(actor_hash=actor_hash, kind=kind, created_at=moment))


def purge(session: Session, *, ttl_hours: int, now: datetime | None = None) -> int:
    """Удаляет устаревшие сигналы. Возвращает число удалённых записей."""
    moment = now or datetime.now(timezone.utc)
    threshold = moment - timedelta(hours=ttl_hours)
    result = session.execute(sa.delete(RateEvent).where(RateEvent.created_at < threshold))
    session.commit()
    return result.rowcount or 0
