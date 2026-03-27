HIGH_THRESHOLD = 0.7
LOW_THRESHOLD = 0.3

NOTIFY_CREATOR_URGENT = "NOTIFY_CREATOR_URGENT"
QUEUE_WITH_SUGGESTION = "QUEUE_WITH_SUGGESTION"
AUTO_RESPOND = "AUTO_RESPOND"
QUEUE_SILENT = "QUEUE_SILENT"

_ALWAYS_URGENT_INTENTS = {"boundary", "complaint"}


def route_message(
    value_score: float,
    intent: str,
    auto_respond_enabled: bool = False,
    high_threshold: float = HIGH_THRESHOLD,
    low_threshold: float = LOW_THRESHOLD,
) -> str:
    """Determine the routing action for an inbound message.

    Returns one of: NOTIFY_CREATOR_URGENT, QUEUE_WITH_SUGGESTION,
    AUTO_RESPOND, QUEUE_SILENT.
    """
    if intent in _ALWAYS_URGENT_INTENTS:
        return NOTIFY_CREATOR_URGENT

    if value_score >= high_threshold:
        return NOTIFY_CREATOR_URGENT

    if value_score >= low_threshold:
        return QUEUE_WITH_SUGGESTION

    if auto_respond_enabled:
        return AUTO_RESPOND

    return QUEUE_SILENT
