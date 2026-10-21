"""Tests for Poltergeist notification service."""

import os
import pytest
from fastapi.testclient import TestClient

from poltergeist.api import app, _notifications, _templates


@pytest.fixture(autouse=True)
def clear_data():
    _notifications.clear()
    _templates.clear()
    os.environ["API_KEY"] = "test-key"
    yield


client = TestClient(app)


class TestHealth:
    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "Poltergeist"


class TestNotifications:
    def test_send_notification(self):
        response = client.post(
            "/api/notifications",
            json={"channel": "slack", "recipient": "#alerts", "title": "Alert", "message": "Server down"},
            params={"x_key": "test-key"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["channel"] == "slack"
        assert data["status"] == "sent"

    def test_list_notifications(self):
        response = client.get("/api/notifications", params={"x_key": "test-key"})
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestTemplates:
    def test_create_template(self):
        response = client.post(
            "/api/templates",
            json={"name": "welcome", "channel": "email", "subject": "Hello {name}", "body": "Welcome {name}!"},
            params={"x_key": "test-key"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "welcome"

    def test_send_from_template(self):
        client.post(
            "/api/templates",
            json={"name": "greet", "channel": "discord", "subject": "", "body": "Hi {name}!"},
            params={"x_key": "test-key"},
        )
        response = client.post(
            "/api/templates/greet/send",
            json={"recipient": "user123", "variables": {"name": "Luigi"}},
            params={"x_key": "test-key"},
        )
        assert response.status_code == 200
        assert "Luigi" in response.json()["message"]


class TestAuth:
    def test_invalid_key(self):
        response = client.get("/api/notifications", params={"x_key": "wrong"})
        assert response.status_code == 401
