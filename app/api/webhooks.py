import hmac
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.config import settings
from app.integrations.telegram_bot import TelegramIntegration
from app.services.ml_pipeline import classify_intent, score_value
from app.services.routing import AUTO_RESPOND, NOTIFY_CREATOR_URGENT, route_message

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory store — replace with DB when ready
messages_store: list[dict[str, Any]] = []

# ── Demo messages — run through the REAL pipeline, not hardcoded results ──────
_DEMO_MESSAGES = [
    {"username": "whale_dan",      "display": "Dan",        "text": "Hey I want to order a custom 10 min video just for me, how much?", "fan_spend": 500.0},
    {"username": "big_spender",    "display": "Jessica",    "text": "I'd love to tip you and get a custom clip, what are your rates?",   "fan_spend": 150.0},
    {"username": "regular_sub",    "display": "Mike",       "text": "How much are your subscription tiers? Do you do customs?",          "fan_spend": 25.0},
    {"username": "new_fan",        "display": "Alex",       "text": "Your last post was so hot, when's the next one coming?",            "fan_spend": 0.0},
    {"username": "just_browsing",  "display": "Sam",        "text": "hey",                                                               "fan_spend": 0.0},
    {"username": "upset_customer", "display": "Tyler",      "text": "I paid for a custom 2 weeks ago and never got it, I want a refund", "fan_spend": 75.0},
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _value_to_tier(score: float) -> str:
    if score >= 0.7:
        return "HIGH"
    elif score >= 0.3:
        return "MID"
    return "LOW"


def _verify_telegram_secret(request: Request) -> bool:
    if not settings.telegram_webhook_secret:
        return True
    incoming = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    return hmac.compare_digest(incoming, settings.telegram_webhook_secret)


def _verify_dashboard_token(token: str) -> bool:
    if not settings.dashboard_token:
        return True
    return hmac.compare_digest(token, settings.dashboard_token)


async def _run_pipeline(
    text: str,
    username: str,
    chat_id: Any,
    platform: str = "telegram",
    fan_spend: float = 0.0,
    is_demo: bool = False,
) -> dict[str, Any]:
    """Core pipeline: score → classify → route → store. Used by webhook and demo."""
    value_score = score_value(text, fan_spend=fan_spend)
    intent = await classify_intent(text)
    tier = _value_to_tier(value_score)
    action = route_message(value_score=value_score, intent=intent, auto_respond_enabled=True)

    record: dict[str, Any] = {
        "platform": platform,
        "chat_id": chat_id,
        "username": username,
        "content": text,
        "value_score": round(value_score, 2),
        "value_tier": tier,
        "intent": intent,
        "action": action,
        "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
        "is_demo": is_demo,
    }
    messages_store.append(record)
    logger.info("Pipeline [%s] @%s score=%.2f tier=%s intent=%s action=%s",
                "DEMO" if is_demo else platform, username, value_score, tier, intent, action)
    return record


# ── Telegram webhook ──────────────────────────────────────────────────────────

@router.post("/telegram")
async def telegram_webhook(request: Request) -> dict[str, Any]:
    """Receive Telegram updates, score them, route them.

    Register with:
      https://api.telegram.org/bot<TOKEN>/setWebhook?url=<HOST>/webhooks/telegram&secret_token=<TELEGRAM_WEBHOOK_SECRET>
    """
    if not _verify_telegram_secret(request):
        logger.warning("Rejected webhook request with invalid secret from %s", request.client.host)
        return {"ok": True}

    try:
        data = await request.json()
        message = data.get("message")
        if not message:
            return {"ok": True, "skipped": "no message"}

        text: str = message.get("text", "")
        if not text:
            return {"ok": True, "skipped": "no text"}

        chat_id = message["chat"]["id"]
        from_user = message.get("from", {})

        # Username > first+last name > "Fan"
        username = (
            from_user.get("username")
            or " ".join(filter(None, [from_user.get("first_name"), from_user.get("last_name")]))
            or "Fan"
        )

        record = await _run_pipeline(text=text, username=username, chat_id=chat_id)

        if record["action"] == AUTO_RESPOND:
            try:
                telegram = TelegramIntegration()
                await telegram.send_message(str(chat_id), "Hey! Thanks for reaching out 💕 I'll get back to you soon!")
                logger.info("Auto-responded to @%s", username)
            except Exception as e:
                logger.error("Failed to send auto-reply to @%s: %s", username, e)

        elif record["action"] == NOTIFY_CREATOR_URGENT:
            # TODO: notify creator via their preferred channel
            logger.warning("URGENT: high-value message from @%s needs attention", username)

        return {"ok": True, "processed": record}

    except Exception as e:
        logger.error("Webhook error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ── Twilio webhook ────────────────────────────────────────────────────────────

@router.post("/twilio")
async def twilio_webhook(request: Request) -> dict[str, str]:
    return {"status": "ok"}


# ── Demo endpoints ────────────────────────────────────────────────────────────

@router.post("/demo")
async def run_demo(token: str = "") -> dict[str, Any]:
    """Fire realistic demo messages through the real ML pipeline.

    Every score, intent, and routing decision is genuine — same code path
    as a live Telegram message. Protected by dashboard token.
    """
    if not _verify_dashboard_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")

    results = []
    for msg in _DEMO_MESSAGES:
        record = await _run_pipeline(
            text=msg["text"],
            username=msg["username"],
            chat_id=f"demo_{msg['username']}",
            platform="demo",
            fan_spend=msg["fan_spend"],
            is_demo=True,
        )
        results.append(record)

    return {"ok": True, "messages_added": len(results), "results": results}


@router.post("/demo/clear")
async def clear_demo(token: str = "") -> dict[str, Any]:
    """Clear all messages from the store (demo reset)."""
    if not _verify_dashboard_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    count = len(messages_store)
    messages_store.clear()
    return {"ok": True, "cleared": count}


# ── Debug endpoint ────────────────────────────────────────────────────────────

@router.get("/messages")
async def get_messages() -> dict[str, Any]:
    return {"messages": messages_store[-50:], "total": len(messages_store)}


# ── Dashboard ─────────────────────────────────────────────────────────────────

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(token: str = "") -> HTMLResponse:
    """Creator inbox — live scored message view."""
    if not _verify_dashboard_token(token):
        raise HTTPException(status_code=401, detail="Invalid or missing token. Use ?token=<DASHBOARD_TOKEN>")

    token_qs = f"?token={token}" if token else ""

    rows = ""
    for msg in reversed(messages_store[-100:]):
        tier = msg["value_tier"]
        tier_color = {"HIGH": "#ff4444", "MID": "#ffaa00", "LOW": "#44cc88"}.get(tier, "#888")
        tier_bg   = {"HIGH": "#fff0f0", "MID": "#fffbf0", "LOW": "#f0fff6"}.get(tier, "#f9f9f9")
        action_label = {
            "NOTIFY_CREATOR_URGENT": "🚨 Needs you",
            "QUEUE_WITH_SUGGESTION": "📋 Queued",
            "AUTO_RESPOND":          "🤖 Auto-replied",
            "QUEUE_SILENT":          "🔇 Silenced",
        }.get(msg["action"], msg["action"])
        demo_badge = ' <span style="font-size:10px;color:#aaa;">[demo]</span>' if msg.get("is_demo") else ""

        rows += f"""
        <tr style="background:{tier_bg}; border-bottom:1px solid #eee;">
            <td style="padding:10px 8px; font-size:12px; color:#888;">{msg.get("timestamp","")}</td>
            <td style="padding:10px 8px; font-weight:600;">@{msg["username"]}{demo_badge}</td>
            <td style="padding:10px 8px; max-width:320px;">{msg["content"]}</td>
            <td style="padding:10px 8px; text-align:center;">
                <span style="background:{tier_color};color:#fff;padding:2px 8px;border-radius:12px;font-size:12px;font-weight:700;">{tier}</span>
            </td>
            <td style="padding:10px 8px; text-align:center; font-size:13px; color:#555;">{msg["value_score"]:.2f}</td>
            <td style="padding:10px 8px; font-size:13px; color:#666;">{msg["intent"]}</td>
            <td style="padding:10px 8px; font-size:13px;">{action_label}</td>
        </tr>"""

    high_count = sum(1 for m in messages_store if m["value_tier"] == "HIGH")
    total = len(messages_store)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CreatorOS — Inbox</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f7; color: #1d1d1f; }}
        .header {{ background: #1d1d1f; color: #fff; padding: 20px 32px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px; }}
        .header h1 {{ font-size: 20px; font-weight: 700; letter-spacing: -0.5px; }}
        .header .subtitle {{ font-size: 13px; color: #999; margin-top: 2px; }}
        .header-right {{ display: flex; align-items: center; gap: 24px; }}
        .stats {{ display: flex; gap: 16px; }}
        .stat {{ text-align: right; }}
        .stat .num {{ font-size: 24px; font-weight: 700; }}
        .stat .label {{ font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 0.5px; }}
        .stat.urgent .num {{ color: #ff4444; }}
        .btn {{ border: none; border-radius: 8px; padding: 8px 16px; font-size: 13px; font-weight: 600; cursor: pointer; }}
        .btn-demo {{ background: #fff; color: #000; }}
        .btn-clear {{ background: #333; color: #fff; }}
        .btn:disabled {{ opacity: 0.5; cursor: default; }}
        .container {{ padding: 24px 32px; }}
        .card {{ background: #fff; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); overflow: hidden; }}
        table {{ width: 100%; border-collapse: collapse; }}
        thead {{ background: #f5f5f7; }}
        th {{ padding: 10px 8px; text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: #888; font-weight: 600; }}
        tr:hover {{ filter: brightness(0.97); }}
        .empty {{ text-align: center; padding: 60px; color: #999; font-size: 15px; }}
        .footer {{ font-size: 11px; color: #999; margin-top: 12px; text-align: right; }}
        #status {{ font-size: 12px; color: #44cc88; margin-left: 8px; }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>CreatorOS</h1>
            <div class="subtitle">Fan Message Inbox</div>
        </div>
        <div class="header-right">
            <div style="display:flex;gap:8px;align-items:center;">
                <button class="btn btn-demo" id="demoBtn" onclick="runDemo()">Run Demo</button>
                <button class="btn btn-clear" id="clearBtn" onclick="clearDemo()">Reset</button>
                <span id="status"></span>
            </div>
            <div class="stats">
                <div class="stat urgent">
                    <div class="num">{high_count}</div>
                    <div class="label">Needs Attention</div>
                </div>
                <div class="stat">
                    <div class="num">{total}</div>
                    <div class="label">Total Messages</div>
                </div>
            </div>
        </div>
    </div>
    <div class="container">
        <div class="card">
            {"<table><thead><tr><th>Time</th><th>Fan</th><th>Message</th><th style='text-align:center'>Tier</th><th style='text-align:center'>Score</th><th>Intent</th><th>Action</th></tr></thead><tbody>" + rows + "</tbody></table>" if messages_store else '<div class="empty">No messages yet — hit <strong>Run Demo</strong> or send your bot a message 👀</div>'}
        </div>
        <div class="footer">Auto-refreshes every 5 seconds</div>
    </div>
    <script>
        const TOKEN = new URLSearchParams(window.location.search).get("token") || "";

        async function runDemo() {{
            const btn = document.getElementById("demoBtn");
            const status = document.getElementById("status");
            btn.disabled = true;
            status.textContent = "Running pipeline...";
            try {{
                const res = await fetch("/webhooks/demo?token=" + TOKEN, {{method: "POST"}});
                const data = await res.json();
                status.textContent = `✓ ${{data.messages_added}} messages processed`;
                setTimeout(() => location.reload(), 800);
            }} catch(e) {{
                status.textContent = "Error — check token";
                btn.disabled = false;
            }}
        }}

        async function clearDemo() {{
            const status = document.getElementById("status");
            status.textContent = "Clearing...";
            await fetch("/webhooks/demo/clear?token=" + TOKEN, {{method: "POST"}});
            setTimeout(() => location.reload(), 400);
        }}

        // Auto-refresh every 5s
        setTimeout(() => location.reload(), 5000);
    </script>
</body>
</html>"""
    return HTMLResponse(content=html)
