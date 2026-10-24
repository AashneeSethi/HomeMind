from fastapi.testclient import TestClient
from backend.main import app
from backend.api.deps import reset_planner

client = TestClient(app)


def setup_function():
    reset_planner()


def test_command_change_mode():
    """Verify user voice/text command changes occupancy mode."""
    payload = {
        "command_text": "Set home mode to focus",
        "source": "alexa",
    }
    response = client.post("/commands", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "processed"
    assert data["home_state"]["occupancy_mode"] == "focus"
    assert "focus" in data["action"]["payload"]["message"]


def test_command_status_query():
    """Verify user query for home status returns current context summary."""
    payload = {
        "command_text": "What is the current home status?",
        "source": "alexa",
    }
    response = client.post("/commands", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "processed"
    assert data["action"]["action_type"] == "status_report"
    assert "Current status" in data["action"]["payload"]["message"]
