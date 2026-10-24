from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid
from backend.agent.planner import AgentPlanner
from backend.api.deps import get_planner
from backend.models.actions import AgentAction
from backend.models.events import HomeEvent


def create_simulated_event(
    event_type: str,
    location: str = "front_door",
    source: str = "ring",
    device_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None,
) -> HomeEvent:
    """Factory helper to construct a simulated smart home event."""
    dev_id = device_id or f"{source}_{location}_{event_type}"
    return HomeEvent(
        event_id=f"sim-evt-{uuid.uuid4().hex[:8]}",
        event_type=event_type,
        source=source,
        device_id=dev_id,
        location=location,
        timestamp=timestamp or datetime.now(timezone.utc),
        metadata=metadata or {},
    )


def create_doorbell_event(
    location: str = "front_door",
    device_id: str = "ring_doorbell_front",
    metadata: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None,
) -> HomeEvent:
    """Generate a simulated Ring Doorbell press (ding) event."""
    meta = metadata or {"person_detected": True, "chime": True}
    return create_simulated_event(
        event_type="doorbell_press",
        location=location,
        source="ring",
        device_id=device_id,
        metadata=meta,
        timestamp=timestamp,
    )


def create_motion_event(
    location: str = "front_door",
    device_id: str = "ring_floodlight_front",
    person_detected: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None,
) -> HomeEvent:
    """Generate a simulated Ring perimeter motion event."""
    meta = metadata or {}
    meta["person_detected"] = person_detected
    return create_simulated_event(
        event_type="motion_detected",
        location=location,
        source="ring",
        device_id=device_id,
        metadata=meta,
        timestamp=timestamp,
    )


async def dispatch_simulated_event(
    event: HomeEvent,
    planner: Optional[AgentPlanner] = None,
) -> AgentAction:
    """
    Dispatch a simulated event into the HomeMind cognitive loop.
    Returns the resulting AgentAction.
    """
    p = planner or get_planner()
    return await p.process_event(event)
