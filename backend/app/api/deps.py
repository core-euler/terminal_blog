"""Извлечение адреса клиента для ограничения частоты."""

from fastapi import Request

from app.config import Settings


def client_ip(request: Request, settings: Settings) -> str:
    """Адрес клиента. Заголовку прокси верим только при явной настройке."""
    if settings.trust_proxy_headers:
        forwarded = request.headers.get("x-real-ip") or request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
    if request.client is not None:
        return request.client.host
    return "unknown"
