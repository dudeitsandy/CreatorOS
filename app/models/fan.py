import uuid

from sqlalchemy import JSON, Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Fan(Base):
    """Represents a fan profile associated with one or more creators."""

    __tablename__ = "fans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    platform_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    total_spend: Mapped[float] = mapped_column(Float, default=0.0)
    metadata_: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
