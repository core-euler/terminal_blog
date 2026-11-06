"""Подсказка модели и разбор её ответа."""

import json

import httpx
import pytest

from app.agent.writer import DraftedNews, LlmWriter, WriterError, parse_answer

MATERIAL = "PostgreSQL 18 released with async IO\nhttps://example.com/pg18\n\nАсинхронный ввод-вывод включён по умолчанию."


def _writer(handler) -> LlmWriter:
    return LlmWriter(
        base_url="https://models.example/v1",
        model="test-model",
        api_key="key",
        transport=httpx.MockTransport(handler),
    )


def test_prompt_keeps_json_example_and_material():
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["body"] = json.loads(request.content)
        seen["auth"] = request.headers.get("authorization")
        return httpx.Response(200, json={"choices": [{"message": {"content": '{"title": "Заголовок", "body": "Тело"}'}}]})

    writer = _writer(handler)
    draft = writer.write(title="PostgreSQL 18 released", url="https://example.com/pg18", page_text="Асинхронный ввод-вывод включён по умолчанию.", topic="databases")

    assert draft == DraftedNews(title="Заголовок", body="Тело")
    content = seen["body"]["messages"][0]["content"]
    assert '{"title"' in content, "пример JSON не должен ломаться подстановкой"
    assert "Асинхронный ввод-вывод включён по умолчанию." in content
    assert seen["body"]["model"] == "test-model"
    assert seen["auth"] == "Bearer key"


def test_provider_error_means_no_text():
    writer = _writer(lambda request: httpx.Response(500, json={"error": "нет"}))

    with pytest.raises(WriterError):
        writer.write(title="t", url="u", page_text=MATERIAL, topic="dev")


def test_missing_key_stops_before_request():
    writer = LlmWriter(base_url="https://models.example/v1", model="m", api_key="")

    with pytest.raises(WriterError):
        writer.write(title="t", url="u", page_text=MATERIAL, topic="dev")


def test_answer_in_code_fence_is_parsed():
    raw = '```json\n{"title": "Коротко", "body": "Первый абзац.\\n\\nВторой абзац."}\n```'

    draft = parse_answer(raw)

    assert draft.title == "Коротко"
    assert draft.body.startswith("Первый абзац.")


def test_links_inside_body_are_rejected():
    with pytest.raises(WriterError):
        parse_answer('{"title": "Заголовок", "body": "см. https://example.com"}')


def test_long_title_is_rejected():
    with pytest.raises(WriterError):
        parse_answer(json.dumps({"title": "я" * 120, "body": "тело"}))


def test_english_answer_is_rejected():
    with pytest.raises(WriterError):
        parse_answer('{"title": "PostgreSQL 18 released", "body": "Async IO is enabled by default."}')
