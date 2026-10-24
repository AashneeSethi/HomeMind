from contextlib import asynccontextmanager
from typing import Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import api_router, health_router, events_router, commands_router, simulator_router
from backend.api.deps import get_planner


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event to initialize planner and adapters."""
    planner = get_planner()
    # Initialize placeholder adapters
    for name, integration in planner.integrations.items():
        await integration.initialize()
    yield


app = FastAPI(
    title="HomeMind Agent Service",
    description="Context-Aware Multi-Device AI Home Agent for Amazon Build, Ship, Shape Hackathon",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for React/Vite frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root-level health endpoint matching requirement:
# GET /health -> {"status": "ok", "service": "homemind"}
@app.get("/health", response_model=Dict[str, str], tags=["Health"])
async def health_check() -> Dict[str, str]:
    return {
        "status": "ok",
        "service": "homemind",
    }


# Include top-level routes directly as specified
app.include_router(events_router)
app.include_router(commands_router)
app.include_router(simulator_router)

# Also expose under /api prefix for API versioning and frontend proxying
app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8081))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
