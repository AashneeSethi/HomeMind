from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.agent.planner import AgentPlanner
from backend.api.deps import get_planner
from backend.models.actions import AgentAction
from backend.models.events import HomeEvent
from backend.models.home_state import HomeState, TemporaryWatch
from backend.simulator.agent import SimulatedAlexaAgent
from backend.simulator.events import create_simulated_event

router = APIRouter(tags=["Simulator & Frontend"])


class DetailedHomeState(BaseModel):
    occupancy_mode: str
    active_alerts: List[str]
    devices_count: int
    devices: Dict[str, Any]
    context_summary: str
    last_event_timestamp: Optional[datetime]
    active_watches_count: int
    updated_at: datetime


class WatchView(BaseModel):
    watch_id: str
    location: str
    duration_minutes: int
    event_types: Optional[List[str]]
    created_at: datetime
    expires_at: datetime
    remaining_seconds: int
    is_active: bool


class SimulateEventRequest(BaseModel):
    event_type: str = Field(..., description="e.g. 'doorbell_press', 'motion_detected', 'vehicle_detected'")
    location: str = Field(default="front_door", description="Location, e.g. 'front_door', 'driveway', 'backyard'")
    source: str = Field(default="ring", description="Device source, e.g. 'ring'")
    device_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SimulateEventResponse(BaseModel):
    status: str
    event: HomeEvent
    action: AgentAction
    home_state: HomeState


class ChatRequest(BaseModel):
    message: str = Field(..., description="User voice utterance / chat text")


class ChatResponse(BaseModel):
    input_text: str
    tool_called: str
    tool_parameters: Dict[str, Any]
    tool_result: Dict[str, Any]
    reply: str


class SetModeRequest(BaseModel):
    mode: Literal["home", "away", "sleep", "focus"]


class ClearAlertRequest(BaseModel):
    alert_id: str


@router.get("/state", response_model=DetailedHomeState)
async def get_state(planner: AgentPlanner = Depends(get_planner)) -> DetailedHomeState:
    """Retrieve full live home state for the frontend dashboard."""
    state = planner.context.get_state()
    active_watches = planner.memory.get_active_watches()
    return DetailedHomeState(
        occupancy_mode=state.occupancy_mode,
        active_alerts=list(state.active_alerts),
        devices_count=len(state.devices),
        devices={k: v.model_dump(mode="json") for k, v in state.devices.items()},
        context_summary=state.context_summary,
        last_event_timestamp=state.last_event_timestamp,
        active_watches_count=len(active_watches),
        updated_at=state.updated_at,
    )


@router.get("/watches", response_model=List[WatchView])
async def get_watches(planner: AgentPlanner = Depends(get_planner)) -> List[WatchView]:
    """Retrieve active and recent temporary watches."""
    now = datetime.now(timezone.utc)
    # clean expired
    watches = planner.memory.get_active_watches(current_time=now)
    views = []
    for w in watches:
        remaining = max(0, int((w.expires_at - now).total_seconds()))
        views.append(
            WatchView(
                watch_id=w.watch_id,
                location=w.location,
                duration_minutes=w.duration_minutes,
                event_types=w.event_types,
                created_at=w.created_at,
                expires_at=w.expires_at,
                remaining_seconds=remaining,
                is_active=w.is_active(now),
            )
        )
    return views


@router.delete("/watches/{watch_id}")
async def cancel_watch(
    watch_id: str, planner: AgentPlanner = Depends(get_planner)
) -> Dict[str, Any]:
    """Cancel a temporary watch."""
    watch = planner.memory._watches.pop(watch_id, None)
    if not watch:
        raise HTTPException(status_code=404, detail="Watch not found")
    return {"status": "cancelled", "watch_id": watch_id}


@router.get("/alerts", response_model=List[str])
async def get_alerts(planner: AgentPlanner = Depends(get_planner)) -> List[str]:
    """Retrieve active home alerts."""
    return list(planner.context.get_state().active_alerts)


@router.post("/alerts/clear")
async def clear_alert(
    req: ClearAlertRequest, planner: AgentPlanner = Depends(get_planner)
) -> Dict[str, Any]:
    """Clear an active alert by ID, text, or 'all'."""
    cleared = planner.context.clear_alert(req.alert_id)
    return {
        "status": "cleared" if cleared else "not_found",
        "alert_id": req.alert_id,
        "remaining_alerts": planner.context.get_state().active_alerts,
    }


@router.post("/simulate/event", response_model=SimulateEventResponse)
async def simulate_event(
    req: SimulateEventRequest, planner: AgentPlanner = Depends(get_planner)
) -> SimulateEventResponse:
    """Trigger a simulated Ring/sensor event into HomeMind."""
    event = create_simulated_event(
        event_type=req.event_type,
        location=req.location,
        source=req.source,
        device_id=req.device_id,
        metadata=req.metadata,
    )
    action = await planner.process_event(event)
    state = planner.context.get_state()
    return SimulateEventResponse(
        status="processed",
        event=event,
        action=action,
        home_state=state,
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest, planner: AgentPlanner = Depends(get_planner)
) -> ChatResponse:
    """Conversational interaction representing Alexa+ executing HomeMind MCP tools."""
    agent = SimulatedAlexaAgent(planner=planner)
    resp = await agent.handle_utterance(req.message)
    return ChatResponse(
        input_text=resp.input_text,
        tool_called=resp.tool_called,
        tool_parameters=resp.tool_parameters,
        tool_result=resp.tool_result,
        reply=resp.spoken_response,
    )


@router.post("/mode")
async def set_mode(
    req: SetModeRequest, planner: AgentPlanner = Depends(get_planner)
) -> Dict[str, Any]:
    """Quickly set occupancy mode."""
    new_state = planner.context.set_occupancy_mode(req.mode)
    return {
        "status": "mode_updated",
        "occupancy_mode": new_state.occupancy_mode,
        "context_summary": new_state.context_summary,
    }
