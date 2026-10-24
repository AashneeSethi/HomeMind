from fastapi.testclient import TestClient
from backend.main import app
from backend.api.deps import reset_planner

client = TestClient(app)


def setup_function():
    reset_planner()


def test_api_state_endpoint():
    """Verify GET /state returns detailed context and occupancy."""
    response = client.get("/state")
    assert response.status_code == 200
    data = response.json()
    assert data["occupancy_mode"] == "home"
    assert data["devices_count"] == 0
    assert "active_watches_count" in data


def test_api_simulate_event():
    """Verify POST /simulate/event triggers event through cognitive loop."""
    payload = {
        "event_type": "doorbell_press",
        "location": "front_door",
        "source": "ring",
        "metadata": {"camera": "active"},
    }
    response = client.post("/simulate/event", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"
    assert data["event"]["event_type"] == "doorbell_press"
    assert data["action"]["decision"] == "notify_user"
    assert data["action"]["target_device"] == "alexa"


def test_api_chat_alexa_simulator():
    """Verify POST /chat routes to SimulatedAlexaAgent and executes MCP tools."""
    # 1. Ask home status
    res1 = client.post("/chat", json={"message": "What is happening at home?"})
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["tool_called"] == "get_home_status"
    assert "home" in data1["reply"].lower()

    # 2. Set watch
    res2 = client.post("/chat", json={"message": "Watch the front door for 30 minutes."})
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["tool_called"] == "set_temporary_watch"
    assert "front_door" in data2["reply"].lower()

    # Verify watch appears in /watches
    watches_res = client.get("/watches")
    assert watches_res.status_code == 200
    watches = watches_res.json()
    assert len(watches) == 1
    assert watches[0]["location"] == "front_door"


def test_api_mode_and_alerts():
    """Verify mode switching and alert dismissal via API."""
    # Set mode to away
    mode_res = client.post("/mode", json={"mode": "away"})
    assert mode_res.status_code == 200
    assert mode_res.json()["occupancy_mode"] == "away"

    # Trigger motion while away -> causes alert
    sim_res = client.post("/simulate/event", json={
        "event_type": "motion_detected",
        "location": "backyard",
    })
    assert sim_res.status_code == 200

    # Check alert
    alerts_res = client.get("/alerts")
    assert alerts_res.status_code == 200
    alerts = alerts_res.json()
    assert len(alerts) > 0

    # Clear alert
    clear_res = client.post("/alerts/clear", json={"alert_id": "all"})
    assert clear_res.status_code == 200
    assert len(clear_res.json()["remaining_alerts"]) == 0
