import pytest
from backend.agent.planner import AgentPlanner
from backend.mcp.server import create_mcp_server
from backend.models.events import HomeEvent
from backend.simulator.agent import SimulatedAlexaAgent


@pytest.fixture
def clean_planner():
    """Create an isolated AgentPlanner instance."""
    return AgentPlanner()


@pytest.mark.anyio
async def test_mcp_server_initialization_and_tool_registration(clean_planner):
    """Verify MCP server starts and all 6 required tools are registered."""
    server = create_mcp_server(planner=clean_planner)
    tools = await server.list_tools()
    tool_names = {t.name for t in tools}

    required_tools = {
        "get_home_status",
        "what_happened",
        "set_home_mode",
        "set_temporary_watch",
        "get_recent_events",
        "clear_alert",
    }
    assert required_tools.issubset(tool_names), f"Missing tools: {required_tools - tool_names}"


@pytest.mark.anyio
async def test_mcp_get_home_status(clean_planner):
    """Verify get_home_status returns structured HomeStatusOutput."""
    server = create_mcp_server(planner=clean_planner)
    result = await server.call_tool("get_home_status", {})
    assert not result.is_error

    data = result.structured_content
    assert data["occupancy_mode"] == "home"
    assert data["devices_count"] == 0
    assert "home" in data["message"].lower()


@pytest.mark.anyio
async def test_mcp_what_happened_filtering_by_location(clean_planner):
    """Verify what_happened filters by location."""
    # Ingest two events with different locations
    evt1 = HomeEvent(
        event_type="motion_detected",
        source="ring",
        device_id="cam_front",
        location="front_door",
    )
    evt2 = HomeEvent(
        event_type="motion_detected",
        source="sensor",
        device_id="sensor_back",
        location="backyard",
    )
    await clean_planner.process_event(evt1)
    await clean_planner.process_event(evt2)

    server = create_mcp_server(planner=clean_planner)

    # Filter for front_door
    res_front = await server.call_tool("what_happened", {"location": "front_door"})
    data_front = res_front.structured_content
    assert data_front["events_count"] == 1
    assert data_front["events"][0]["location"] == "front_door"
    assert "front_door" in data_front["summary"]

    # Filter for non-existent location
    res_garage = await server.call_tool("what_happened", {"location": "garage"})
    data_garage = res_garage.structured_content
    assert data_garage["events_count"] == 0
    assert "No events recorded" in data_garage["summary"]


@pytest.mark.anyio
async def test_mcp_set_home_mode(clean_planner):
    """Verify set_home_mode updates ContextManager state."""
    server = create_mcp_server(planner=clean_planner)
    result = await server.call_tool("set_home_mode", {"mode": "focus"})
    assert not result.is_error
    data = result.structured_content
    assert data["new_mode"] == "focus"
    assert data["previous_mode"] == "home"

    # Context should be updated
    assert clean_planner.context.get_state().occupancy_mode == "focus"


@pytest.mark.anyio
async def test_mcp_get_recent_events(clean_planner):
    """Verify get_recent_events returns events from operational memory."""
    evt = HomeEvent(
        event_type="doorbell_press",
        source="ring",
        device_id="ring_doorbell",
        location="front_door",
    )
    await clean_planner.process_event(evt)

    server = create_mcp_server(planner=clean_planner)
    result = await server.call_tool("get_recent_events", {"limit": 5})
    assert not result.is_error
    data = result.structured_content
    assert data["count"] == 1
    assert data["events"][0]["event_type"] == "doorbell_press"


@pytest.mark.anyio
async def test_mcp_clear_alert(clean_planner):
    """Verify clear_alert clears active alert."""
    clean_planner.context.add_alert("Unauthorized movement detected.")
    assert len(clean_planner.context.get_state().active_alerts) == 1

    server = create_mcp_server(planner=clean_planner)
    result = await server.call_tool("clear_alert", {"alert_id": "movement"})
    assert not result.is_error
    data = result.structured_content
    assert data["cleared"] is True
    assert len(clean_planner.context.get_state().active_alerts) == 0


@pytest.mark.anyio
async def test_simulated_alexa_agent_utterances(clean_planner):
    """Verify natural-language utterance parsing in the Alexa+ simulator."""
    agent = SimulatedAlexaAgent(planner=clean_planner)

    # 1. "What is happening at home?"
    resp1 = await agent.handle_utterance("What is happening at home?")
    assert resp1.tool_called == "get_home_status"
    assert "home" in resp1.spoken_response.lower()

    # 2. "Set the home to focus mode."
    resp2 = await agent.handle_utterance("Set the home to focus mode.")
    assert resp2.tool_called == "set_home_mode"
    assert resp2.tool_parameters["mode"] == "focus"
    assert clean_planner.context.get_state().occupancy_mode == "focus"

    # 3. "Watch the front door for 30 minutes."
    resp3 = await agent.handle_utterance("Watch the front door for 30 minutes.")
    assert resp3.tool_called == "set_temporary_watch"
    assert resp3.tool_parameters["location"] == "front_door"
    assert resp3.tool_parameters["duration_minutes"] == 30
    assert len(clean_planner.memory.get_active_watches()) == 1

    # 4. "What happened at the front door?"
    resp4 = await agent.handle_utterance("What happened at the front door?")
    assert resp4.tool_called == "what_happened"
    assert resp4.tool_parameters["location"] == "front_door"

    # 5. "Show me recent events."
    resp5 = await agent.handle_utterance("Show me recent events.")
    assert resp5.tool_called == "get_recent_events"
