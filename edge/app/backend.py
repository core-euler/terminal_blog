"""Разговор с домашним API."""

import httpx


class Backend:
    """Тонкий клиент бэка. Транспорт подменяется в тестах."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float,
        accept_timeout: float | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._accept_timeout = accept_timeout or timeout
        self._transport = transport

    def _client(self, timeout: float) -> httpx.Client:
        # Бэк доступен через туннель на этой же машине: прокси из окружения не нужны.
        return httpx.Client(
            base_url=self._base_url,
            timeout=timeout,
            transport=self._transport,
            trust_env=False,
        )

    def get(self, path: str, query: str = "") -> tuple[int, str]:
        """Чтение. Сеть пробрасывает ошибкой, ответ отдаёт как есть."""
        target = f"{path}?{query}" if query else path
        with self._client(self._timeout) as client:
            response = client.get(target)
        return response.status_code, response.text

    def post(self, path: str, body: dict, headers: dict) -> tuple[int, str]:
        with self._client(self._accept_timeout) as client:
            response = client.post(path, json=body, headers=headers)
        return response.status_code, response.text
