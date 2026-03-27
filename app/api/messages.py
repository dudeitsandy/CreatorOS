from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class IncomingMessagePayload(BaseModel):
    platform: str
    fan_id: UUID | None = None
    creator_id: UUID
    content: str
    media_urls: list[str] = []


class MessageResponse(BaseModel):
    id: UUID
    platform: str
    creator_id: UUID
    fan_id: UUID | None
    content: str
    value_score: float | None
    value_tier: str | None
    intent: str | None
    direction: str
    response_source: str | None


@router.post("/incoming")
async def receive_incoming_message(payload: IncomingMessagePayload) -> dict[str, Any]:
    """Accept an inbound message, run ML pipeline, and route accordingly."""
    from app.services.ml_pipeline import classify_intent, score_value
    from app.services.routing import route_message

    value_score = score_value(content=payload.content, fan_spend=0.0)
    intent = await classify_intent(content=payload.content)
    action = route_message(value_score=value_score, intent=intent)

    return {
        "status": "received",
        "value_score": value_score,
        "intent": intent,
        "action": action,
    }


@router.get("")
async def list_messages() -> list[dict[str, Any]]:
    """Return a paginated list of messages."""
    return []
