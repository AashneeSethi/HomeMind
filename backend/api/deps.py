from typing import Optional
from backend.agent.planner import AgentPlanner
from backend.integrations.alexa import AlexaIntegration
from backend.integrations.firetv import FireTVIntegration
from backend.integrations.ring import RingIntegration

_planner_instance: Optional[AgentPlanner] = None


def get_planner() -> AgentPlanner:
    """
    Provide singleton AgentPlanner instance loaded with registered placeholder adapters.
    """
    global _planner_instance
    if _planner_instance is None:
        _planner_instance = AgentPlanner()
        _planner_instance.register_integration("ring", RingIntegration())
        _planner_instance.register_integration("alexa", AlexaIntegration())
        _planner_instance.register_integration("firetv", FireTVIntegration())
    return _planner_instance


def reset_planner() -> None:
    """Reset the singleton instance (useful for testing)."""
    global _planner_instance
    _planner_instance = None
