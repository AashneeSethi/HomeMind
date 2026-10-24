from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from backend.agent.planner import AgentPlanner
from backend.api.deps import get_planner
from backend.mcp.schemas import (
    ClearAlertOutput,
    HomeStatusOutput,
    RecentEventsOutput,
    SetHomeModeOutput,
    SetTemporaryWatchOutput,
    WhatHappenedOutput,
)


def get_home_status_impl(planner: Optional[AgentPlanner] = None) -> HomeStatusOutput:
    """Execute get_home_status tool logic."""
    p = planner or get_planner()
    state = p.context.get_state()
    devices_data = {
        d_id: d.model_dump(mode="json")
        for d_id, d in state.devices.items()
    }
    alerts_str = f" Active alerts: {', '.join(state.active_alerts)}." if state.active_alerts else " No active alerts."
    message = f"Home is currently in '{state.occupancy_mode}' mode with {len(state.devices)} known device(s).{alerts_str}"

    return HomeStatusOutput(
        occupancy_mode=state.occupancy_mode,
        active_alerts=list(state.active_alerts),
        devices_count=len(state.devices),
        devices=devices_data,
        context_summary=state.context_summary,
        last_event_timestamp=state.last_event_timestamp.isoformat() if state.last_event_timestamp else None,
        message=message,
    )


def what_happened_impl(
    location: Optional[str] = None,
    since_minutes: Optional[int] = None,
    planner: Optional[AgentPlanner] = None,
) -> WhatHappenedOutput:
    """Execute what_happened tool logic with optional location and time filters."""
    p = planner or get_planner()
    all_recent = p.memory.get_recent_events(limit=50)
    now = datetime.now(timezone.utc)

    filtered = []
    for evt in all_recent:
        # Location filter
        if location and location.lower().strip() not in evt.location.lower().strip():
            continue
        # Time filter
        if since_minutes is not None:
            cutoff = now - timedelta(minutes=since_minutes)
            if evt.timestamp < cutoff:
                continue
        filtered.append(evt)

    events_data = [e.model_dump(mode="json") for e in filtered]

    if not filtered:
        loc_msg = f" at {location}" if location else ""
        time_msg = f" in the last {since_minutes} minute(s)" if since_minutes else ""
        summary = f"No events recorded{loc_msg}{time_msg}."
    else:
        event_descriptions = [f"{e.event_type} at {e.location}" for e in filtered[-5:]]
        loc_msg = f" for {location}" if location else ""
        summary = f"Found {len(filtered)} event(s){loc_msg}: {', '.join(event_descriptions)}."

    return WhatHappenedOutput(
        summary=summary,
        events_count=len(filtered),
        events=events_data,
    )


def set_home_mode_impl(
    mode: str,
    planner: Optional[AgentPlanner] = None,
) -> SetHomeModeOutput:
    """Execute set_home_mode tool logic."""
    p = planner or get_planner()
    prev_state = p.context.get_state()
    prev_mode = prev_state.occupancy_mode

    new_state = p.context.set_occupancy_mode(mode)
    msg = f"Occupancy mode successfully changed from '{prev_mode}' to '{new_state.occupancy_mode}'."

    return SetHomeModeOutput(
        previous_mode=prev_mode,
        new_mode=new_state.occupancy_mode,
        success=True,
        message=msg,
    )


def set_temporary_watch_impl(
    location: str,
    duration_minutes: int,
    event_types: Optional[List[str]] = None,
    planner: Optional[AgentPlanner] = None,
) -> SetTemporaryWatchOutput:
    """Execute set_temporary_watch tool logic."""
    p = planner or get_planner()
    watch = p.memory.create_watch(
        location=location,
        duration_minutes=duration_minutes,
        event_types=event_types,
    )

    types_str = f" for [{', '.join(event_types)}]" if event_types else " for all activities"
    msg = (
        f"Temporary watch established on {location}{types_str}. "
        f"Active for {duration_minutes} minute(s) until {watch.expires_at.strftime('%H:%M:%S UTC')}."
    )

    return SetTemporaryWatchOutput(
        watch_id=watch.watch_id,
        location=watch.location,
        duration_minutes=watch.duration_minutes,
        event_types=watch.event_types,
        expires_at=watch.expires_at.isoformat(),
        message=msg,
    )


def get_recent_events_impl(
    limit: Optional[int] = 10,
    planner: Optional[AgentPlanner] = None,
) -> RecentEventsOutput:
    """Execute get_recent_events tool logic."""
    p = planner or get_planner()
    lim = limit or 10
    events = p.memory.get_recent_events(limit=lim)
    events_data = [e.model_dump(mode="json") for e in events]
    msg = f"Retrieved {len(events)} recent event(s) from memory."

    return RecentEventsOutput(
        count=len(events),
        events=events_data,
        message=msg,
    )


def clear_alert_impl(
    alert_id: str,
    planner: Optional[AgentPlanner] = None,
) -> ClearAlertOutput:
    """Execute clear_alert tool logic."""
    p = planner or get_planner()
    cleared = p.context.clear_alert(alert_id)
    state = p.context.get_state()

    if cleared:
        msg = f"Alert '{alert_id}' has been cleared."
    else:
        msg = f"No active alert matching '{alert_id}' was found."

    return ClearAlertOutput(
        alert_id=alert_id,
        cleared=cleared,
        remaining_alerts=list(state.active_alerts),
        message=msg,
    )
