import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Platform(str, enum.Enum):
    telegram = "telegram"
    sms = "sms"
    onlyfans = "onlyfans"
    fansly = "fansly"
    sextpanther = "sextpanther"


class Direction(str, enum.Enum):
    inbound = "inbound"
    outbound = "outbound"


class ValueTier(str, enum.Enum):
    HIGH = "HIGH"
    MID = "MID"
    LOW = "LOW"


class Intent(str, enum.Enum):
    greeting = "greeting"
    pricing = "pricing"
    custom_request = "custom_request"
    complaint = "complaint"
    boundary = "boundary"
    general = "general"


class ResponseSource(str, enum.Enum):
    creator = "creator"
    ai_auto = "ai_auto"
    ai_suggested = "ai_suggested"


class Message(Base):
    """Represents a single message within a conversation."""

    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform: Mapped[Platform] = mapped_column(Enum(Platform), nullable=False)
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True
    )
    fan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fans.id"), nullable=True
    )
    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("creators.id"), nullable=False
    )
    direction: Mapped[Direction] = mapped_column(Enum(Direction), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    media_urls: Mapped[list] = mapped_column(JSON, default=list)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    value_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    value_tier: Mapped[ValueTier | None] = mapped_column(Enum(ValueTier), nullable=True)
    intent: Mapped[Intent | None] = mapped_column(Enum(Intent), nullable=True)
    response_source: Mapped[ResponseSource | None] = mapped_column(Enum(ResponseSource), nullable=True)
