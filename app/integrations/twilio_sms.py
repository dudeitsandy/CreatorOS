from typing import Any

from twilio.rest import Client

from app.config import settings
from app.integrations.base import PlatformIntegration
from app.integrations.normalizer import normalize_message


class TwilioSMSIntegration(PlatformIntegration):
    """Twilio SMS integration."""

    def __init__(
        self,
        account_sid: str | None = None,
        auth_token: str | None = None,
    ) -> None:
        self._account_sid = account_sid or settings.twilio_account_sid
        self._auth_token = auth_token or settings.twilio_auth_token
        self._client: Client | None = None

    async def connect(self) -> None:
        """Initialize the Twilio REST client."""
        self._client = Client(self._account_sid, self._auth_token)

    async def fetch_messages(self, conversation_id: str) -> list[dict[str, Any]]:
        """Fetch SMS messages for the given phone number (conversation_id)."""
        if self._client is None:
            await self.connect()
        raw_messages = self._client.messages.list(to=conversation_id, limit=50)  # type: ignore[union-attr]
        return [normalize_message(m.__dict__, platform="sms") for m in raw_messages]

    async def send_message(self, conversation_id: str, content: str) -> dict[str, Any]:
        """Send an SMS to the given phone number."""
        if self._client is None:
            await self.connect()
        message = self._client.messages.create(  # type: ignore[union-attr]
            body=content,
            from_=settings.twilio_from_number,
            to=conversation_id,
        )
        return {"sid": message.sid, "status": message.status}

    async def get_conversation_history(
        self, conversation_id: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Retrieve SMS history for a phone number."""
        if self._client is None:
            await self.connect()
        raw_messages = self._client.messages.list(to=conversation_id, limit=limit)  # type: ignore[union-attr]
        return [normalize_message(m.__dict__, platform="sms") for m in raw_messages]
