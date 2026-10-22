"""Delivery implementations for Poltergeist notification service.

Each delivery class handles formatting and sending notifications to a specific
channel: Slack (webhooks), Discord (webhooks), Email (SMTP), and Telegram (bot API).
"""

import logging
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx

from poltergeist.models import Notification

logger = logging.getLogger("poltergeist")


class BaseDelivery:
    """Abstract base for notification delivery."""

    async def send(self, notification: Notification) -> None:
        """Send a notification and update its status."""
        raise NotImplementedError

    def _get_timeout(self) -> float:
        return float(os.getenv("POLTERGEIST_REQUEST_TIMEOUT", "30"))


class SlackDelivery(BaseDelivery):
    """Deliver notifications via Slack Incoming Webhooks."""

    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL", "")

    async def send(self, notification: Notification) -> None:
        if not self.webhook_url:
            raise RuntimeError("SLACK_WEBHOOK_URL is not configured")

        # Slack block kit format
        payload = {
            "text": f"{notification.title}\n{notification.message}",
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": notification.title or "Notification"},
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": notification.message},
                },
            ],
        }
        # Override webhook if recipient is provided as a URL
        url = notification.recipient or self.webhook_url

        async with httpx.AsyncClient(timeout=self._get_timeout()) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                raise ConnectionError(f"Slack returned {response.status_code}: {response.text}")


class DiscordDelivery(BaseDelivery):
    """Deliver notifications via Discord Webhooks."""

    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")

    async def send(self, notification: Notification) -> None:
        if not self.webhook_url:
            raise RuntimeError("DISCORD_WEBHOOK_URL is not configured")

        payload = {
            "content": None,
            "embeds": [
                {
                    "title": notification.title or "Notification",
                    "description": notification.message[:2048],  # Discord limit
                    "color": 5814783,  # Blue
                }
            ],
        }
        url = notification.recipient or self.webhook_url

        async with httpx.AsyncClient(timeout=self._get_timeout()) as client:
            response = await client.post(url, json=payload)
            if response.status_code not in (200, 204):
                raise ConnectionError(f"Discord returned {response.status_code}: {response.text}")


class EmailDelivery(BaseDelivery):
    """Deliver notifications via SMTP."""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "localhost")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_from = os.getenv("SMTP_FROM", "noreply@evershade.local")
        self.use_tls = os.getenv("SMTP_TLS", "true").lower() in ("true", "1", "yes")

    async def send(self, notification: Notification) -> None:
        if not self.smtp_user:
            raise RuntimeError("SMTP_USER is not configured")

        msg = MIMEMultipart()
        msg["From"] = self.smtp_from
        msg["To"] = notification.recipient
        msg["Subject"] = notification.title or "Evershade Notification"
        msg.attach(MIMEText(notification.message, "html"))

        context = ssl.create_default_context() if self.use_tls else None

        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
            if self.use_tls:
                server.starttls(context=context)
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
            server.sendmail(
                self.smtp_from,
                notification.recipient,
                msg.as_string(),
            )


class TelegramDelivery(BaseDelivery):
    """Deliver notifications via Telegram Bot API."""

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.base_url = "https://api.telegram.org/bot"

    async def send(self, notification: Notification) -> None:
        if not self.bot_token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")

        # Recipient is the chat_id
        chat_id = notification.recipient
        if not chat_id:
            raise ValueError("Telegram chat_id (recipient) is required")

        url = f"{self.base_url}{self.bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": f"{notification.title}\n\n{notification.message}",
            "parse_mode": "HTML",
        }

        async with httpx.AsyncClient(timeout=self._get_timeout()) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                raise ConnectionError(f"Telegram returned {response.status_code}: {response.text}")


class WebhookDelivery(BaseDelivery):
    """Deliver notifications via generic HTTP webhooks."""

    async def send(self, notification: Notification) -> None:
        url = notification.recipient
        if not url:
            raise ValueError("Webhook URL (recipient) is required")

        payload = {
            "title": notification.title,
            "message": notification.message,
            "metadata": notification.metadata,
        }

        async with httpx.AsyncClient(timeout=self._get_timeout()) as client:
            response = await client.post(url, json=payload)
            if response.status_code >= 400:
                raise ConnectionError(f"Webhook returned {response.status_code}: {response.text}")


def get_delivery(channel_str: str) -> BaseDelivery:
    """Get the delivery instance for a given channel."""
    delivery_map = {
        "slack": SlackDelivery(),
        "discord": DiscordDelivery(),
        "email": EmailDelivery(),
        "telegram": TelegramDelivery(),
        "webhook": WebhookDelivery(),
    }
    if channel_str not in delivery_map:
        raise ValueError(f"Unknown channel: {channel_str}")
    return delivery_map[channel_str]
