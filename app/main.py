import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api import creators, messages, webhooks
from app.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(
    title="CreatorOS",
    description="Intelligent messaging triage system for content creators",
    # Hide docs in production — no need to advertise the API surface
    docs_url=None if settings.environment == "production" else "/docs",
    redoc_url=None if settings.environment == "production" else "/redoc",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
# Webhook endpoints are server-to-server (Telegram/Twilio call us directly),
# so they don't need browser CORS at all. We only open up origins that actually
# need it (e.g. a future frontend). Default to localhost in dev.
_origins = (
    [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
    if settings.allowed_origins
    else ["http://localhost:3000", "http://localhost:8000"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


# ── Security headers ──────────────────────────────────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        if settings.environment == "production":
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        return response


app.add_middleware(SecurityHeadersMiddleware)


# ── Request size limit ────────────────────────────────────────────────────────
# Telegram/Twilio payloads are small. Reject anything over 1 MB to prevent
# memory exhaustion from oversized requests.
MAX_BODY_BYTES = 1 * 1024 * 1024  # 1 MB


@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_BODY_BYTES:
        return JSONResponse(status_code=413, content={"detail": "Request body too large"})
    return await call_next(request)


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(creators.router, prefix="/api/creators", tags=["creators"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])


@app.get("/health")
async def health_check() -> dict:
    """Return service health status."""
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def landing():
    return HTMLResponse(content="""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CreatorOS</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0a0a0a;
            color: #fff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }
        .badge {
            background: #1a1a1a;
            border: 1px solid #2a2a2a;
            border-radius: 20px;
            padding: 6px 14px;
            font-size: 12px;
            color: #888;
            margin-bottom: 32px;
            letter-spacing: 0.5px;
        }
        .badge span { color: #44cc88; margin-right: 6px; }
        h1 {
            font-size: clamp(48px, 8vw, 80px);
            font-weight: 800;
            letter-spacing: -3px;
            line-height: 1;
            margin-bottom: 20px;
            background: linear-gradient(135deg, #fff 0%, #888 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        p {
            font-size: 18px;
            color: #666;
            max-width: 480px;
            text-align: center;
            line-height: 1.6;
            margin-bottom: 48px;
        }
        .pills {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            justify-content: center;
            margin-bottom: 48px;
        }
        .pill {
            background: #111;
            border: 1px solid #222;
            border-radius: 8px;
            padding: 10px 18px;
            font-size: 13px;
            color: #aaa;
        }
        .pill strong { color: #fff; display: block; font-size: 15px; margin-bottom: 2px; }
        .footer {
            position: fixed;
            bottom: 24px;
            font-size: 12px;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="badge"><span>●</span> System operational</div>
    <h1>CreatorOS</h1>
    <p>Intelligent messaging triage for content creators. Every fan scored, routed, and handled — so you focus on what matters.</p>
    <div class="pills">
        <div class="pill"><strong>AI Scoring</strong>Value per message</div>
        <div class="pill"><strong>Smart Routing</strong>High value → you first</div>
        <div class="pill"><strong>Auto-Reply</strong>Low value handled</div>
        <div class="pill"><strong>Live Dashboard</strong>Full inbox visibility</div>
    </div>
    <div style="display:flex;gap:12px;margin-bottom:48px;flex-wrap:wrap;justify-content:center;">
        <button onclick="runDemo()" id="demoBtn" style="
            background: #fff; color: #000; border: none;
            padding: 14px 32px; border-radius: 10px;
            font-size: 15px; font-weight: 600; cursor: pointer; letter-spacing: -0.3px;
        ">Run Demo</button>
        <a href="/webhooks/dashboard?token=7b59ff4cda0d628a9d6184ace0ba5082ee61dbd1e38faee936d27e3b25494fd4" style="
            background: transparent; color: #fff;
            border: 1px solid #333; text-decoration: none;
            padding: 14px 32px; border-radius: 10px;
            font-size: 15px; font-weight: 600; letter-spacing: -0.3px;
        ">View Inbox →</a>
    </div>
    <script>
        async function runDemo() {
            const btn = document.getElementById("demoBtn");
            btn.textContent = "Running...";
            btn.disabled = true;
            const token = "7b59ff4cda0d628a9d6184ace0ba5082ee61dbd1e38faee936d27e3b25494fd4";
            await fetch("/webhooks/demo?token=" + token, {method: "POST"});
            window.location.href = "/webhooks/dashboard?token=" + token;
        }
    </script>
    <div class="footer">CreatorOS — Private Beta</div>
</body>
</html>""")
