"""Data models for Poltergeist notifications."""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class Channel(StrEnum):
    SLACK = "slack"
    DISCORD = "discord"
    EMAIL = "email"
    TELEGRAM = "telegram"
    WEBHOOK = "webhook"


class NotificationStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Notification:
    def __init__(
        self,
        channel: Channel,
        recipient: str,
        title: str,
        message: str,
        metadata: dict[str, Any] | None = None,
        status: NotificationStatus = NotificationStatus.PENDING,
        id: UUID | None = None,
        created_at: datetime | None = None,
    ):
        self.id = id or uuid4()
        self.channel = channel
        self.recipient = recipient
        self.title = title
        self.message = message
        self.metadata = metadata or {}
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.sent_at: datetime | None = None
        self.error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "channel": self.channel.value,
            "recipient": self.recipient,
            "title": self.title,
            "message": self.message,
            "metadata": self.metadata,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "error": self.error,
        }


class Template:
    def __init__(
        self,
        name: str,
        channel: Channel,
        subject: str,
        body: str,
        variables: list[str] | None = None,
        id: UUID | None = None,
    ):
        self.id = id or uuid4()
        self.name = name
        self.channel = channel
        self.subject = subject
        self.body = body
        self.variables = variables or []

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "channel": self.channel.value,
            "subject": self.subject,
            "body": self.body,
            "variables": self.variables,
        }

    def render(self, **kwargs: str) -> dict[str, str]:
        return {
            "subject": self.subject.format(**kwargs),
            "body": self.body.format(**kwargs),
        }
