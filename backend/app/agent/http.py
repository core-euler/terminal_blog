"""Запросы к источникам: условный запрос, таймаут, честное имя клиента."""

import httpx

USER_AGENT = "coreeuler-news/1.0 (+https://coreeuler.art)"
TIMEOUT_SECONDS = 20
MAX_BODY_BYTES = 4 * 1024 * 1024


class FetchError(Exception):
    """Источник не ответил или ответил ошибкой."""


class FetchResult:
    __slots__ = ("status", "body", "etag", "last_modified")

    def __init__(self, status: int, body: str = "", etag: str | None = None, last_modified: str | None = None):
        self.status = status
        self.body = body
        self.etag = etag
        self.last_modified = last_modified

    @property
    def unchanged(self) -> bool:
        return self.status == 304

    def __repr__(self) -> str:  # pragma: no cover - отладка
        return f"FetchResult(status={self.status}, bytes={len(self.body)})"


class Fetcher:
    """Что нужно циклу от сети. В тестах подменяется записанными ответами."""

    def get(self, url: str, *, etag: str | None = None, last_modified: str | None = None) -> FetchResult:
        raise NotImplementedError


class HttpFetcher(Fetcher):
    def __init__(self, *, timeout: float = TIMEOUT_SECONDS) -> None:
        self._http = httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT, "Accept-Language": "en,ru;q=0.8"},
        )

    def get(self, url: str, *, etag: str | None = None, last_modified: str | None = None) -> FetchResult:
        headers = {}
        if etag:
            headers["If-None-Match"] = etag
        if last_modified:
            headers["If-Modified-Since"] = last_modified
        try:
            response = self._http.get(url, headers=headers)
        except httpx.HTTPError as error:
            raise FetchError(f"{type(error).__name__}: {error}") from error

        if response.status_code == 304:
            return FetchResult(304, etag=etag, last_modified=last_modified)
        if response.status_code >= 400:
            raise FetchError(f"ответ {response.status_code}")
        if len(response.content) > MAX_BODY_BYTES:
            raise FetchError("ответ больше допустимого размера")
        return FetchResult(
            response.status_code,
            response.text,
            response.headers.get("ETag"),
            response.headers.get("Last-Modified"),
        )

    def close(self) -> None:
        self._http.close()
