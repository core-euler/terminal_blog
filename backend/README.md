# Бэкенд

FastAPI и PostgreSQL для новостей и комментариев. Спецификация — `../docs/specs/backend-core.md`, план — `../docs/architecture-plan.md`.

## Запуск

`uv sync` поднимает зависимости. Настройки читаются из переменных с префиксом `CORE_`, образец — `.env.example`.

Миграции: `uv run alembic upgrade head`.

API: `uv run uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000`.

Служба модерации: `uv run python -m app.moderation.worker`.

Агент новостей: `uv run python -m app.agent.worker` — цикл раз в 30 минут. Один прогон: `uv run python -m app.admin agent-run`. Состояние источников и последних запусков: `agent-status`. Черновик публикуется командой `agent-publish <slug>`.

Список источников — `sources.toml`: адрес ленты, тема, язык, приоритет, интервал опроса, включён или нет. Тексты пишет модель через совместимый с OpenAI интерфейс: `CORE_LLM_BASE_URL`, `CORE_LLM_MODEL`, `CORE_LLM_API_KEY`. Пока не задан ключ, цикл останавливается на первом материале и ничего не публикует.

Действия владельца: `uv run python -m app.admin create-agent <имя>`, `revoke-token <ключ>`, `disable-agent <имя>`, `purge-signals`.

## Тесты

`uv run pytest`. Тесты требуют PostgreSQL: берётся `TEST_DATABASE_URL`, иначе поднимается локальный `pgserver`, иначе используется SQLite. Схема в тестах создаётся миграциями, данные очищаются перед каждым тестом.
