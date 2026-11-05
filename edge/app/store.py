"""Местное хранилище: кэш ответов и очередь недоставленных комментариев."""

import json
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS cached (
    path TEXT PRIMARY KEY,
    body TEXT NOT NULL,
    status INTEGER NOT NULL,
    stored_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS outbox (
    client_id TEXT PRIMARY KEY,
    path TEXT NOT NULL,
    body TEXT NOT NULL,
    headers TEXT NOT NULL,
    created_at TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    state TEXT NOT NULL DEFAULT 'pending',
    last_error TEXT
);
CREATE INDEX IF NOT EXISTS ix_outbox_state ON outbox (state, created_at);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self, path: str) -> None:
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        self.db.commit()

    def close(self) -> None:
        self.db.close()

    def cached(self, path: str) -> dict | None:
        row = self.db.execute("SELECT body, status, stored_at FROM cached WHERE path = ?", (path,)).fetchone()
        return dict(row) if row else None

    def remember(self, path: str, body: str, status: int) -> None:
        self.db.execute(
            "INSERT INTO cached (path, body, status, stored_at) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(path) DO UPDATE SET body = excluded.body, status = excluded.status, "
            "stored_at = excluded.stored_at",
            (path, body, status, _now()),
        )
        self.db.commit()

    def enqueue(self, path: str, body: dict, headers: dict, client_id: str | None = None) -> str:
        key = client_id or uuid.uuid4().hex
        self.db.execute(
            "INSERT OR IGNORE INTO outbox (client_id, path, body, headers, created_at, state) "
            "VALUES (?, ?, ?, ?, ?, 'pending')",
            (key, path, json.dumps(body, ensure_ascii=False), json.dumps(headers, ensure_ascii=False), _now()),
        )
        self.db.commit()
        return key

    def pending(self, limit: int = 50) -> list[dict]:
        rows = self.db.execute(
            "SELECT * FROM outbox WHERE state = 'pending' ORDER BY created_at LIMIT ?", (limit,)
        ).fetchall()
        return [dict(row) for row in rows]

    def sent(self, client_id: str) -> None:
        self.db.execute("UPDATE outbox SET state = 'sent', last_error = NULL WHERE client_id = ?", (client_id,))
        self.db.commit()

    def rejected(self, client_id: str, reason: str) -> None:
        self.db.execute(
            "UPDATE outbox SET state = 'rejected', last_error = ? WHERE client_id = ?", (reason[:300], client_id)
        )
        self.db.commit()

    def failed(self, client_id: str, reason: str) -> None:
        self.db.execute(
            "UPDATE outbox SET attempts = attempts + 1, last_error = ? WHERE client_id = ?",
            (reason[:300], client_id),
        )
        self.db.commit()

    def count(self, state: str | None = None) -> int:
        if state is None:
            row = self.db.execute("SELECT count(*) FROM outbox").fetchone()
        else:
            row = self.db.execute("SELECT count(*) FROM outbox WHERE state = ?", (state,)).fetchone()
        return int(row[0])

    def compact(self, *, retention_days: int) -> int:
        """Убирает отправленное и безнадёжное старше срока хранения."""
        border = (datetime.now(timezone.utc) - timedelta(days=retention_days)).isoformat()
        cursor = self.db.execute(
            "DELETE FROM outbox WHERE state IN ('sent', 'rejected') AND created_at < ?", (border,)
        )
        self.db.commit()
        return cursor.rowcount
