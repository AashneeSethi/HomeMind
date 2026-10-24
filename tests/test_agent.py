from backend.agent.context import ContextManager
from backend.agent.decisions import DecisionEngine
from backend.agent.memory import MemoryManager
from backend.models.actions import DecisionType
from backend.models.events import HomeEvent
from backend.models.home_state import HomeState


def test_decision_emergency_triggers_action():
    """Critical alarms must trigger immediate action/interruption."""
    engine = DecisionEngine()
    context = HomeState(occupancy_mode="home")
    event = HomeEvent(
        event_type="smoke_alarm_triggered",
        source="sensor",
        device_id="smoke_detector_kitchen",
        location="kitchen",
    )
    decision = engine.evaluate(event=event, context=context, recent_events=[])
    assert decision.decision == DecisionType.TRIGGER_ACTION
    assert decision.target_device == "alexa"
    assert "critical" in decision.reasoning.lower() or "emergency" in decision.reasoning.lower()


def test_decision_routine_motion_updates_context_only():
    """Normal daytime motion inside the house should update context without disturbing the user."""
    engine = DecisionEngine()
    context = HomeState(occupancy_mode="home")
    event = HomeEvent(
        event_type="motion_detected",
        source="sensor",
        device_id="living_room_motion",
        location="living_room",
    )
    decision = engine.evaluate(event=event, context=context, recent_events=[])
    assert decision.decision == DecisionType.UPDATE_CONTEXT_ONLY
    assert decision.target_device is None


def test_decision_repeated_motion_is_ignored():
    """Rapid repeated sensor flutter from same device should be debounced and ignored."""
    engine = DecisionEngine()
    context = HomeState(occupancy_mode="home")
    recent = [
        HomeEvent(
            event_type="motion_detected",
            source="sensor",
            device_id="porch_cam",
            location="porch",
        ),
        HomeEvent(
            event_type="motion_detected",
            source="sensor",
            device_id="porch_cam",
            location="porch",
        ),
    ]
    event = HomeEvent(
        event_type="motion_detected",
        source="sensor",
        device_id="porch_cam",
        location="porch",
    )
    decision = engine.evaluate(event=event, context=context, recent_events=recent)
    assert decision.decision == DecisionType.IGNORE
    assert "noise" in decision.reasoning.lower() or "suppressed" in decision.reasoning.lower()


def test_decision_doorbell_in_focus_mode_routes_to_firetv():
    """During focus mode, doorbell notification is routed visually to Fire TV rather than spoken by Alexa."""
    engine = DecisionEngine()
    context = HomeState(occupancy_mode="focus")
    event = HomeEvent(
        event_type="doorbell_press",
        source="ring",
        device_id="front_doorbell",
        location="front_door",
    )
    decision = engine.evaluate(event=event, context=context, recent_events=[])
    assert decision.decision == DecisionType.NOTIFY_USER
    assert decision.target_device == "firetv"
    assert "focus mode" in decision.reasoning.lower()


def test_context_manager_state_transitions():
    """ContextManager correctly transitions modes and registers devices."""
    cm = ContextManager()
    state = cm.get_state()
    assert state.occupancy_mode == "home"

    cm.set_occupancy_mode("away")
    assert cm.get_state().occupancy_mode == "away"

    event = HomeEvent(
        event_type="motion_detected",
        source="ring",
        device_id="cam_backyard",
        location="backyard",
    )
    cm.update_from_event(event)
    updated = cm.get_state()
    assert "cam_backyard" in updated.devices
    assert len(updated.active_alerts) > 0  # Motion while away triggers alert
