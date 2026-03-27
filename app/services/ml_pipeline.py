from typing import Any

import httpx

from app.config import settings

_TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

_BUYING_SIGNALS = {"custom", "video", "price", "buy", "tip", "pay", "paid", "purchase", "order", "want"}
_LOW_EFFORT = {"hey", "hi", "wyd", "sup", "hello", "yo"}

_INTENT_LABELS = ["greeting", "pricing", "custom_request", "complaint", "boundary", "general"]


def score_value(content: str, fan_spend: float = 0.0) -> float:
    """Compute a 0-1 value score for an inbound message using rules-based heuristics.

    Higher scores indicate messages more likely to lead to a purchase.
    Fan spend history and buying-signal keywords boost the score; low-effort
    openers reduce it.
    """
    score = 0.5

    import re
    words = set(re.findall(r"[a-z']+", content.lower()))
    buying_hits = len(words & _BUYING_SIGNALS)
    low_effort_hits = len(words & _LOW_EFFORT)

    score += buying_hits * 0.1
    score -= low_effort_hits * 0.15

    # Short low-effort messages (≤3 words, only greetings) get a bigger penalty
    if len(words) <= 3 and words <= (_LOW_EFFORT | {"wyd", "wbu", "u", "there"}):
        score -= 0.25

    if fan_spend > 500:
        score += 0.2
    elif fan_spend > 100:
        score += 0.1
    elif fan_spend > 0:
        score += 0.05

    return max(0.0, min(1.0, score))


async def classify_intent(content: str) -> str:
    """Classify the intent of an inbound message using Together.ai Llama-3.3-70B.

    Returns one of: greeting, pricing, custom_request, complaint, boundary, general.
    Falls back to 'general' if the API is unavailable or returns an unexpected value.
    """
    if not settings.together_api_key:
        return _fallback_classify_intent(content)

    prompt = (
        f"Classify the intent of this fan message into exactly one of these categories: "
        f"{', '.join(_INTENT_LABELS)}.\n\n"
        f"Message: {content}\n\n"
        f"Respond with only the category name, nothing else."
    )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                _TOGETHER_API_URL,
                headers={"Authorization": f"Bearer {settings.together_api_key}"},
                json={
                    "model": _MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 10,
                    "temperature": 0,
                },
            )
            response.raise_for_status()
            data = response.json()
            label = data["choices"][0]["message"]["content"].strip().lower()
            return label if label in _INTENT_LABELS else "general"
    except Exception:
        return _fallback_classify_intent(content)


def _fallback_classify_intent(content: str) -> str:
    """Simple keyword-based intent fallback when Together.ai is unavailable."""
    import re

    lower = content.lower()
    words = set(re.findall(r"[a-z']+", lower))
    if words & {"hi", "hey", "hello", "sup"}:
        return "greeting"
    if words & {"price", "cost", "rate"} or "how much" in lower:
        return "pricing"
    if words & {"custom", "video", "pic", "photo", "request"}:
        return "custom_request"
    if words & {"complaint", "refund", "unhappy", "disappointed", "issue"}:
        return "complaint"
    if words & {"no", "stop", "boundary", "uncomfortable"} or "don't" in lower or "won't" in lower:
        return "boundary"
    return "general"


async def summarize_conversation(messages: list[dict[str, Any]]) -> str:
    """Summarize a conversation into under 50 words using Together.ai.

    Falls back to a simple truncation if the API is unavailable.
    """
    if not messages:
        return ""

    if not settings.together_api_key:
        combined = " ".join(m.get("content", "") for m in messages)
        words = combined.split()
        return " ".join(words[:50]) + ("..." if len(words) > 50 else "")

    conversation_text = "\n".join(
        f"{m.get('direction', 'unknown')}: {m.get('content', '')}" for m in messages
    )
    prompt = (
        f"Summarize this fan-creator conversation in under 50 words:\n\n{conversation_text}"
    )

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                _TOGETHER_API_URL,
                headers={"Authorization": f"Bearer {settings.together_api_key}"},
                json={
                    "model": _MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 80,
                    "temperature": 0.3,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        combined = " ".join(m.get("content", "") for m in messages)
        words = combined.split()
        return " ".join(words[:50]) + ("..." if len(words) > 50 else "")
