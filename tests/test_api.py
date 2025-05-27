import os
import tempfile

import pytest
from fastapi.testclient import TestClient

from app.database import Database
from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def test_db():
    """Create a temporary test database."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_path = f.name

    db = Database(db_path)
    yield db

    # Cleanup
    os.unlink(db_path)


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "TRMNL Custom Server"
    assert data["status"] == "running"


def test_setup_new_device(client):
    """Test device setup for a new device."""
    headers = {"ID": "AA:BB:CC:DD:EE:FF", "FW-Version": "1.5.2"}

    response = client.post("/api/setup", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == 200
    assert "api_key" in data
    assert "friendly_id" in data
    assert "image_url" in data
    assert len(data["api_key"]) == 32
    assert len(data["friendly_id"]) == 6


def test_setup_existing_device(client):
    """Test setup for existing device returns same credentials."""
    headers = {"ID": "AA:BB:CC:DD:EE:FF", "FW-Version": "1.5.2"}

    # First setup
    response1 = client.post("/api/setup", headers=headers)
    data1 = response1.json()

    # Second setup (should return same credentials)
    response2 = client.post("/api/setup", headers=headers)
    data2 = response2.json()

    assert data1["api_key"] == data2["api_key"]
    assert data1["friendly_id"] == data2["friendly_id"]


def test_display_endpoint_no_auth_required(client):
    """Test display endpoint without authentication."""
    headers = {
        "ID": "AA:BB:CC:DD:EE:FF",
        "Refresh-Rate": "1800",
        "Battery-Voltage": "4.12",
        "FW-Version": "1.5.2",
        "RSSI": "-45",
        "Width": "800",
        "Height": "480",
    }

    response = client.get("/api/display", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == 0
    assert "image_url" in data
    assert "filename" in data
    assert data["refresh_rate"] == 1800


def test_log_endpoint(client):
    """Test device logging endpoint (no auth required)."""
    # Test logging without authentication
    log_headers = {"ID": "AA:BB:CC:DD:EE:FF"}

    log_data = {
        "battery_voltage": 4.12,
        "heap_free": 45632,
        "rssi": -45,
        "wake_reason": "timer",
        "firmware_version": "1.5.2",
    }

    response = client.post("/api/log", headers=log_headers, json=log_data)
    assert response.status_code == 200


def test_log_endpoint_unknown_device(client):
    """Test device logging endpoint with unknown device."""
    log_headers = {
        "ID": "FF:FF:FF:FF:FF:FF"  # Unknown device
    }

    log_data = {"battery_voltage": 3.8, "firmware_version": "1.4.0"}

    response = client.post("/api/log", headers=log_headers, json=log_data)
    assert response.status_code == 200  # Should still accept the log


def test_create_screen_endpoint(client):
    """Test screen creation endpoint (no auth required)."""
    headers = {}

    screen_data = {
        "content_type": "html",
        "content": "<h1>Test Content</h1>",
        "filename": "test-screen",
        "width": 800,
        "height": 480,
    }

    response = client.post("/api/screens", headers=headers, json=screen_data)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert "image_url" in data
    assert "filename" in data


def test_current_screen_endpoint(client):
    """Test current screen endpoint (no auth required)."""
    headers = {"ID": "AA:BB:CC:DD:EE:FF"}

    response = client.get("/api/current_screen", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == 0
    assert "image_url" in data
