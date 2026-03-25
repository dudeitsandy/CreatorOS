from typing import Any

import httpx

from app.config import settings
from app.integrations.base import PlatformIntegration
from app.integrations.normalizer import normalize_message

_TELEGRAM_API_BASE = "https://api.telegram.org/bot"


class TelegramIntegration(PlatformIntegration):
    """Telegram Bot API integration."""

    def __init__(self, bot_token: str | None = None) -> None:
        self._token = bot_token or settings.telegram_bot_token
        self._base_url = f"{_TELEGRAM_API_BASE}{self._token}"

    async def connect(self) -> None:
        """Verify the bot token by calling getMe."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self._base_url}/getMe")
            response.raise_for_status()

    async def fetch_messages(self, conversation_id: str) -> list[dict[str, Any]]:
        """Fetch updates from Telegram for a given chat ID."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self._base_url}/getUpdates",
                params={"chat_id": conversation_id},
            )
            response.raise_for_status()
            data = response.json()
            messages = []
            for update in data.get("result", []):
                msg = update.get("message")
                if msg:
                    messages.append(normalize_message(msg, platform="telegram"))
            return messages

    async def send_message(self, conversation_id: str, content: str) -> dict[str, Any]:
        """Send a text message to a Telegram chat."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{self._base_url}/sendMessage",
                json={"chat_id": conversation_id, "text": content},
            )
            response.raise_for_status()
            return response.json()

    async def get_conversation_history(
        self, conversation_id: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Telegram does not expose full history via Bot API; returns empty list."""
        return []
