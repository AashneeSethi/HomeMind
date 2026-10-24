from datetime import datetime, timezone
from typing import Optional
from backend.models.events import HomeEvent
from backend.models.home_state import HomeState, DeviceState


class ContextManager:
    """
    Maintains the current contextual state of the smart home (HomeState).
    Tracks occupancy mode, active devices, open alerts, and ambient context.
    """

    def __init__(self, initial_state: Optional[HomeState] = None):
        self._state = initial_state or HomeState()

    def get_state(self) -> HomeState:
        """Return the current snapshot of HomeState."""
        return self._state.model_copy(deep=True)

    def set_occupancy_mode(self, mode: str) -> HomeState:
        """Update occupancy mode ('home', 'away', 'sleep', 'focus')."""
        valid_modes = {"home", "away", "sleep", "focus"}
        normalized = mode.lower().strip()
        if normalized in valid_modes:
            self._state.occupancy_mode = normalized
        else:
            self._state.occupancy_mode = normalized

        self._state.updated_at = datetime.now(timezone.utc)
        self._update_summary()
        return self.get_state()

    def update_from_event(self, event: HomeEvent) -> HomeState:
        """
        Incorporate an incoming event into the ambient home context.
        Updates device last_seen, active alerts, and context summary.
        """
        now = datetime.now(timezone.utc)
        self._state.last_event_timestamp = event.timestamp

        # Update or register device snapshot
        device = self._state.devices.get(event.device_id)
        if device:
            device.last_seen = event.timestamp
            device.attributes.update(event.metadata)
            device.location = event.location
        else:
            self._state.devices[event.device_id] = DeviceState(
                device_id=event.device_id,
                device_type=event.source,
                status="online",
                location=event.location,
                last_seen=event.timestamp,
                attributes=event.metadata
            )

        # Update alert state if applicable
        if self._state.occupancy_mode == "away" and "motion" in event.event_type.lower():
            alert_msg = f"Unexpected motion detected at {event.location} while in 'away' mode."
            if alert_msg not in self._state.active_alerts:
                self._state.active_alerts.append(alert_msg)

        self._state.updated_at = now
        self._update_summary(last_event=event)
        return self.get_state()

    def add_alert(self, alert: str) -> None:
        """Add an active alert."""
        if alert not in self._state.active_alerts:
            self._state.active_alerts.append(alert)
            self._state.updated_at = datetime.now(timezone.utc)
            self._update_summary()

    def clear_alert(self, alert_id: str) -> bool:
        """
        Remove a resolved alert by exact string, ID, or substring match.
        Returns True if an alert was removed, False otherwise.
        """
        # Exact match
        if alert_id in self._state.active_alerts:
            self._state.active_alerts.remove(alert_id)
            self._state.updated_at = datetime.now(timezone.utc)
            self._update_summary()
            return True

        # Special "all" keyword
        if alert_id.lower() == "all" and self._state.active_alerts:
            self._state.active_alerts.clear()
            self._state.updated_at = datetime.now(timezone.utc)
            self._update_summary()
            return True

        # Substring / fuzzy match
        target_lower = alert_id.lower().strip()
        for alert in list(self._state.active_alerts):
            if target_lower in alert.lower():
                self._state.active_alerts.remove(alert)
                self._state.updated_at = datetime.now(timezone.utc)
                self._update_summary()
                return True

        return False

    def reset(self) -> None:
        """Reset state to baseline."""
        self._state = HomeState()

    def _update_summary(self, last_event: Optional[HomeEvent] = None) -> None:
        """Recompute a human-readable summary of the current context."""
        alerts_count = len(self._state.active_alerts)
        devices_count = len(self._state.devices)
        mode = self._state.occupancy_mode

        parts = [f"Mode: '{mode}'", f"{devices_count} active device(s)"]
        if alerts_count > 0:
            parts.append(f"{alerts_count} active alert(s): {'; '.join(self._state.active_alerts)}")
        else:
            parts.append("No active alerts.")

        if last_event:
            parts.append(f"Last event: {last_event.event_type} at {last_event.location}")

        self._state.context_summary = " | ".join(parts)
