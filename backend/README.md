# Бэкенд

FastAPI и PostgreSQL для новостей и комментариев. Спецификация — `../docs/specs/backend-core.md`, план — `../docs/architecture-plan.md`.

## Запуск

`uv sync` поднимает зависимости. Настройки читаются из переменных с префиксом `CORE_`, образец — `.env.example`.

Миграции: `uv run alembic upgrade head`.

API: `uv run uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000`.

Служба модерации: `uv run python -m app.moderation.worker`.

Действия владельца: `uv run python -m app.admin create-agent <имя>`, `revoke-token <ключ>`, `disable-agent <имя>`, `purge-signals`.

## Тесты

`uv run pytest`. Тесты требуют PostgreSQL: берётся `TEST_DATABASE_URL`, иначе поднимается локальный `pgserver`, иначе используется SQLite. Схема в тестах создаётся миграциями, данные очищаются перед каждым тестом.
