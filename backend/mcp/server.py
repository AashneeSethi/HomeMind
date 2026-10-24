from typing import List, Literal, Optional
from mcp.server.mcpserver import MCPServer
from backend.agent.planner import AgentPlanner
from backend.api.deps import get_planner
from backend.mcp.schemas import (
    ClearAlertOutput,
    HomeStatusOutput,
    RecentEventsOutput,
    SetHomeModeOutput,
    SetTemporaryWatchOutput,
    WhatHappenedOutput,
)
from backend.mcp.tools import (
    clear_alert_impl,
    get_home_status_impl,
    get_recent_events_impl,
    set_home_mode_impl,
    set_temporary_watch_impl,
    what_happened_impl,
)


def create_mcp_server(planner: Optional[AgentPlanner] = None) -> MCPServer:
    """
    Factory creating a standards-compliant HomeMind MCP server.
    Registers the 6 core tools for home context, event querying, and watch management.
    """
    server = MCPServer(name="HomeMind")
    active_planner = planner or get_planner()

    @server.tool(
        description="Return the current HomeMind home state, current mode, active alerts, known devices and a concise context summary."
    )
    def get_home_status() -> HomeStatusOutput:
        return get_home_status_impl(planner=active_planner)

    @server.tool(
        description="Return a concise natural-language summary plus structured recent events, optionally filtered by location and time window in minutes."
    )
    def what_happened(
        location: Optional[str] = None,
        since_minutes: Optional[int] = None,
    ) -> WhatHappenedOutput:
        return what_happened_impl(
            location=location,
            since_minutes=since_minutes,
            planner=active_planner,
        )

    @server.tool(
        description="Update the HomeMind occupancy mode to one of: 'home', 'away', 'sleep', 'focus'."
    )
    def set_home_mode(
        mode: Literal["home", "away", "sleep", "focus"]
    ) -> SetHomeModeOutput:
        return set_home_mode_impl(mode=mode, planner=active_planner)

    @server.tool(
        description="Create a temporary monitoring or watch intention in HomeMind MemoryManager for a specific location."
    )
    def set_temporary_watch(
        location: str,
        duration_minutes: int,
        event_types: Optional[List[str]] = None,
    ) -> SetTemporaryWatchOutput:
        return set_temporary_watch_impl(
            location=location,
            duration_minutes=duration_minutes,
            event_types=event_types,
            planner=active_planner,
        )

    @server.tool(
        description="Retrieve recent events from HomeMind operational working memory."
    )
    def get_recent_events(
        limit: Optional[int] = 10
    ) -> RecentEventsOutput:
        return get_recent_events_impl(limit=limit, planner=active_planner)

    @server.tool(
        description="Clear an active HomeMind alert by ID, keyword match, or 'all'."
    )
    def clear_alert(alert_id: str) -> ClearAlertOutput:
        return clear_alert_impl(alert_id=alert_id, planner=active_planner)

    return server


# Default singleton instance
mcp_server = create_mcp_server()


if __name__ == "__main__":
    import asyncio
    # Standalone execution for local STDIO testing
    print("Starting HomeMind MCP server via stdio transport...")
    asyncio.run(mcp_server.run_stdio_async())
