"""Настройки пограничной службы."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class EdgeSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="EDGE_", env_file=".env", extra="ignore")

    backend_url: str = "http://127.0.0.1:8081"
    db_path: str = "edge.db"
    # Сколько секунд ответ считается свежим: дальше сначала спрашиваем бэк.
    cache_seconds: int = 60
    timeout_seconds: float = 5.0
    # Быстрый запрос к бэку при приёме комментария: не заставляем человека ждать.
    accept_timeout_seconds: float = 2.0
    retention_days: int = 30
