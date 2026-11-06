"""Написание текста новости по первоисточнику."""

import json
import re
from dataclasses import dataclass

import httpx

from app.agent.text import html_to_text

MAX_TITLE = 90
MAX_BODY = 4000

PROMPT = """Ты пишешь короткую новость для технического блога на русском языке.

Правила:
- пиши только по-русски, даже если материал на другом языке;
- только факты из материала ниже: числа, версии, даты, названия продуктов;
- никаких оценок, прогнозов, советов и рассуждений: запрещены обороты «важно отметить», «стоит отметить», «ключевое обновление», «это значит», «играет важную роль»;
- имена, названия продуктов и версии не переводятся;
- заголовок до 90 символов, без точки в конце;
- тело: лид на одно-два предложения, затем один или два коротких абзаца, абзацы разделяются пустой строкой;
- ссылки в тексте не нужны, они добавляются отдельно.

Ответ строго в виде JSON без пояснений: {"title": "...", "body": "..."}

Материал:
{text}
"""


class WriterError(Exception):
    """Текст не написан: материал не публикуется."""


@dataclass(frozen=True)
class DraftedNews:
    title: str
    body: str


class Writer:
    """Что нужно циклу от модели. В тестах подменяется заглушкой."""

    def write(self, *, title: str, url: str, page_text: str, topic: str) -> DraftedNews:
        raise NotImplementedError


def _clean(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise WriterError(f"модель не заполнила поле «{field}»")
    text = html_to_text(value).strip() if "<" in value else value.strip()
    return text


CYRILLIC = re.compile(r"[а-яё]", re.I)


def parse_answer(raw: str) -> DraftedNews:
    """Разбирает ответ модели: JSON с заголовком и телом."""
    start = raw.find("{")
    end = raw.rfind("}")
    if start < 0 or end <= start:
        raise WriterError("в ответе модели нет JSON")
    try:
        payload = json.loads(raw[start : end + 1])
    except json.JSONDecodeError as error:
        raise WriterError(f"ответ модели не разбирается: {error}") from error

    title = _clean(payload.get("title"), "title")
    body = _clean(payload.get("body"), "body")
    if len(title) > MAX_TITLE:
        raise WriterError("заголовок длиннее допустимого")
    if len(body) > MAX_BODY:
        raise WriterError("текст новости длиннее допустимого")
    if not CYRILLIC.search(f"{title} {body}"):
        raise WriterError("текст не на русском")
    if "http://" in body or "https://" in body:
        raise WriterError("ссылки в тексте не нужны, они добавляются отдельно")
    return DraftedNews(title=title, body=body)


class LlmWriter(Writer):
    """Пишет через совместимый с OpenAI HTTP-интерфейс."""

    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        api_key: str,
        timeout: float = 60.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._api_key = api_key
        self._timeout = timeout
        self._transport = transport

    def write(self, *, title: str, url: str, page_text: str, topic: str) -> DraftedNews:
        if not self._api_key:
            raise WriterError("не задан ключ модели")
        material = f"{title}\n{url}\n\n{page_text[:8000]}"
        # Подстановка буквальная: в подсказке есть фигурные скобки примера JSON.
        content = PROMPT.replace("{text}", material)
        try:
            with httpx.Client(timeout=self._timeout, transport=self._transport) as client:
                response = client.post(
                    f"{self._base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json={
                        "model": self._model,
                        "temperature": 0.2,
                        "messages": [{"role": "user", "content": content}],
                    },
                )
        except httpx.HTTPError as error:
            raise WriterError(f"модель недоступна: {type(error).__name__}") from error
        if response.status_code >= 400:
            raise WriterError(f"модель ответила {response.status_code}")
        try:
            content = response.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as error:
            raise WriterError("неожиданный ответ модели") from error
        return parse_answer(content)
