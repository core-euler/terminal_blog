"""Правила модерации: интерфейс к проверяющему.

Текст промптов и модель сюда не входят: спецификация фиксирует только поведение.
"""

import enum
from dataclasses import dataclass
from typing import Protocol


class Decision(str, enum.Enum):
    approved = "approved"
    rejected = "rejected"
    undecided = "undecided"


@dataclass(frozen=True)
class Review:
    decision: Decision
    reason: str
    rules_version: str = ""


class Moderator(Protocol):
    def review(self, text: str) -> Review:
        """Оценивает текст комментария."""
        ...


class AlwaysUndecided:
    """Заглушка: ничего не публикует и не отклоняет."""

    def review(self, text: str) -> Review:
        return Review(decision=Decision.undecided, reason="модератор не настроен")


class KeywordModerator:
    """Простое правило для локальной проверки: запрещённые слова отклоняют текст.

    Настоящая проверка смысла и тематики появится отдельной спецификацией.
    """

    def __init__(self, blocked: tuple[str, ...], rules_version: str) -> None:
        self._blocked = tuple(word.lower() for word in blocked)
        self._rules_version = rules_version

    def review(self, text: str) -> Review:
        lowered = text.lower()
        for word in self._blocked:
            if word in lowered:
                return Review(
                    decision=Decision.rejected,
                    reason=f"запрещённое слово: {word}",
                    rules_version=self._rules_version,
                )
        return Review(decision=Decision.approved, reason="нет замечаний", rules_version=self._rules_version)
