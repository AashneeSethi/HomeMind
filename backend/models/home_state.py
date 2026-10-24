from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DeviceState(BaseModel):
    """Snapshot of an individual device's reported state."""
    device_id: str
    device_type: str
    status: str = "online"
    location: str = "unknown"
    last_seen: datetime = Field(default_factory=get_utc_now)
    attributes: Dict[str, Any] = Field(default_factory=dict)


class TemporaryWatch(BaseModel):
    """
    User intention for temporary focused monitoring of a specific location/event.
    Expires automatically after duration_minutes.
    """
    watch_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    location: str = Field(..., description="Target location to monitor, e.g. 'front_door'")
    duration_minutes: int = Field(..., description="Duration of watch in minutes")
    event_types: Optional[List[str]] = Field(
        default=None,
        description="Optional filter for specific event types, e.g. ['motion', 'doorbell']"
    )
    created_at: datetime = Field(default_factory=get_utc_now)
    expires_at: datetime = Field(default_factory=get_utc_now)

    def is_active(self, current_time: Optional[datetime] = None) -> bool:
        now = current_time or datetime.now(timezone.utc)
        return now < self.expires_at

    def matches(self, location: str, event_type: str, current_time: Optional[datetime] = None) -> bool:
        if not self.is_active(current_time):
            return False
        if self.location.lower().strip() != location.lower().strip():
            return False
        if self.event_types:
            event_type_lower = event_type.lower()
            return any(t.lower() in event_type_lower for t in self.event_types)
        return True


class HomeState(BaseModel):
    """
    Current context and state of the home as tracked by HomeMind ContextManager.
    """
    occupancy_mode: str = Field(
        default="home",
        description="Current occupancy/focus mode: 'home', 'away', 'sleep', 'focus'"
    )
    active_alerts: List[str] = Field(
        default_factory=list,
        description="List of unresolved alerts or security conditions"
    )
    last_event_timestamp: Optional[datetime] = Field(
        default=None,
        description="Timestamp of the most recently processed event"
    )
    devices: Dict[str, DeviceState] = Field(
        default_factory=dict,
        description="Map of device ID to device status snapshot"
    )
    context_summary: str = Field(
        default="Home is in normal home occupancy mode. No active alerts.",
        description="High-level human-readable context summary"
    )
    updated_at: datetime = Field(
        default_factory=get_utc_now,
        description="UTC timestamp of the last state update"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "occupancy_mode": "home",
                "active_alerts": [],
                "context_summary": "All systems normal. 1 active sensor.",
                "devices": {}
            }
        }
    }
