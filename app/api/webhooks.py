import hmac
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.config import settings
from app.integrations.telegram_bot import TelegramIntegration
from app.services.ml_pipeline import classify_intent, score_value, summarize_conversation
from app.services.routing import AUTO_RESPOND, NOTIFY_CREATOR_URGENT, route_message

logger = logging.getLogger(__name__)
router = APIRouter()

# Store for demo - replace with DB later
messages_store = []

def value_to_tier(score: float) -> str:
    if score >= 0.7:
        return "HIGH"
    elif score >= 0.3:
        return "MID"
    return "LOW"


def _verify_telegram_secret(request: Request) -> bool:
    """Return True if the request carries a valid Telegram webhook secret token."""
    if not settings.telegram_webhook_secret:
        return True  # Secret not configured — skip check (dev only)
    incoming = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    # Use hmac.compare_digest to prevent timing attacks
    return hmac.compare_digest(incoming, settings.telegram_webhook_secret)


@router.post("/telegram")
async def telegram_webhook(request: Request):
    """Receive Telegram updates, score them, route them.

    Register this as your bot webhook:
      https://api.telegram.org/bot<TOKEN>/setWebhook?url=<HOST>/webhooks/telegram&secret_token=<TELEGRAM_WEBHOOK_SECRET>
    """
    if not _verify_telegram_secret(request):
        logger.warning("Rejected webhook request with invalid secret token from %s", request.client.host)
        # Return 200 to avoid Telegram retry storms; log and drop silently
        return {"ok": True}

    try:
        data = await request.json()
        logger.info(f"Received Telegram update: {data}")
        
        # Extract message
        message = data.get("message")
        if not message:
            return {"ok": True, "skipped": "no message"}
        
        text = message.get("text", "")
        chat_id = message["chat"]["id"]
        from_user = message.get("from", {})
        username = from_user.get("username", "unknown")
        
        if not text:
            return {"ok": True, "skipped": "no text"}
        
        # Run through ML pipeline
        value_score = score_value(text, fan_spend=0.0)  # TODO: lookup fan spend from DB
        intent = await classify_intent(text)
        tier = value_to_tier(value_score)
        
        # Determine routing
        action = route_message(
            value_score=value_score,
            intent=intent,
            auto_respond_enabled=True  # TODO: get from creator settings
        )
        
        # Store message (replace with DB later)
        msg_record = {
            "platform": "telegram",
            "chat_id": chat_id,
            "username": username,
            "content": text,
            "value_score": value_score,
            "value_tier": tier,
            "intent": intent,
            "action": action,
            "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
        }
        messages_store.append(msg_record)
        
        logger.info(f"Processed: score={value_score:.2f}, tier={tier}, intent={intent}, action={action}")
        
        # Take action based on routing
        telegram = TelegramIntegration()
        
        if action == AUTO_RESPOND:
            try:
                await telegram.send_message(str(chat_id), "Hey! Thanks for reaching out 💕 I'll get back to you soon!")
                logger.info(f"Auto-responded to {username}")
            except Exception as send_err:
                logger.error(f"Failed to send auto-reply to {username}: {send_err}")

        elif action == NOTIFY_CREATOR_URGENT:
            # TODO: Send notification to creator's personal Telegram/SMS
            logger.warning(f"URGENT: High-value message from @{username} needs attention")

        return {
            "ok": True,
            "processed": {
                "value_score": value_score,
                "tier": tier,
                "intent": intent,
                "action": action
            }
        }

    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/twilio")
async def twilio_webhook(request: Request) -> dict[str, str]:
    """Handle incoming Twilio SMS webhook callbacks."""
    return {"status": "ok"}


@router.get("/messages")
async def get_messages():
    """Debug endpoint to see processed messages."""
    return {"messages": messages_store[-50:], "total": len(messages_store)}


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(token: str = ""):
    """Creator inbox dashboard — live view of all scored messages."""
    if settings.dashboard_token and not hmac.compare_digest(token, settings.dashboard_token):
        raise HTTPException(status_code=401, detail="Invalid or missing token. Use ?token=<DASHBOARD_TOKEN>")

    rows = ""
    for msg in reversed(messages_store[-100:]):
        tier = msg["value_tier"]
        tier_color = {"HIGH": "#ff4444", "MID": "#ffaa00", "LOW": "#44cc88"}.get(tier, "#888")
        tier_bg = {"HIGH": "#fff0f0", "MID": "#fffbf0", "LOW": "#f0fff6"}.get(tier, "#f9f9f9")
        action_label = {
            "NOTIFY_CREATOR_URGENT": "🚨 Needs you",
            "QUEUE_WITH_SUGGESTION": "📋 Queued",
            "AUTO_RESPOND": "🤖 Auto-replied",
            "QUEUE_SILENT": "🔇 Silenced",
        }.get(msg["action"], msg["action"])

        rows += f"""
        <tr style="background:{tier_bg}; border-bottom:1px solid #eee;">
            <td style="padding:10px 8px; font-size:12px; color:#888;">{msg.get("timestamp","")}</td>
            <td style="padding:10px 8px; font-weight:600;">@{msg["username"]}</td>
            <td style="padding:10px 8px; max-width:320px;">{msg["content"]}</td>
            <td style="padding:10px 8px; text-align:center;">
                <span style="background:{tier_color}; color:#fff; padding:2px 8px; border-radius:12px; font-size:12px; font-weight:700;">{tier}</span>
            </td>
            <td style="padding:10px 8px; text-align:center; font-size:13px; color:#555;">{msg["score_display"] if "score_display" in msg else f'{msg["value_score"]:.2f}'}</td>
            <td style="padding:10px 8px; font-size:13px; color:#666;">{msg["intent"]}</td>
            <td style="padding:10px 8px; font-size:13px;">{action_label}</td>
        </tr>"""

    high_count = sum(1 for m in messages_store if m["value_tier"] == "HIGH")
    total = len(messages_store)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="5">
    <title>CreatorOS — Inbox</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f7; color: #1d1d1f; }}
        .header {{ background: #1d1d1f; color: #fff; padding: 20px 32px; display: flex; align-items: center; justify-content: space-between; }}
        .header h1 {{ font-size: 20px; font-weight: 700; letter-spacing: -0.5px; }}
        .header .subtitle {{ font-size: 13px; color: #999; margin-top: 2px; }}
        .stats {{ display: flex; gap: 16px; }}
        .stat {{ text-align: right; }}
        .stat .num {{ font-size: 24px; font-weight: 700; }}
        .stat .label {{ font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 0.5px; }}
        .stat.urgent .num {{ color: #ff4444; }}
        .container {{ padding: 24px 32px; }}
        .card {{ background: #fff; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); overflow: hidden; }}
        table {{ width: 100%; border-collapse: collapse; }}
        thead {{ background: #f5f5f7; }}
        th {{ padding: 10px 8px; text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: #888; font-weight: 600; }}
        tr:hover {{ filter: brightness(0.97); }}
        .empty {{ text-align: center; padding: 60px; color: #999; font-size: 15px; }}
        .refresh {{ font-size: 11px; color: #999; margin-top: 12px; text-align: right; }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>CreatorOS</h1>
            <div class="subtitle">Fan Message Inbox</div>
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
    <div class="container">
        <div class="card">
            {"<table><thead><tr><th>Time</th><th>Fan</th><th>Message</th><th style='text-align:center'>Tier</th><th style='text-align:center'>Score</th><th>Intent</th><th>Action</th></tr></thead><tbody>" + rows + "</tbody></table>" if messages_store else '<div class="empty">No messages yet — waiting for fans to message your bot 👀</div>'}
        </div>
        <div class="refresh">Auto-refreshes every 5 seconds</div>
    </div>
</body>
</html>"""
    return HTMLResponse(content=html)