from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class TelegramUpdate(BaseModel):
    update_id: int
    message: dict[str, Any] | None = None


@router.post("/telegram")
async def telegram_webhook(update: TelegramUpdate) -> dict[str, str]:
    """Handle incoming Telegram webhook updates."""
    return {"status": "ok"}


@router.post("/twilio")
async def twilio_webhook(request: Request) -> dict[str, str]:
    """Handle incoming Twilio SMS webhook callbacks."""
    return {"status": "ok"}
