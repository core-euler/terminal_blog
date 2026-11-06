"""Написание и редактура новости по прочитанному источнику."""

import json
import re
from dataclasses import dataclass
from importlib.resources import files

import httpx

from app.agent.text import html_to_text

MAX_TITLE = 90
MAX_BODY = 4000
CYRILLIC = re.compile(r"[а-яё]", re.I)


class WriterError(Exception):
    """Текст не готов: материал остаётся для следующей попытки."""


class EditorialSkip(Exception):
    """Материал прочитан и отклонён редактором."""


@dataclass(frozen=True)
class DraftedNews:
    title: str
    body: str


class Writer:
    def write(self, *, title: str, url: str, page_text: str, topic: str) -> DraftedNews:
        raise NotImplementedError


def _clean(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise WriterError(f"не заполнено поле «{field}»")
    return html_to_text(value).strip() if "<" in value else value.strip()


def parse_answer(raw: str) -> DraftedNews:
    """Разбирает решение; ошибка формата не считается редакционным отказом."""
    if not isinstance(raw, str):
        raise WriterError("ответ не содержит текста")
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end <= start:
        raise WriterError("в ответе нет JSON-объекта")
    try:
        payload = json.loads(raw[start : end + 1])
    except json.JSONDecodeError as error:
        raise WriterError("ответ не разбирается как JSON") from error
    if not isinstance(payload, dict):
        raise WriterError("ожидался JSON-объект")
    decision = payload.get("decision", "write")
    if decision == "skip":
        raise EditorialSkip(_clean(payload.get("reason"), "reason")[:300])
    if decision != "write":
        raise WriterError("неизвестное решение редактора")
    title = _clean(payload.get("title"), "title")
    body = _clean(payload.get("body"), "body")
    if len(title) > MAX_TITLE:
        raise WriterError("заголовок длиннее допустимого")
    if len(body) > MAX_BODY:
        raise WriterError("текст новости длиннее допустимого")
    if not CYRILLIC.search(body):
        raise WriterError("текст не на русском")
    if "http://" in body or "https://" in body:
        raise WriterError("ссылки в тексте не нужны, они добавляются отдельно")
    return DraftedNews(title, body)


def editorial_prompt(stage: str) -> str:
    root = files("app.agent").joinpath("skills", "editorial")
    return "\n\n".join(
        root.joinpath(*path).read_text(encoding="utf-8")
        for path in [("SKILL.md",), ("references", "style.md"), ("prompts", f"{stage}.md")]
    )


class LlmWriter(Writer):
    def __init__(self, *, base_url: str, model: str, api_key: str, timeout: float = 60.0,
                 transport: httpx.BaseTransport | None = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._api_key = api_key
        self._timeout = timeout
        self._transport = transport

    def _request(self, stage: str, payload: dict) -> DraftedNews:
        try:
            with httpx.Client(timeout=self._timeout, transport=self._transport) as client:
                response = client.post(
                    f"{self._base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json={
                        "model": self._model,
                        "temperature": 0.4 if stage == "write" else 0.2,
                        "messages": [
                            {"role": "system", "content": editorial_prompt(stage)},
                            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
                        ],
                    },
                )
        except httpx.HTTPError as error:
            raise WriterError(f"сервис текстов недоступен: {type(error).__name__}") from error
        if response.status_code >= 400:
            raise WriterError(f"сервис текстов ответил {response.status_code}")
        try:
            content = response.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError, TypeError) as error:
            raise WriterError("неожиданный ответ сервиса текстов") from error
        return parse_answer(content)

    def write(self, *, title: str, url: str, page_text: str, topic: str) -> DraftedNews:
        if not self._api_key:
            raise WriterError("не задан ключ модели")
        source = {"title": title, "url": url, "source_topic": topic, "text": page_text[:16000]}
        drafted = self._request("write", {"source": source})
        return self._request("review", {
            "source": source, "draft": {"title": drafted.title, "body": drafted.body},
        })
