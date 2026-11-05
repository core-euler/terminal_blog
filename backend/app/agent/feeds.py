"""Разбор лент RSS и Atom."""

import time
from dataclasses import dataclass
from datetime import datetime, timezone

import feedparser

from app.agent.text import canonical_url, html_to_text

MAX_ITEMS = 50


class FeedParseError(Exception):
    """Ответ не является лентой."""


@dataclass(frozen=True)
class RawItem:
    external_id: str
    url: str
    canonical: str
    title: str
    summary: str
    published_at: datetime | None


def _moment(entry: dict) -> datetime | None:
    for field in ("published_parsed", "updated_parsed", "created_parsed"):
        parsed = entry.get(field)
        if parsed:
            return datetime.fromtimestamp(time.mktime(parsed), tz=timezone.utc)
    return None


def _summary(entry: dict) -> str:
    parts = [entry.get("summary", "")]
    for block in entry.get("content", []) or []:
        parts.append(block.get("value", ""))
    return html_to_text("\n".join(part for part in parts if part))


def parse_feed(body: str, *, limit: int = MAX_ITEMS) -> list[RawItem]:
    """Читает ленту и отдаёт записи в порядке источника, не больше указанного числа."""
    parsed = feedparser.parse(body)
    entries = parsed.get("entries", [])
    if not entries:
        reason = parsed.get("bozo_exception")
        raise FeedParseError(f"в ответе нет записей: {type(reason).__name__}" if reason else "в ответе нет записей")

    items: list[RawItem] = []
    for entry in entries[:limit]:
        url = entry.get("link") or ""
        canonical = canonical_url(url)
        title = (entry.get("title") or "").strip()
        if canonical is None or not title:
            continue
        external_id = (entry.get("id") or canonical)[:400]
        items.append(
            RawItem(
                external_id=external_id,
                url=url.strip(),
                canonical=canonical,
                title=title[:500],
                summary=_summary(entry)[:20000],
                published_at=_moment(entry),
            )
        )
    if not items:
        raise FeedParseError("в ленте нет записей с адресом и заголовком")
    return items
