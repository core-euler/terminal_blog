"""Адреса, заголовки и разметка: мелкие правила, на которых стоит отбор."""

from app.agent.text import (
    canonical_url,
    html_to_text,
    looks_like_digest,
    page_text,
    same_event,
    slugify,
    title_fingerprint,
)


def test_canonical_url_drops_tracking_and_anchor():
    assert (
        canonical_url("https://WWW.Example.com/news/item/?utm_source=rss&id=7#top")
        == "https://example.com/news/item?id=7"
    )


def test_canonical_url_rejects_garbage():
    assert canonical_url("") is None
    assert canonical_url("ftp://example.com/x") is None
    assert canonical_url("не адрес") is None


def test_html_to_text_removes_tags_and_scripts():
    raw = "<p>Первый</p><script>alert(1)</script><p>Второй &amp; третий</p>"

    text = html_to_text(raw)

    assert "Первый" in text and "Второй & третий" in text
    assert "alert" not in text and "<" not in text


def test_page_text_keeps_only_paragraphs():
    html = "<nav><p>меню</p></nav><article><p>" + "д" * 60 + "</p><p>коротко</p></article>"

    text = page_text(html)

    assert "д" * 60 in text
    assert "коротко" not in text


def test_same_event_compares_words_not_order():
    assert same_event(
        "PostgreSQL 18 released with async IO", "PostgreSQL 18 released with async IO support"
    )
    assert not same_event("PostgreSQL 18 released", "Rust 1.80 released with new lints")


def test_slugify_transliterates_russian_title():
    slug = slugify("PostgreSQL 18 вышел с асинхронным вводом-выводом")

    assert slug == "postgresql-18-vyshel-s-asinhronnym-vvodom-vyvodom"
    assert slugify("!!!") == "novost"


def test_fingerprint_ignores_order_and_case():
    assert title_fingerprint("Async IO in PostgreSQL") == title_fingerprint("postgresql async io")


def test_digest_titles_are_recognised():
    assert looks_like_digest("Weekly roundup: databases", "")
    assert looks_like_digest("Итоги недели в разработке", "")
    assert not looks_like_digest("PostgreSQL 18 released", "Асинхронный ввод-вывод по умолчанию")
