"""Разбор адресов, заголовков и разметки страниц."""

import html
import re
from urllib.parse import urlsplit, urlunsplit

TAG = re.compile(r"<[^>]+>")
SCRIPT = re.compile(r"<(script|style|noscript)\b.*?</\1>", re.S | re.I)
SPACES = re.compile(r"[ \t\u00a0]+")
BLANK_LINES = re.compile(r"\n{3,}")
WORD = re.compile(r"[\w\-]{4,}", re.U)

TRACKING = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "utm_name",
    "fbclid",
    "gclid",
    "ref",
    "ref_src",
    "source",
    "at_medium",
}


def canonical_url(raw: str) -> str | None:
    """Адрес без хвостов: без параметров слежки, без якоря, без завершающего слэша."""
    if not raw:
        return None
    parts = urlsplit(raw.strip())
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        return None
    query = [pair for pair in parts.query.split("&") if pair and pair.split("=")[0].lower() not in TRACKING]
    path = parts.path.rstrip("/") or "/"
    host = parts.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return urlunsplit((parts.scheme, host, path, "&".join(query), ""))


def html_to_text(raw: str) -> str:
    """Текст из разметки: теги убираются, лишние пробелы схлопываются."""
    without_scripts = SCRIPT.sub(" ", raw or "")
    breaks = re.sub(r"</(p|div|li|h[1-6]|br|tr)>", "\n", without_scripts, flags=re.I)
    breaks = re.sub(r"<br\s*/?>", "\n", breaks, flags=re.I)
    text = html.unescape(TAG.sub(" ", breaks))
    lines = [SPACES.sub(" ", line).strip() for line in text.splitlines()]
    joined = "\n".join(line for line in lines if line)
    return BLANK_LINES.sub("\n\n", joined).strip()


def page_text(raw_html: str, *, min_paragraph: int = 40) -> str:
    """Основной текст страницы: абзацы подряд, служебные обрывки отбрасываются."""
    blocks = re.findall(r"<p\b[^>]*>(.*?)</p>", raw_html or "", re.S | re.I)
    paragraphs = [html_to_text(block) for block in blocks]
    useful = [text for text in paragraphs if len(text) >= min_paragraph]
    return "\n\n".join(useful)


def title_fingerprint(title: str) -> str:
    """Отпечаток события: значимые слова заголовка без порядка и регистра."""
    words = sorted({word.lower() for word in WORD.findall(title or "")})
    return " ".join(words)[:200]


def word_set(title: str) -> set[str]:
    return {word.lower() for word in WORD.findall(title or "")}


def same_event(first: str, second: str, *, threshold: float = 0.6) -> bool:
    """Одно и то же событие у разных изданий: заголовки совпадают по значимым словам."""
    left, right = word_set(first), word_set(second)
    if not left or not right:
        return False
    return len(left & right) / len(left | right) >= threshold


def looks_like_digest(title: str, summary: str) -> bool:
    """Подборки, дайджесты и итоги недели новостью не считаются."""
    haystack = f"{title} {summary[:300]}".lower()
    markers = (
        "дайджест",
        "итоги недели",
        "что нового за неделю",
        "weekly roundup",
        "roundup:",
        "this week in",
        "links for",
        "подборка",
        "top stories",
    )
    return any(marker in haystack for marker in markers)


def slugify(title: str, *, limit: int = 80) -> str:
    """Адрес новости из заголовка: латиница, цифры и дефисы."""
    transliterated = transliterate((title or "").lower())
    slug = re.sub(r"[^a-z0-9]+", "-", transliterated).strip("-")
    return slug[:limit].strip("-") or "novost"


TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e", "ж": "zh",
    "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o",
    "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "ts",
    "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu",
    "я": "ya",
}


def transliterate(text: str) -> str:
    return "".join(TRANSLIT.get(char, char) for char in text)
