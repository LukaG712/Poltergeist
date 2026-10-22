"""SQLite storage for Poltergeist notifications and templates."""

import os
import sqlite3
from datetime import datetime

from poltergeist.models import Notification, NotificationStatus, Template


class Storage:
    """SQLite-backed storage for notifications and templates."""

    def __init__(self, db_path: str = "/app/data/poltergeist.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id TEXT PRIMARY KEY,
                    channel TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    title TEXT,
                    message TEXT NOT NULL,
                    metadata TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    sent_at TEXT,
                    error TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS templates (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    channel TEXT NOT NULL,
                    subject TEXT,
                    body TEXT NOT NULL,
                    variables TEXT
                )
            """)
            conn.commit()

    # ─── Notifications ──────────────────────────────────────────

    def create_notification(self, notification: Notification) -> dict:
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO notifications (id, channel, recipient, title, message, metadata, status, created_at, sent_at, error) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    str(notification.id), notification.channel.value, notification.recipient,
                    notification.title, notification.message,
                    str(notification.metadata) if notification.metadata else None,
                    notification.status.value, notification.created_at.isoformat(),
                    notification.sent_at.isoformat() if notification.sent_at else None,
                    notification.error,
                ),
            )
            conn.commit()

    def update_notification_status(self, notification_id: str, status: NotificationStatus, error: str | None = None, sent_at: datetime | None = None) -> bool:
        with self._get_conn() as conn:
            updates = ["status = ?"]
            values = [status.value]
            if sent_at:
                updates.append("sent_at = ?")
                values.append(sent_at.isoformat())
            if error is not None:
                updates.append("error = ?")
                values.append(error)
            values.append(str(notification_id))
            conn.execute(f"UPDATE notifications SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()
            return conn.total_changes > 0

    def list_notifications(
        self,
        channel: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        with self._get_conn() as conn:
            query = "SELECT * FROM notifications WHERE 1=1"
            params = []
            if channel:
                query += " AND channel = ?"
                params.append(channel)
            if status:
                query += " AND status = ?"
                params.append(status)
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def get_notification(self, notification_id: str) -> dict | None:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM notifications WHERE id = ?",
                (str(notification_id),)
            ).fetchone()
            return dict(row) if row else None

    # ─── Templates ──────────────────────────────────────────────

    def create_template(self, template: Template) -> dict:
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO templates (id, name, channel, subject, body, variables) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    str(template.id), template.name, template.channel.value,
                    template.subject, template.body,
                    str(template.variables) if template.variables else None,
                ),
            )
            conn.commit()

    def get_template(self, name: str) -> dict | None:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM templates WHERE name = ?", (name,)
            ).fetchone()
            return dict(row) if row else None

    def list_templates(self) -> list[dict]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM templates ORDER BY name").fetchall()
            return [dict(r) for r in rows]

    def delete_template(self, name: str) -> bool:
        with self._get_conn() as conn:
            conn.execute("DELETE FROM templates WHERE name = ?", (name,))
            conn.commit()
            return conn.total_changes > 0
