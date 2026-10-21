"""FastAPI application for Polterpup notification service."""

import os
from datetime import datetime
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query

from polterpup.models import Notification, Template, Channel, NotificationStatus


app = FastAPI(
    title="Polterpup",
    description="Notification and messaging hub for the Evershade ecosystem",
    version="1.0.0",
)

API_KEY = os.getenv("API_KEY", "Polterpup-dev-key-change-me")

_notifications: list[Notification] = []
_templates: dict[str, Template] = {}


def verify_key(x_key: Optional[str] = Query(None)) -> None:
    if x_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "Polterpup"}


# ─── Notifications ──────────────────────────────────────────────

@app.post("/api/notifications")
async def send_notification(data: dict[str, Any], x_key: Optional[str] = Query(None)) -> dict[str, Any]:
    verify_key(x_key)
    notification = Notification(
        channel=Channel(data["channel"]),
        recipient=data["recipient"],
        title=data.get("title", ""),
        message=data["message"],
        metadata=data.get("metadata"),
    )
    # Simulate sending
    notification.status = NotificationStatus.SENT
    notification.sent_at = datetime.utcnow()
    _notifications.append(notification)
    return notification.to_dict()


@app.get("/api/notifications")
async def list_notifications(
    channel: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    x_key: Optional[str] = Query(None),
) -> list[dict[str, Any]]:
    verify_key(x_key)
    results = _notifications
    if channel:
        results = [n for n in results if n.channel.value == channel]
    if status:
        results = [n for n in results if n.status.value == status]
    return [n.to_dict() for n in results[-limit:]]


# ─── Templates ──────────────────────────────────────────────────

@app.post("/api/templates")
async def create_template(data: dict[str, Any], x_key: Optional[str] = Query(None)) -> dict[str, Any]:
    verify_key(x_key)
    template = Template(
        name=data["name"],
        channel=Channel(data["channel"]),
        subject=data.get("subject", ""),
        body=data["body"],
        variables=data.get("variables"),
    )
    _templates[template.name] = template
    return template.to_dict()


@app.get("/api/templates")
async def list_templates(x_key: Optional[str] = Query(None)) -> list[dict[str, Any]]:
    verify_key(x_key)
    return [t.to_dict() for t in _templates.values()]


@app.get("/api/templates/{name}")
async def get_template(name: str, x_key: Optional[str] = Query(None)) -> dict[str, Any]:
    verify_key(x_key)
    template = _templates.get(name)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return template.to_dict()


@app.post("/api/templates/{name}/send")
async def send_from_template(
    name: str,
    data: dict[str, Any],
    x_key: Optional[str] = Query(None),
) -> dict[str, Any]:
    verify_key(x_key)
    template = _templates.get(name)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    rendered = template.render(**data.get("variables", {}))
    notification = Notification(
        channel=template.channel,
        recipient=data["recipient"],
        title=rendered["subject"],
        message=rendered["body"],
    )
    notification.status = NotificationStatus.SENT
    notification.sent_at = datetime.utcnow()
    _notifications.append(notification)
    return notification.to_dict()


@app.delete("/api/templates/{name}")
async def delete_template(name: str, x_key: Optional[str] = Query(None)) -> dict[str, bool]:
    verify_key(x_key)
    if name not in _templates:
        raise HTTPException(status_code=404, detail="Template not found")
    del _templates[name]
    return {"deleted": True}
