from typing import Any


def normalize_message(raw: dict[str, Any], platform: str) -> dict[str, Any]:
    """Normalize a platform-specific message payload to a common format.

    Returns a dict with keys: platform, content, media_urls, sender_id,
    timestamp, direction, raw.
    """
    if platform == "telegram":
        return _normalize_telegram(raw)
    if platform == "sms":
        return _normalize_twilio(raw)
    return {
        "platform": platform,
        "content": raw.get("content", ""),
        "media_urls": [],
        "sender_id": None,
        "timestamp": None,
        "direction": "inbound",
        "raw": raw,
    }


def _normalize_telegram(raw: dict[str, Any]) -> dict[str, Any]:
    """Convert a Telegram message dict to the common format."""
    sender = raw.get("from", {})
    sender_id = str(sender.get("id", "")) if sender else None
    photo = raw.get("photo", [])
    media_urls: list[str] = [p.get("file_id", "") for p in photo if p.get("file_id")]

    return {
        "platform": "telegram",
        "content": raw.get("text", raw.get("caption", "")),
        "media_urls": media_urls,
        "sender_id": sender_id,
        "timestamp": raw.get("date"),
        "direction": "inbound",
        "raw": raw,
    }


def _normalize_twilio(raw: dict[str, Any]) -> dict[str, Any]:
    """Convert a Twilio SMS message dict to the common format."""
    direction_map = {"inbound": "inbound", "outbound-api": "outbound", "outbound-reply": "outbound"}
    direction = direction_map.get(str(raw.get("direction", "inbound")), "inbound")
    num_media = int(raw.get("num_media", 0))
    media_urls = [raw.get(f"media_url_{i}", "") for i in range(num_media)]

    return {
        "platform": "sms",
        "content": raw.get("body", ""),
        "media_urls": [u for u in media_urls if u],
        "sender_id": raw.get("from_"),
        "timestamp": str(raw.get("date_created", "")),
        "direction": direction,
        "raw": raw,
    }
