from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

_creators: dict[str, dict[str, Any]] = {}


class CreatorCreate(BaseModel):
    name: str
    platform_handles: dict[str, str] = {}
    settings: dict[str, Any] = {}


class CreatorUpdate(BaseModel):
    name: str | None = None
    platform_handles: dict[str, str] | None = None
    settings: dict[str, Any] | None = None


@router.get("")
async def list_creators() -> list[dict[str, Any]]:
    """Return all creators."""
    return list(_creators.values())


@router.post("")
async def create_creator(payload: CreatorCreate) -> dict[str, Any]:
    """Create a new creator."""
    creator_id = str(uuid4())
    creator = {"id": creator_id, **payload.model_dump()}
    _creators[creator_id] = creator
    return creator


@router.get("/{creator_id}")
async def get_creator(creator_id: UUID) -> dict[str, Any]:
    """Retrieve a single creator by ID."""
    creator = _creators.get(str(creator_id))
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")
    return creator


@router.put("/{creator_id}")
async def update_creator(creator_id: UUID, payload: CreatorUpdate) -> dict[str, Any]:
    """Update an existing creator."""
    creator = _creators.get(str(creator_id))
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    creator.update(update_data)
    return creator


@router.delete("/{creator_id}")
async def delete_creator(creator_id: UUID) -> dict[str, str]:
    """Delete a creator by ID."""
    if str(creator_id) not in _creators:
        raise HTTPException(status_code=404, detail="Creator not found")
    del _creators[str(creator_id)]
    return {"status": "deleted"}
