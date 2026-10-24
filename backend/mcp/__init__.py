from backend.mcp.server import create_mcp_server, mcp_server
from backend.mcp.schemas import (
    GetHomeStatusInput,
    HomeStatusOutput,
    WhatHappenedInput,
    WhatHappenedOutput,
    SetHomeModeInput,
    SetHomeModeOutput,
    SetTemporaryWatchInput,
    SetTemporaryWatchOutput,
    GetRecentEventsInput,
    RecentEventsOutput,
    ClearAlertInput,
    ClearAlertOutput,
)

__all__ = [
    "create_mcp_server",
    "mcp_server",
    "GetHomeStatusInput",
    "HomeStatusOutput",
    "WhatHappenedInput",
    "WhatHappenedOutput",
    "SetHomeModeInput",
    "SetHomeModeOutput",
    "SetTemporaryWatchInput",
    "SetTemporaryWatchOutput",
    "GetRecentEventsInput",
    "RecentEventsOutput",
    "ClearAlertInput",
    "ClearAlertOutput",
]
