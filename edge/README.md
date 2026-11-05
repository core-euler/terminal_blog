# Пограничная служба

Стоит на VPS между сайтом и домашним API: кэширует чтение и держит очередь комментариев, пока бэк выключен. Правила — `docs/specs/offline-mode.md`.

## Запуск

    python -m venv .venv && .venv/bin/pip install -e .
    cp .env.example .env
    .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8090

Досылка очереди — по таймеру: `deploy/systemd/coreeuler-edge-sync.timer` раз в тридцать секунд запускает `coreeuler-edge-sync.service`.

Состояние очереди: `GET /api/health` — сколько ждёт отправки и сколько отклонено.

## Проверка

    python -m pytest

Тесты поднимают службу в процессе и подменяют бэк транспортом httpx: сеть не нужна.
