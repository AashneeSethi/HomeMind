import re
from typing import Any, Dict, Optional
from pydantic import BaseModel
from backend.agent.planner import AgentPlanner
from backend.api.deps import get_planner
from backend.mcp.tools import (
    clear_alert_impl,
    get_home_status_impl,
    get_recent_events_impl,
    set_home_mode_impl,
    set_temporary_watch_impl,
    what_happened_impl,
)


class SimulatedAgentResponse(BaseModel):
    """Result of processing a natural language utterance in the Alexa+ simulator."""
    input_text: str
    tool_called: str
    tool_parameters: Dict[str, Any]
    tool_result: Dict[str, Any]
    spoken_response: str


class SimulatedAlexaAgent:
    """
    Deterministic simulated Alexa+ conversational agent.
    Bridges natural-language user queries to HomeMind MCP tools.
    """

    def __init__(self, planner: Optional[AgentPlanner] = None):
        self.planner = planner or get_planner()

    async def handle_utterance(self, utterance: str) -> SimulatedAgentResponse:
        """
        Parse natural-language voice utterance and route to appropriate MCP tool.
        """
        text = utterance.strip()
        lower = text.lower()

        # Command Pattern 1: Watch location for N minutes
        # "Watch the front door for 30 minutes." or "Watch front door for 15 minutes"
        watch_match = re.search(
            r"watch\s+(?:the\s+)?([a-z0-9_\s]+?)\s+for\s+(\d+)\s+minute",
            lower
        )
        if watch_match:
            raw_loc = watch_match.group(1).strip().replace(" ", "_")
            duration = int(watch_match.group(2))
            res = set_temporary_watch_impl(
                location=raw_loc,
                duration_minutes=duration,
                planner=self.planner,
            )
            return SimulatedAgentResponse(
                input_text=text,
                tool_called="set_temporary_watch",
                tool_parameters={"location": raw_loc, "duration_minutes": duration},
                tool_result=res.model_dump(mode="json"),
                spoken_response=res.message,
            )

        # Command Pattern 2: What happened at <location>?
        # "What happened at the front door?"
        what_loc_match = re.search(
            r"what\s+happened\s+(?:at\s+(?:the\s+)?|in\s+(?:the\s+)?)([a-z0-9_\s]+)",
            lower
        )
        if what_loc_match:
            loc = what_loc_match.group(1).strip().rstrip("?.!").replace(" ", "_")
            res = what_happened_impl(location=loc, planner=self.planner)
            return SimulatedAgentResponse(
                input_text=text,
                tool_called="what_happened",
                tool_parameters={"location": loc},
                tool_result=res.model_dump(mode="json"),
                spoken_response=res.summary,
            )

        # Command Pattern 3: Generic what happened / recent events
        if "what happened" in lower:
            res = what_happened_impl(planner=self.planner)
            return SimulatedAgentResponse(
                input_text=text,
                tool_called="what_happened",
                tool_parameters={},
                tool_result=res.model_dump(mode="json"),
                spoken_response=res.summary,
            )

        # Command Pattern 4: Set home mode
        # "Set the home to focus mode." or "Set mode to away"
        mode_match = re.search(
            r"(?:set|switch|change)\s+(?:the\s+)?(?:home\s+)?(?:mode\s+to\s+|to\s+)([a-z]+)(?:\s+mode)?",
            lower
        )
        if mode_match:
            target_mode = mode_match.group(1).strip()
            if target_mode in ["home", "away", "sleep", "focus"]:
                res = set_home_mode_impl(mode=target_mode, planner=self.planner)
                return SimulatedAgentResponse(
                    input_text=text,
                    tool_called="set_home_mode",
                    tool_parameters={"mode": target_mode},
                    tool_result=res.model_dump(mode="json"),
                    spoken_response=res.message,
                )

        # Command Pattern 5: Show recent events
        # "Show me recent events." or "recent events"
        if "recent events" in lower or "show events" in lower or "list events" in lower:
            res = get_recent_events_impl(limit=10, planner=self.planner)
            return SimulatedAgentResponse(
                input_text=text,
                tool_called="get_recent_events",
                tool_parameters={"limit": 10},
                tool_result=res.model_dump(mode="json"),
                spoken_response=res.message,
            )

        # Command Pattern 6: Clear alert
        # "Clear alert <id>" or "Dismiss alert <id>"
        clear_match = re.search(r"(?:clear|dismiss|remove)\s+alert\s*([a-z0-9_\-\s]*)", lower)
        if clear_match:
            alert_id = clear_match.group(1).strip() or "all"
            res = clear_alert_impl(alert_id=alert_id, planner=self.planner)
            return SimulatedAgentResponse(
                input_text=text,
                tool_called="clear_alert",
                tool_parameters={"alert_id": alert_id},
                tool_result=res.model_dump(mode="json"),
                spoken_response=res.message,
            )

        # Command Pattern 7: Home status (Default / What is happening at home?)
        # "What is happening at home?" or "status" or "home status"
        res = get_home_status_impl(planner=self.planner)
        return SimulatedAgentResponse(
            input_text=text,
            tool_called="get_home_status",
            tool_parameters={},
            tool_result=res.model_dump(mode="json"),
            spoken_response=res.message,
        )
