from abc import ABC, abstractmethod
from typing import Any


class PlatformIntegration(ABC):
    """Abstract base class for all messaging platform integrations."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish a connection or authenticate with the platform."""
        ...

    @abstractmethod
    async def fetch_messages(self, conversation_id: str) -> list[dict[str, Any]]:
        """Fetch recent messages for a given conversation.

        Args:
            conversation_id: Platform-specific conversation identifier.

        Returns a list of normalized message dicts.
        """
        ...

    @abstractmethod
    async def send_message(self, conversation_id: str, content: str) -> dict[str, Any]:
        """Send a message to a conversation.

        Args:
            conversation_id: Platform-specific conversation identifier.
            content: Text content to send.

        Returns the platform's send-confirmation payload.
        """
        ...

    @abstractmethod
    async def get_conversation_history(
        self, conversation_id: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Retrieve the full message history for a conversation.

        Args:
            conversation_id: Platform-specific conversation identifier.
            limit: Maximum number of messages to return.

        Returns a list of normalized message dicts in chronological order.
        """
        ...
