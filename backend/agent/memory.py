from collections import deque
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from backend.models.events import HomeEvent
from backend.models.actions import AgentAction
from backend.models.home_state import TemporaryWatch


class MemoryManager:
    """
    Manages short-term operational memory (recent events and actions),
    temporary watch intentions, and long-term user preferences/habits.

    This abstraction decouples the in-memory agent logic from underlying storage,
    paving the way for future persistent stores (e.g. AWS DynamoDB, SQLite, or Vector Memory).
    """

    def __init__(self, max_event_history: int = 100, max_action_history: int = 100):
        self._events: deque[HomeEvent] = deque(maxlen=max_event_history)
        self._actions: deque[AgentAction] = deque(maxlen=max_action_history)
        self._watches: Dict[str, TemporaryWatch] = {}
        self._user_preferences: Dict[str, Any] = {
            "quiet_hours_enabled": False,
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "07:00",
            "primary_voice_device": "alexa",
            "primary_visual_device": "firetv",
            "notify_on_all_doorbell_events": True,
            "interrupt_during_focus": False,
        }

    # Short-term event memory
    def record_event(self, event: HomeEvent) -> None:
        """Append an event to short-term memory buffer."""
        self._events.append(event)

    def get_recent_events(
        self, limit: int = 10, event_type: Optional[str] = None
    ) -> List[HomeEvent]:
        """Retrieve recent events, optionally filtered by event type."""
        events = list(self._events)
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return events[-limit:]

    # Temporary watch management
    def create_watch(
        self,
        location: str,
        duration_minutes: int,
        event_types: Optional[List[str]] = None,
    ) -> TemporaryWatch:
        """Create and register a temporary watch request."""
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=duration_minutes)
        watch = TemporaryWatch(
            location=location,
            duration_minutes=duration_minutes,
            event_types=event_types,
            created_at=now,
            expires_at=expires_at,
        )
        self._watches[watch.watch_id] = watch
        return watch

    def add_watch(self, watch: TemporaryWatch) -> TemporaryWatch:
        """Add an existing TemporaryWatch object."""
        self._watches[watch.watch_id] = watch
        return watch

    def get_watch(self, watch_id: str) -> Optional[TemporaryWatch]:
        """Retrieve a watch by ID."""
        return self._watches.get(watch_id)

    def get_active_watches(
        self, current_time: Optional[datetime] = None
    ) -> List[TemporaryWatch]:
        """Retrieve currently active watches, filtering out expired ones."""
        now = current_time or datetime.now(timezone.utc)
        return [w for w in self._watches.values() if w.is_active(now)]

    def clear_expired_watches(
        self, current_time: Optional[datetime] = None
    ) -> List[TemporaryWatch]:
        """Remove and return expired watches."""
        now = current_time or datetime.now(timezone.utc)
        expired = [w for w in self._watches.values() if not w.is_active(now)]
        for w in expired:
            self._watches.pop(w.watch_id, None)
        return expired

    # Short-term action history
    def record_action(self, action: AgentAction) -> None:
        """Append an agent action to recent action buffer."""
        self._actions.append(action)

    def get_recent_actions(self, limit: int = 10) -> List[AgentAction]:
        """Retrieve recent agent actions."""
        return list(self._actions)[-limit:]

    # Long-term preference storage abstraction
    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """Retrieve a user preference or default."""
        return self._user_preferences.get(key, default)

    def set_user_preference(self, key: str, value: Any) -> None:
        """Update or insert a user preference."""
        self._user_preferences[key] = value

    def get_all_preferences(self) -> Dict[str, Any]:
        """Return a copy of all user preferences."""
        return dict(self._user_preferences)

    def clear(self) -> None:
        """Clear memory buffers (useful for testing)."""
        self._events.clear()
        self._actions.clear()
        self._watches.clear()
