"""Хеширование секретов. Открытые ключи и адреса не хранятся."""

import hashlib
import hmac
import secrets


def new_token() -> str:
    """Возвращает новый секрет для выдачи внешнему агенту."""
    return secrets.token_urlsafe(32)


def hash_secret(secret: str, pepper: str) -> str:
    """Необратимый хеш секрета."""
    return hashlib.sha256(f"{pepper}:{secret}".encode()).hexdigest()


def secrets_equal(left: str, right: str) -> bool:
    """Сравнение без утечки времени."""
    return hmac.compare_digest(left.encode(), right.encode())
