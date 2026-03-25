from typing import Any

import httpx

from app.config import settings

_TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"


async def generate_response(
    conversation_history: list[dict[str, Any]],
    creator_persona: str = "",
) -> str:
    """Generate an AI response for a fan message using Together.ai.

    Args:
        conversation_history: List of message dicts with 'direction' and 'content' keys.
        creator_persona: Optional persona/style instructions for the creator.

    Returns the generated response text, or an empty string if generation fails.
    """
    if not settings.together_api_key:
        return ""

    system_prompt = (
        "You are a content creator responding to a fan message. "
        "Be warm, engaging, and professional."
    )
    if creator_persona:
        system_prompt += f" {creator_persona}"

    messages = [{"role": "system", "content": system_prompt}]
    for msg in conversation_history:
        role = "user" if msg.get("direction") == "inbound" else "assistant"
        messages.append({"role": role, "content": msg.get("content", "")})

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                _TOGETHER_API_URL,
                headers={"Authorization": f"Bearer {settings.together_api_key}"},
                json={
                    "model": _MODEL,
                    "messages": messages,
                    "max_tokens": 200,
                    "temperature": 0.7,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return ""
