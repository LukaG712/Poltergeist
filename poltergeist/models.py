"""Data models for Poltergeist notifications."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4


class Channel(str, Enum):
    SLACK = "slack"
    DISCORD = "discord"
    EMAIL = "email"
    TELEGRAM = "telegram"
    WEBHOOK = "webhook"


class NotificationStatus(str, Enum):
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
        metadata: Optional[dict[str, Any]] = None,
        status: NotificationStatus = NotificationStatus.PENDING,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id or uuid4()
        self.channel = channel
        self.recipient = recipient
        self.title = title
        self.message = message
        self.metadata = metadata or {}
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.sent_at: Optional[datetime] = None
        self.error: Optional[str] = None

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
        variables: Optional[list[str]] = None,
        id: Optional[UUID] = None,
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
