from typing import Any, Dict, Optional
from backend.agent.context import ContextManager
from backend.agent.decisions import DecisionEngine
from backend.agent.memory import MemoryManager
from backend.integrations.base import BaseIntegration
from backend.models.actions import AgentAction, DecisionType
from backend.models.events import HomeEvent, UserCommand


class AgentPlanner:
    """
    Central orchestrator for the HomeMind agent.
    Coordinates ContextManager, MemoryManager, DecisionEngine, and Device Integrations.

    NOTE: Uses deterministic placeholder planning logic.
    No LLM dependency is used at this stage, per hackathon architecture guidelines.
    """

    def __init__(
        self,
        context_manager: Optional[ContextManager] = None,
        memory_manager: Optional[MemoryManager] = None,
        decision_engine: Optional[DecisionEngine] = None,
    ):
        self.context = context_manager or ContextManager()
        self.memory = memory_manager or MemoryManager()
        self.decision_engine = decision_engine or DecisionEngine()
        self.integrations: Dict[str, BaseIntegration] = {}

    def register_integration(self, name: str, integration: BaseIntegration) -> None:
        """Register a device or cloud platform integration adapter."""
        self.integrations[name] = integration

    async def process_event(self, event: HomeEvent) -> AgentAction:
        """
        Process an incoming home event through the 5-step cognitive pipeline:
        1. Contextualize what happened
        2. Evaluate whether it matters
        3. Decide if the user should be interrupted
        4. Select appropriate action
        5. Route to suitable device interface
        """
        # Step 1 & 2: Gather context & recent history & active watches
        current_state = self.context.get_state()
        recent_events = self.memory.get_recent_events(limit=10)
        preferences = self.memory.get_all_preferences()
        active_watches = self.memory.get_active_watches(current_time=event.timestamp)

        # Step 3, 4, 5: Evaluate via DecisionEngine
        evaluation = self.decision_engine.evaluate(
            event=event,
            context=current_state,
            recent_events=recent_events,
            preferences=preferences,
            active_watches=active_watches,
        )

        action = AgentAction(
            decision=evaluation.decision,
            target_device=evaluation.target_device,
            action_type=evaluation.action_type,
            payload=evaluation.payload,
            reasoning=evaluation.reasoning,
        )

        # Update context and memory if not ignored
        if evaluation.decision != DecisionType.IGNORE:
            self.context.update_from_event(event)

        self.memory.record_event(event)
        self.memory.record_action(action)

        # Dispatch to target device adapter if registered and actionable
        if action.target_device and action.target_device in self.integrations:
            adapter = self.integrations[action.target_device]
            await adapter.execute_action(action)

        return action

    async def process_command(self, command: UserCommand) -> AgentAction:
        """
        Process an explicit user instruction (voice or text command).
        """
        text = command.command_text.lower().strip()
        response_text = ""
        action_type = "respond"
        target_device = command.source if command.source in ["alexa", "firetv"] else "alexa"

        # Deterministic intent handling
        if "mode" in text:
            new_mode = "home"
            for mode in ["away", "sleep", "focus", "home"]:
                if mode in text:
                    new_mode = mode
                    break
            self.context.set_occupancy_mode(new_mode)
            response_text = f"Home occupancy mode has been updated to '{new_mode}'."
            action_type = "mode_change"
        elif "status" in text or "summary" in text:
            state = self.context.get_state()
            response_text = f"Current status: {state.context_summary}"
            action_type = "status_report"
        elif "clear alert" in text or "dismiss" in text:
            self.context.reset()
            response_text = "All active alerts and states have been reset."
            action_type = "clear_alerts"
        else:
            response_text = f"HomeMind received your command: '{command.command_text}'."
            action_type = "acknowledgement"

        action = AgentAction(
            decision=DecisionType.TRIGGER_ACTION,
            target_device=target_device,
            action_type=action_type,
            payload={"message": response_text, "command_id": command.command_id},
            reasoning=f"Handled user command: '{command.command_text}'",
        )

        self.memory.record_action(action)

        if target_device in self.integrations:
            await self.integrations[target_device].execute_action(action)

        return action
