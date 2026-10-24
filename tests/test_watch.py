from datetime import datetime, timezone, timedelta
import pytest
from backend.agent.planner import AgentPlanner
from backend.models.actions import DecisionType
from backend.models.home_state import TemporaryWatch
from backend.simulator.agent import SimulatedAlexaAgent
from backend.simulator.events import create_doorbell_event, create_motion_event, dispatch_simulated_event


@pytest.fixture
def clean_planner():
    return AgentPlanner()


def test_set_temporary_watch_creation(clean_planner):
    """Verify temporary watch is created and stored in MemoryManager."""
    watch = clean_planner.memory.create_watch(
        location="front_door",
        duration_minutes=30,
        event_types=["motion_detected", "doorbell_press"],
    )
    assert watch.location == "front_door"
    assert watch.duration_minutes == 30
    assert watch.is_active() is True
    assert len(clean_planner.memory.get_active_watches()) == 1


@pytest.mark.anyio
async def test_matching_event_triggers_watch_notification(clean_planner):
    """Verify a matching event on a watched location triggers a NOTIFY_USER action."""
    # 1. User sets a watch on front_door
    clean_planner.memory.create_watch(
        location="front_door",
        duration_minutes=30,
    )

    # 2. Simulated Ring motion event arrives at front_door
    event = create_motion_event(location="front_door", device_id="ring_cam_front")
    action = await clean_planner.process_event(event)

    # 3. Decision should notify user because of the active watch
    assert action.decision == DecisionType.NOTIFY_USER
    assert action.target_device == "alexa"
    assert "active temporary watch" in action.reasoning.lower()
    assert action.payload["location"] == "front_door"


@pytest.mark.anyio
async def test_unrelated_event_does_not_trigger_watch(clean_planner):
    """Verify an event at a different location does not trigger the watch notification."""
    # 1. User sets a watch on front_door
    clean_planner.memory.create_watch(
        location="front_door",
        duration_minutes=30,
    )

    # 2. Event occurs at living_room (unwatched location) in normal home mode
    event = create_motion_event(location="living_room", device_id="sensor_living_room")
    action = await clean_planner.process_event(event)

    # 3. Should update context only, NOT trigger the front_door watch notification
    assert action.decision == DecisionType.UPDATE_CONTEXT_ONLY
    assert "temporary watch" not in action.reasoning.lower()


@pytest.mark.anyio
async def test_expired_watch_does_not_trigger(clean_planner):
    """Verify that an expired watch is ignored and does not trigger notifications."""
    now = datetime.now(timezone.utc)
    # Manually create an already expired watch
    expired_watch = TemporaryWatch(
        location="front_door",
        duration_minutes=10,
        created_at=now - timedelta(minutes=20),
        expires_at=now - timedelta(minutes=10),
    )
    clean_planner.memory.add_watch(expired_watch)
    assert expired_watch.is_active(now) is False

    # Dispatch event at front_door
    event = create_motion_event(location="front_door", timestamp=now)
    action = await clean_planner.process_event(event)

    # Normal home mode routine motion updates context only; expired watch must not fire
    assert action.decision == DecisionType.UPDATE_CONTEXT_ONLY
    assert "temporary watch" not in action.reasoning.lower()


@pytest.mark.anyio
async def test_end_to_end_agentic_loop(clean_planner):
    """
    Test complete end-to-end loop:
    1. User natural language voice utterance to Alexa+ simulator
    2. Simulator maps command to MCP tool `set_temporary_watch`
    3. Simulated Ring event arrives
    4. HomeMind cognitive pipeline matches active watch
    5. HomeMind dispatches proactive AgentAction
    """
    agent = SimulatedAlexaAgent(planner=clean_planner)

    # Step 1 & 2: User voice command
    sim_resp = await agent.handle_utterance("Watch the front door for 45 minutes.")
    assert sim_resp.tool_called == "set_temporary_watch"
    assert len(clean_planner.memory.get_active_watches()) == 1

    # Step 3: Simulated Ring doorbell event arrives
    doorbell_evt = create_doorbell_event(location="front_door")

    # Step 4 & 5: Event dispatch & evaluation
    action = await dispatch_simulated_event(doorbell_evt, planner=clean_planner)

    assert action.decision == DecisionType.NOTIFY_USER
    assert action.target_device == "alexa"
    assert "active temporary watch" in action.reasoning.lower()
