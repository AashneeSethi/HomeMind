from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.models.events import HomeEvent
from backend.models.home_state import HomeState, TemporaryWatch
from backend.models.actions import DecisionType


@dataclass
class DecisionEvaluation:
    """Outcome of a DecisionEngine evaluation."""
    decision: DecisionType
    target_device: Optional[str] = None
    action_type: str = "log_only"
    reasoning: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)


class DecisionEngine:
    """
    Core context-aware decision logic for HomeMind.

    Determines:
    1. What happened
    2. Whether it matters in the current home context
    3. Whether the user should be interrupted
    4. What information or action is appropriate
    5. Which device should communicate it (Alexa for conversational/voice,
       Fire TV for visual/overlay, or silent context tracking)
    """

    def evaluate(
        self,
        event: HomeEvent,
        context: HomeState,
        recent_events: List[HomeEvent],
        preferences: Optional[Dict[str, Any]] = None,
        active_watches: Optional[List[TemporaryWatch]] = None,
    ) -> DecisionEvaluation:
        """
        Evaluate an incoming event against current HomeState, recent event history,
        user preferences, and active temporary watches.
        """
        preferences = preferences or {}
        event_type = event.event_type.lower()
        occupancy = context.occupancy_mode.lower()
        location = event.location.lower()

        # Rule 1: High severity emergency / security alerts (fire, leak, glass break)
        if any(keyword in event_type for keyword in ["smoke", "fire", "leak", "alarm", "intrusion"]):
            return DecisionEvaluation(
                decision=DecisionType.TRIGGER_ACTION,
                target_device="alexa",
                action_type="speak_and_alert",
                reasoning=f"Critical event '{event.event_type}' detected at {event.location}. Immediate user interruption required.",
                payload={
                    "message": f"Emergency alert: {event.event_type} detected at {event.location}.",
                    "priority": "critical",
                    "sound_alarm": True,
                },
            )

        # Rule 2: Active temporary watch matching event
        if active_watches:
            for watch in active_watches:
                if watch.matches(location=event.location, event_type=event.event_type):
                    return DecisionEvaluation(
                        decision=DecisionType.NOTIFY_USER,
                        target_device="alexa",
                        action_type="speak",
                        reasoning=f"Event '{event.event_type}' at {event.location} matched active temporary watch (watch_id={watch.watch_id}).",
                        payload={
                            "message": f"Watch alert: Activity detected at {event.location}.",
                            "watch_id": watch.watch_id,
                            "event_type": event.event_type,
                            "location": event.location,
                        },
                    )

        # Rule 3: Doorbell press (e.g. Ring doorbell)
        if "doorbell" in event_type or "door_chime" in event_type:
            if occupancy == "focus":
                # In focus mode: visual overlay on Fire TV, do not speak out loud
                return DecisionEvaluation(
                    decision=DecisionType.NOTIFY_USER,
                    target_device="firetv",
                    action_type="display_overlay",
                    reasoning="Doorbell pressed while user is in focus mode. Suppressing voice prompt, displaying subtle Fire TV visual card.",
                    payload={
                        "message": "Visitor at the front door.",
                        "overlay_type": "pip_banner",
                        "duration_seconds": 15,
                    },
                )
            else:
                # Normal or away mode: announce on Alexa voice assistant
                return DecisionEvaluation(
                    decision=DecisionType.NOTIFY_USER,
                    target_device="alexa",
                    action_type="speak",
                    reasoning=f"Doorbell pressed in '{occupancy}' mode. Prompting user via primary voice interface.",
                    payload={
                        "message": "Someone is at the front door.",
                        "chime": True,
                    },
                )

        # Rule 4: Motion detection
        if "motion" in event_type:
            # Check for recent motion from the same device to debounce noise
            similar_recent = [
                e for e in recent_events
                if e.device_id == event.device_id and "motion" in e.event_type.lower()
            ]
            if len(similar_recent) >= 2:
                # Too recent, frequent motion flutter -> ignore
                return DecisionEvaluation(
                    decision=DecisionType.IGNORE,
                    target_device=None,
                    action_type="noop",
                    reasoning=f"Repeated motion flutter from {event.device_id} at {event.location}. Suppressed as noise.",
                    payload={},
                )

            # Away mode: unexpected motion is significant
            if occupancy == "away":
                return DecisionEvaluation(
                    decision=DecisionType.NOTIFY_USER,
                    target_device="alexa",
                    action_type="speak",
                    reasoning=f"Unexpected motion detected at {event.location} while home mode is 'away'.",
                    payload={
                        "message": f"Alert: Motion detected at {event.location} while away.",
                        "urgency": "high",
                    },
                )

            # Sleep mode: exterior motion triggers alert, interior motion updates context only
            if occupancy == "sleep":
                if any(ext in location for ext in ["front", "back", "porch", "patio", "yard", "garage"]):
                    return DecisionEvaluation(
                        decision=DecisionType.NOTIFY_USER,
                        target_device="alexa",
                        action_type="speak",
                        reasoning=f"Perimeter motion at {event.location} during sleep mode warrants alert.",
                        payload={
                            "message": f"Notice: Motion detected outside at {event.location}.",
                            "volume": "low",
                        },
                    )
                else:
                    return DecisionEvaluation(
                        decision=DecisionType.UPDATE_CONTEXT_ONLY,
                        target_device=None,
                        action_type="update_state",
                        reasoning=f"Interior motion at {event.location} during sleep mode. User is active; updating context without disturbing.",
                        payload={"activity": "interior_movement"},
                    )

            # Home / Normal mode: routine presence tracking
            return DecisionEvaluation(
                decision=DecisionType.UPDATE_CONTEXT_ONLY,
                target_device=None,
                action_type="update_state",
                reasoning=f"Routine motion in {event.location} during normal home occupancy. Context updated.",
                payload={"activity": "normal_presence"},
            )

        # Rule 5: Routine background telemetry / heartbeat / sensor readings
        if any(keyword in event_type for keyword in ["heartbeat", "ping", "temp", "battery", "status"]):
            return DecisionEvaluation(
                decision=DecisionType.UPDATE_CONTEXT_ONLY,
                target_device=None,
                action_type="update_telemetry",
                reasoning=f"Sensor telemetry '{event.event_type}' recorded into state.",
                payload=event.metadata,
            )

        # Default fallback: update context only
        return DecisionEvaluation(
            decision=DecisionType.UPDATE_CONTEXT_ONLY,
            target_device=None,
            action_type="record_event",
            reasoning=f"Generic event '{event.event_type}' noted in context; no user interruption required.",
            payload=event.metadata,
        )
