from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import creators, messages, webhooks

app = FastAPI(title="CreatorOS", description="Intelligent messaging triage system for content creators")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(creators.router, prefix="/api/creators", tags=["creators"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])


@app.get("/health")
async def health_check() -> dict:
    """Return service health status."""
    return {"status": "ok"}
