from fastapi import APIRouter
from backend.api.health import router as health_router
from backend.api.events import router as events_router
from backend.api.commands import router as commands_router
from backend.api.simulator import router as simulator_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(events_router)
api_router.include_router(commands_router)
api_router.include_router(simulator_router)

__all__ = [
    "api_router",
    "health_router",
    "events_router",
    "commands_router",
    "simulator_router",
]
