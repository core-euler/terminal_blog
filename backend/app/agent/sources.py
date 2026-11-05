"""Список источников: файл конфигурации и его проверка."""

import tomllib
from dataclasses import dataclass
from pathlib import Path


class SourcesError(Exception):
    """Конфигурация источников не годится: запуск не начинается."""


@dataclass(frozen=True)
class Source:
    key: str
    title: str
    url: str
    topic: str
    lang: str
    priority: int
    poll_minutes: int
    enabled: bool


DEFAULT_POLL_MINUTES = 30


def _require(entry: dict, field: str, where: str) -> object:
    if field not in entry or entry[field] in (None, ""):
        raise SourcesError(f"{where}: не заполнено поле «{field}»")
    return entry[field]


def parse_sources(payload: dict) -> list[Source]:
    """Проверяет описание источников и возвращает неизменяемый список."""
    entries = payload.get("sources")
    if not isinstance(entries, list) or not entries:
        raise SourcesError("в конфигурации нет ни одного источника")

    sources: list[Source] = []
    seen: set[str] = set()
    for index, entry in enumerate(entries, start=1):
        where = f"источник №{index}"
        if not isinstance(entry, dict):
            raise SourcesError(f"{where}: ожидается таблица с полями")

        key = str(_require(entry, "key", where)).strip()
        url = str(_require(entry, "url", where)).strip()
        topic = str(_require(entry, "topic", where)).strip()
        where = f"источник «{key}»"

        if not url.startswith(("http://", "https://")):
            raise SourcesError(f"{where}: адрес должен начинаться с http, получено «{url}»")
        if key in seen:
            raise SourcesError(f"{where}: ключ повторяется")
        if not topic:
            raise SourcesError(f"{where}: пустая тема")

        priority = int(entry.get("priority", 2))
        if priority not in (1, 2, 3):
            raise SourcesError(f"{where}: приоритет должен быть 1, 2 или 3")

        poll_minutes = int(entry.get("poll_minutes", DEFAULT_POLL_MINUTES))
        if poll_minutes < 5:
            raise SourcesError(f"{where}: интервал опроса меньше пяти минут")

        seen.add(key)
        sources.append(
            Source(
                key=key,
                title=str(entry.get("title", key)),
                url=url,
                topic=topic,
                lang=str(entry.get("lang", "en")),
                priority=priority,
                poll_minutes=poll_minutes,
                enabled=bool(entry.get("enabled", True)),
            )
        )
    return sources


def load_sources(path: str | Path) -> list[Source]:
    """Читает файл источников. Ошибка чтения или разбора останавливает запуск."""
    file = Path(path)
    if not file.exists():
        raise SourcesError(f"файл источников не найден: {file}")
    try:
        payload = tomllib.loads(file.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as error:
        raise SourcesError(f"файл источников не разбирается: {error}") from error
    return parse_sources(payload)


def topics(sources: list[Source]) -> set[str]:
    return {source.topic for source in sources}
