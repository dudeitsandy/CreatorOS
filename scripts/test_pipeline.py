#!/usr/bin/env python3
"""CLI script to test the ML pipeline against sample messages."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.ml_pipeline import classify_intent, score_value
from app.services.routing import route_message
from tests.fixtures.sample_messages import (
    BOUNDARY_MESSAGES,
    COMPLAINT_MESSAGES,
    HIGH_VALUE_MESSAGES,
    LOW_VALUE_MESSAGES,
    MID_VALUE_MESSAGES,
)

_TIER_THRESHOLDS = {"HIGH": 0.7, "MID": 0.3, "LOW": 0.0}


def _tier_from_score(score: float) -> str:
    if score >= 0.7:
        return "HIGH"
    if score >= 0.3:
        return "MID"
    return "LOW"


async def run_pipeline(label: str, messages: list[dict]) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {label}")
    print("=" * 60)
    for msg in messages:
        score = score_value(msg["content"], fan_spend=msg.get("fan_spend", 0.0))
        intent = await classify_intent(msg["content"])
        action = route_message(score, intent)
        tier = _tier_from_score(score)

        score_ok = "✓" if tier == msg.get("expected_tier") else "✗"
        intent_ok = "✓" if intent == msg.get("expected_intent") else "~"

        print(f"\n  Message : {msg['content'][:70]}")
        print(f"  Score   : {score:.2f}  Tier: {tier} {score_ok} (expected {msg.get('expected_tier')})")
        print(f"  Intent  : {intent} {intent_ok} (expected {msg.get('expected_intent')})")
        print(f"  Action  : {action}")


async def main() -> None:
    print("CreatorOS ML Pipeline Test")
    print("Note: Intent classification uses fallback rules (no Together.ai key set).")

    await run_pipeline("HIGH VALUE MESSAGES", HIGH_VALUE_MESSAGES)
    await run_pipeline("MID VALUE MESSAGES", MID_VALUE_MESSAGES)
    await run_pipeline("LOW VALUE MESSAGES", LOW_VALUE_MESSAGES)
    await run_pipeline("BOUNDARY MESSAGES", BOUNDARY_MESSAGES)
    await run_pipeline("COMPLAINT MESSAGES", COMPLAINT_MESSAGES)

    print("\n" + "=" * 60)
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
