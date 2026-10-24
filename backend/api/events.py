from typing import Any, Dict, List
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from backend.api.deps import get_planner
from backend.agent.planner import AgentPlanner
from backend.models.events import HomeEvent
from backend.models.actions import AgentAction
from backend.models.home_state import HomeState

router = APIRouter(prefix="/events", tags=["Events"])


class EventProcessResponse(BaseModel):
    status: str
    event_id: str
    action: AgentAction
    home_state: HomeState


@router.post("", response_model=EventProcessResponse, status_code=status.HTTP_200_OK)
async def receive_event(
    event: HomeEvent,
    planner: AgentPlanner = Depends(get_planner),
) -> EventProcessResponse:
    """
    Ingest a home event from a sensor, doorbell, camera, or simulator.
    Evaluates through the HomeMind cognitive decision pipeline.
    """
    action = await planner.process_event(event)
    current_state = planner.context.get_state()
    return EventProcessResponse(
        status="processed",
        event_id=event.event_id,
        action=action,
        home_state=current_state,
    )


@router.get("", response_model=List[HomeEvent])
@router.get("/recent", response_model=List[HomeEvent])
async def get_recent_events(
    limit: int = 20,
    planner: AgentPlanner = Depends(get_planner),
) -> List[HomeEvent]:
    """Retrieve recent home events from working memory."""
    return planner.memory.get_recent_events(limit=limit)


@router.get("/context", response_model=HomeState)
async def get_current_context(
    planner: AgentPlanner = Depends(get_planner),
) -> HomeState:
    """Retrieve the current HomeState maintained by ContextManager."""
    return planner.context.get_state()
