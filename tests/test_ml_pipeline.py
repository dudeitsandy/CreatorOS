import pytest

from app.services.ml_pipeline import score_value, _fallback_classify_intent
from app.services.routing import route_message, NOTIFY_CREATOR_URGENT, QUEUE_WITH_SUGGESTION, AUTO_RESPOND, QUEUE_SILENT
from tests.fixtures.sample_messages import (
    HIGH_VALUE_MESSAGES,
    MID_VALUE_MESSAGES,
    LOW_VALUE_MESSAGES,
    BOUNDARY_MESSAGES,
    COMPLAINT_MESSAGES,
)


class TestScoreValue:
    def test_high_value_buying_signals_and_spend(self) -> None:
        score = score_value("I want to buy a custom video", fan_spend=300.0)
        assert score >= 0.7

    def test_low_value_low_effort_message(self) -> None:
        score = score_value("hey", fan_spend=0.0)
        assert score < 0.5

    def test_mid_value_moderate_message(self) -> None:
        score = score_value("how much are your prices?", fan_spend=50.0)
        assert 0.3 <= score < 0.7

    def test_score_clamped_to_zero_one(self) -> None:
        score = score_value("hey hi wyd sup hello yo", fan_spend=0.0)
        assert 0.0 <= score <= 1.0

    def test_score_clamped_upper(self) -> None:
        score = score_value("buy custom video tip pay purchase order price", fan_spend=600.0)
        assert score <= 1.0

    def test_no_spend_no_signals(self) -> None:
        score = score_value("just browsing", fan_spend=0.0)
        assert 0.4 <= score <= 0.6

    @pytest.mark.parametrize("msg", HIGH_VALUE_MESSAGES)
    def test_high_value_fixtures_score_above_threshold(self, msg: dict) -> None:
        score = score_value(msg["content"], fan_spend=msg["fan_spend"])
        assert score >= 0.3, f"Expected score >= 0.3 for: {msg['content']}"

    @pytest.mark.parametrize("msg", LOW_VALUE_MESSAGES)
    def test_low_value_fixtures_score_below_mid(self, msg: dict) -> None:
        score = score_value(msg["content"], fan_spend=msg["fan_spend"])
        assert score < 0.5, f"Expected score < 0.5 for: {msg['content']}"


class TestFallbackClassifyIntent:
    def test_greeting(self) -> None:
        assert _fallback_classify_intent("hey there") == "greeting"

    def test_pricing(self) -> None:
        assert _fallback_classify_intent("what is the price?") == "pricing"

    def test_custom_request(self) -> None:
        assert _fallback_classify_intent("I want a custom video") == "custom_request"

    def test_complaint(self) -> None:
        assert _fallback_classify_intent("I want a refund, very disappointed") == "complaint"

    def test_boundary(self) -> None:
        assert _fallback_classify_intent("please stop, I said no") == "boundary"

    def test_general_fallback(self) -> None:
        assert _fallback_classify_intent("just checking in") == "general"


class TestRouteMessage:
    def test_high_score_returns_urgent(self) -> None:
        assert route_message(0.8, "general") == NOTIFY_CREATOR_URGENT

    def test_boundary_intent_always_urgent(self) -> None:
        assert route_message(0.1, "boundary") == NOTIFY_CREATOR_URGENT

    def test_complaint_intent_always_urgent(self) -> None:
        assert route_message(0.2, "complaint") == NOTIFY_CREATOR_URGENT

    def test_mid_score_returns_queue_with_suggestion(self) -> None:
        assert route_message(0.5, "general") == QUEUE_WITH_SUGGESTION

    def test_low_score_auto_respond_enabled(self) -> None:
        assert route_message(0.1, "general", auto_respond_enabled=True) == AUTO_RESPOND

    def test_low_score_no_auto_respond(self) -> None:
        assert route_message(0.1, "general", auto_respond_enabled=False) == QUEUE_SILENT

    def test_exact_high_threshold(self) -> None:
        assert route_message(0.7, "general") == NOTIFY_CREATOR_URGENT

    def test_exact_low_threshold(self) -> None:
        assert route_message(0.3, "general") == QUEUE_WITH_SUGGESTION

    def test_just_below_low_threshold_no_auto(self) -> None:
        assert route_message(0.29, "general", auto_respond_enabled=False) == QUEUE_SILENT

    @pytest.mark.parametrize("msg", BOUNDARY_MESSAGES)
    def test_boundary_fixtures_route_urgent(self, msg: dict) -> None:
        intent = _fallback_classify_intent(msg["content"])
        score = score_value(msg["content"], fan_spend=msg["fan_spend"])
        action = route_message(score, intent)
        assert action == NOTIFY_CREATOR_URGENT

    @pytest.mark.parametrize("msg", COMPLAINT_MESSAGES)
    def test_complaint_fixtures_route_urgent(self, msg: dict) -> None:
        intent = _fallback_classify_intent(msg["content"])
        score = score_value(msg["content"], fan_spend=msg["fan_spend"])
        action = route_message(score, intent)
        assert action == NOTIFY_CREATOR_URGENT
