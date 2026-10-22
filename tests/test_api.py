"""Tests for Poltergeist notification service."""

import os
import tempfile
import pytest
from fastapi.testclient import TestClient

# Set API_KEY BEFORE importing the app module
os.environ["API_KEY"] = "test-key"

# Use temporary database for tests
db_fd, db_path = tempfile.mkstemp(suffix=".db")
os.close(db_fd)
os.environ["DB_PATH"] = db_path

from poltergeist.api import app

@pytest.fixture(autouse=True)
def cleanup_db():
    """Clean up test database after each test."""
    yield
    if os.path.exists(db_path):
        try:
            os.unlink(db_path)
        except OSError:
            pass
    for suffix in ("-wal", "-shm"):
        wal_path = db_path + suffix
        if os.path.exists(wal_path):
            try:
                os.unlink(wal_path)
            except OSError:
                pass


client = TestClient(app)
HEADERS = {"Authorization": "Bearer test-key"}


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
            headers=HEADERS,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["channel"] == "slack"

    def test_list_notifications(self):
        response = client.get("/api/notifications", headers=HEADERS)
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestTemplates:
    def test_create_template(self):
        response = client.post(
            "/api/templates",
            json={"name": "welcome", "channel": "email", "subject": "Hello {name}", "body": "Welcome {name}!"},
            headers=HEADERS,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "welcome"

    def test_send_from_template(self):
        client.post(
            "/api/templates",
            json={"name": "greet", "channel": "discord", "subject": "", "body": "Hi {name}!"},
            headers=HEADERS,
        )
        response = client.post(
            "/api/templates/greet/send",
            json={"recipient": "user123", "variables": {"name": "Luigi"}},
            headers=HEADERS,
        )
        assert response.status_code == 200
        assert "Luigi" in response.json()["message"]


class TestAuth:
    def test_invalid_key(self):
        response = client.get("/api/notifications", headers={"Authorization": "Bearer wrong"})
        assert response.status_code == 401

    def test_missing_auth(self):
        response = client.get("/api/notifications")
        assert response.status_code == 401

    def test_query_param_rejected(self):
        response = client.get("/api/notifications", params={"x_key": "test-key"})
        assert response.status_code == 401
