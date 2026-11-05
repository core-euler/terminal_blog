"""Настройки сервиса. Значения читаются из переменных окружения с префиксом CORE_."""

from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CORE_", env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres@/coreeuler?host=/tmp"

    # Секрет агента новостей. Пустое значение запрещает публикацию.
    news_agent_token: str = ""

    # Перец для необратимых хешей адресов и ключей.
    hash_pepper: str = "change-me"

    comment_max_length: int = 2000
    name_max_length: int = 40
    comment_rate_limit: int = 5
    comment_rate_window_seconds: int = 600
    agent_rate_limit: int = 60
    agent_rate_window_seconds: int = 3600
    rate_event_ttl_hours: int = 24

    moderation_max_attempts: int = 3
    rules_version: str = "moderation-v1"

    trust_proxy_headers: bool = False

    # Источники, которым разрешены запросы из браузера. В продакшене пусто: сайт и API на одном домене.
    cors_origins: Annotated[list[str], NoDecode] = []

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        """Список в переменной окружения пишется через запятую."""
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    news_page_limit: int = 20
    news_page_max_limit: int = 50
