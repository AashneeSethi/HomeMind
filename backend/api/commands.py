from typing import Any, Dict
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from backend.api.deps import get_planner
from backend.agent.planner import AgentPlanner
from backend.models.events import UserCommand
from backend.models.actions import AgentAction
from backend.models.home_state import HomeState

router = APIRouter(prefix="/commands", tags=["Commands"])


class CommandProcessResponse(BaseModel):
    status: str
    command_id: str
    action: AgentAction
    home_state: HomeState


@router.post("", response_model=CommandProcessResponse, status_code=status.HTTP_200_OK)
async def receive_command(
    command: UserCommand,
    planner: AgentPlanner = Depends(get_planner),
) -> CommandProcessResponse:
    """
    Ingest a user command (voice or UI), route through the AgentPlanner,
    and return the resulting agent action and updated home state.
    """
    action = await planner.process_command(command)
    current_state = planner.context.get_state()
    return CommandProcessResponse(
        status="processed",
        command_id=command.command_id,
        action=action,
        home_state=current_state,
    )
