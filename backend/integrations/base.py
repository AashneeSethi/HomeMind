from abc import ABC, abstractmethod
from typing import Any, Dict
from backend.models.actions import AgentAction


class BaseIntegration(ABC):
    """
    Abstract base class for all smart home device and platform integrations.

    HomeMind decouples decision intelligence from hardware and cloud interfaces.
    Subclasses provide device-specific adapters (e.g., Ring, Alexa, Fire TV)
    that can be swapped from local simulation stubs to real cloud connectors
    as the project evolves.
    """

    def __init__(self, name: str, device_type: str):
        self._name = name
        self._device_type = device_type
        self._is_connected = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def device_type(self) -> str:
        return self._device_type

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the adapter connection.
        Returns True if connection is established, False otherwise.
        """
        pass

    @abstractmethod
    async def execute_action(self, action: AgentAction) -> Dict[str, Any]:
        """
        Execute an agent action on this device interface.
        Returns execution result details.
        """
        pass

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        Query current device status and health.
        """
        pass
