from fastapi.testclient import TestClient
from backend.main import app
from backend.api.deps import reset_planner

client = TestClient(app)


def setup_function():
    """Reset agent state before each test."""
    reset_planner()


def test_event_ingestion_doorbell():
    """Verify posting a doorbell event routes to decision engine and returns an action."""
    payload = {
        "event_id": "test-doorbell-001",
        "event_type": "doorbell_press",
        "source": "ring",
        "device_id": "front_doorbell",
        "location": "front_door",
        "metadata": {"video_clip_available": True},
    }

    response = client.post("/events", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "processed"
    assert data["event_id"] == "test-doorbell-001"
    assert data["action"]["decision"] == "notify_user"
    assert data["action"]["target_device"] == "alexa"
    assert "doorbell" in data["action"]["reasoning"].lower()
    assert "front_doorbell" in data["home_state"]["devices"]


def test_event_ingestion_motion_in_away_mode():
    """Verify that mode-aware context changes decision outcome."""
    # First, switch mode to 'away' via command endpoint
    cmd_response = client.post(
        "/commands",
        json={"command_text": "Set home mode to away", "source": "alexa"},
    )
    assert cmd_response.status_code == 200
    assert cmd_response.json()["home_state"]["occupancy_mode"] == "away"

    # Now ingest motion event
    event_payload = {
        "event_id": "test-motion-away-002",
        "event_type": "motion_detected",
        "source": "ring",
        "device_id": "backyard_cam",
        "location": "backyard",
        "metadata": {"confidence": 0.92},
    }

    response = client.post("/events", json=event_payload)
    assert response.status_code == 200
    data = response.json()

    # In 'away' mode, motion triggers high urgency alert
    assert data["action"]["decision"] == "notify_user"
    assert "away" in data["action"]["reasoning"].lower()
    assert len(data["home_state"]["active_alerts"]) > 0


def test_get_recent_events():
    """Verify retrieving recent events list."""
    event_payload = {
        "event_id": "test-evt-recent-003",
        "event_type": "doorbell_press",
        "source": "ring",
        "device_id": "front_doorbell",
        "location": "front_door",
        "metadata": {},
    }
    client.post("/events", json=event_payload)

    response = client.get("/events/recent")
    assert response.status_code == 200
    events = response.json()
    assert len(events) >= 1
    assert any(e["event_id"] == "test-evt-recent-003" for e in events)
