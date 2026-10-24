from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid
from pydantic import BaseModel, Field


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class HomeEvent(BaseModel):
    """
    Represents an event occurring within the smart home environment.
    Sources can include sensors, doorbells, cameras (e.g. Ring), or user inputs.
    """
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = Field(..., description="Type of event, e.g. 'motion_detected', 'doorbell_press', 'door_open'")
    source: str = Field(..., description="Origin of event, e.g. 'ring', 'alexa', 'sensor', 'simulator'")
    device_id: str = Field(..., description="ID of the device that generated the event")
    location: str = Field(..., description="Location of the event, e.g. 'front_door', 'living_room', 'backyard'")
    timestamp: datetime = Field(default_factory=get_utc_now, description="UTC timestamp of the event")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary event-specific payload")

    model_config = {
        "json_schema_extra": {
            "example": {
                "event_id": "evt-12345",
                "event_type": "motion_detected",
                "source": "ring",
                "device_id": "ring_doorbell_front",
                "location": "front_door",
                "metadata": {"confidence": 0.95, "person_detected": True}
            }
        }
    }


class UserCommand(BaseModel):
    """
    Represents an explicit command or query from the user.
    Can be voiced via Alexa+, typed via Web/Mobile frontend, etc.
    """
    command_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    command_text: str = Field(..., description="Natural language or structured command text")
    source: str = Field(default="user", description="Source interface, e.g. 'alexa', 'web_ui', 'mobile'")
    user_id: Optional[str] = Field(default=None, description="Optional user identifier")
    timestamp: datetime = Field(default_factory=get_utc_now, description="UTC timestamp of command")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parsed or associated parameters")

    model_config = {
        "json_schema_extra": {
            "example": {
                "command_id": "cmd-9876",
                "command_text": "Set home mode to away",
                "source": "alexa",
                "parameters": {"mode": "away"}
            }
        }
    }
