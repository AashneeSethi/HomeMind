from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


# --- Tool 1: get_home_status ---
class GetHomeStatusInput(BaseModel):
    """Input parameters for get_home_status."""
    pass


class HomeStatusOutput(BaseModel):
    """Current home state snapshot and summary."""
    occupancy_mode: str
    active_alerts: List[str]
    devices_count: int
    devices: Dict[str, Any]
    context_summary: str
    last_event_timestamp: Optional[str] = None
    message: str


# --- Tool 2: what_happened ---
class WhatHappenedInput(BaseModel):
    """Input parameters for what_happened."""
    location: Optional[str] = Field(
        default=None,
        description="Optional filter for specific location, e.g. 'front_door', 'backyard'"
    )
    since_minutes: Optional[int] = Field(
        default=None,
        description="Optional time window in minutes to look back"
    )


class WhatHappenedOutput(BaseModel):
    """Natural-language summary and structured event list."""
    summary: str
    events_count: int
    events: List[Dict[str, Any]]


# --- Tool 3: set_home_mode ---
class SetHomeModeInput(BaseModel):
    """Input parameters for set_home_mode."""
    mode: Literal["home", "away", "sleep", "focus"] = Field(
        ...,
        description="Target occupancy mode: 'home', 'away', 'sleep', or 'focus'"
    )


class SetHomeModeOutput(BaseModel):
    """Result of changing home occupancy mode."""
    previous_mode: str
    new_mode: str
    success: bool
    message: str


# --- Tool 4: set_temporary_watch ---
class SetTemporaryWatchInput(BaseModel):
    """Input parameters for set_temporary_watch."""
    location: str = Field(
        ...,
        description="Location to temporarily monitor, e.g. 'front_door', 'patio'"
    )
    duration_minutes: int = Field(
        ...,
        ge=1,
        description="Duration of the watch in minutes"
    )
    event_types: Optional[List[str]] = Field(
        default=None,
        description="Optional list of event types to trigger on, e.g. ['motion', 'doorbell']"
    )


class SetTemporaryWatchOutput(BaseModel):
    """Confirmation of registered temporary watch."""
    watch_id: str
    location: str
    duration_minutes: int
    event_types: Optional[List[str]]
    expires_at: str
    message: str


# --- Tool 5: get_recent_events ---
class GetRecentEventsInput(BaseModel):
    """Input parameters for get_recent_events."""
    limit: Optional[int] = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of recent events to return"
    )


class RecentEventsOutput(BaseModel):
    """List of recent home events."""
    count: int
    events: List[Dict[str, Any]]
    message: str


# --- Tool 6: clear_alert ---
class ClearAlertInput(BaseModel):
    """Input parameters for clear_alert."""
    alert_id: str = Field(
        ...,
        description="Alert ID, text substring to match and clear, or 'all'"
    )


class ClearAlertOutput(BaseModel):
    """Result of clearing an alert."""
    alert_id: str
    cleared: bool
    remaining_alerts: List[str]
    message: str
