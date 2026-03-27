# CreatorOS - Project Context

# CreatorOS: Attack Plan + Claude Code Scaffolding

## Part 1: Attack Plan (When You're Back)

### Week 1: Foundation (Days 1-5)

**Day 1-2: Environment + Skeleton**
- [ ] Set up repo structure (use scaffolding below)
- [ ] Get Claude Code oriented with CLAUDE.md
- [ ] Set up local dev environment (Python, PostgreSQL, Redis)
- [ ] Deploy skeleton to Railway (get URL live immediately)

**Day 3-4: Core ML Pipeline**
- [ ] Implement message normalizer
- [ ] Build value scoring v1 (rules-based, not ML yet)
- [ ] Build intent classifier (pricing, custom request, greeting, boundary)
- [ ] Build conversation summarizer (LLM call)
- [ ] Test with sample messages

**Day 5: First Integration**
- [ ] Choose: Telegram Bot OR Twilio SMS
- [ ] Get messages flowing IN to your pipeline
- [ ] Log everything to database
- [ ] Basic web dashboard to view incoming messages + scores

**Deliverable:** Messages come in → get scored → visible in dashboard

---

### Week 2: Complete the Loop (Days 6-10)

**Day 6-7: Response Generation**
- [ ] Creator persona/voice training setup
- [ ] Response generator for LOW value messages
- [ ] Suggested response generator for MID value
- [ ] "Hold" message generator (e.g., "Hey! I'll get back to you soon")

**Day 8-9: Routing + Sending**
- [ ] Routing rules engine (creator thresholds)
- [ ] Send responses BACK to platform (Telegram or Twilio)
- [ ] Creator notification system (separate Telegram bot or SMS)
- [ ] "I'll handle it" flow (creator takes over conversation)

**Day 10: Demo Polish**
- [ ] Clean up UI
- [ ] Make demo link public
- [ ] Test end-to-end flow
- [ ] Record demo video (optional but powerful)

**Deliverable:** Full loop working - message in → scored → routed → response sent

---

### Week 3: Second Platform + CRM (Days 11-15)

**Day 11-13: Headless Browser (OnlyFans or SextPanther)**
- [ ] Set up Playwright/Puppeteer
- [ ] Login flow + session persistence
- [ ] Message scraping from inbox
- [ ] Message sending via DOM injection
- [ ] Error handling + re-auth alerts

**Day 14-15: Fan Profiles**
- [ ] Per-platform profile creation
- [ ] Conversation history per fan
- [ ] Spend tracking (manual input initially)
- [ ] Tags + notes

**Deliverable:** Two platforms working, basic CRM visible

---

### Week 4: Pilot Ready (Days 16-20)

**Day 16-17: Creator Onboarding**
- [ ] Creator account setup flow
- [ ] Platform credential storage (encrypted)
- [ ] Persona/voice training wizard
- [ ] Threshold configuration UI

**Day 18-19: Hardening**
- [ ] Error handling throughout
- [ ] Logging + monitoring
- [ ] Rate limiting
- [ ] Session recovery

**Day 20: Pilot Launch**
- [ ] Deploy production version
- [ ] Onboard Thrace (or first pilot creator)
- [ ] Set up feedback channel
- [ ] Monitor closely

**Deliverable:** Real creator using it daily

---

## Part 2: Claude Code Scaffolding

### CLAUDE.md (Put this in repo root)

```markdown
# CreatorOS - Claude Code Context

## Project Overview
CreatorOS is an intelligent messaging triage system for adult content creators. It scores incoming messages by predicted value, routes them based on creator preferences, and enables AI-assisted responses for low-value messages only.

## Core Philosophy
- Honest automation: AI handles volume, not relationships
- Creator stays connected to high-value fans (whales)
- Full transparency: creator always knows what's automated
- No deception: fans talking to AI know it (for low-value only)

## Tech Stack
- Backend: Python 3.11+, FastAPI, SQLAlchemy
- Database: PostgreSQL + pgvector for embeddings
- Cache/Queue: Redis + Celery
- LLM: Together.ai (Llama 3.3 70B) - permissive content policy
- Embeddings: sentence-transformers/all-MiniLM-L6-v2
- Headless Browser: Playwright
- Frontend: Next.js + Tailwind + shadcn/ui (later)
- Deployment: Railway

## Directory Structure
```
creatorOS/
├── CLAUDE.md              # This file - context for Claude Code
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── docker-compose.yml     # Local dev environment
│
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI app entry point
│   ├── config.py          # Settings and configuration
│   │
│   ├── api/               # API routes
│   │   ├── __init__.py
│   │   ├── messages.py    # Message intake endpoints
│   │   ├── creators.py    # Creator management
│   │   ├── fans.py        # Fan profiles
│   │   └── webhooks.py    # Platform webhooks
│   │
│   ├── models/            # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── creator.py
│   │   ├── fan.py
│   │   ├── message.py
│   │   ├── conversation.py
│   │   └── platform_credential.py
│   │
│   ├── services/          # Business logic
│   │   ├── __init__.py
│   │   ├── ml_pipeline.py      # Value scoring, intent, summarization
│   │   ├── routing.py          # Routing rules engine
│   │   ├── response_gen.py     # AI response generation
│   │   └── notification.py     # Creator notifications
│   │
│   ├── integrations/      # Platform integrations
│   │   ├── __init__.py
│   │   ├── base.py             # Abstract base class
│   │   ├── telegram_bot.py     # Telegram Bot API
│   │   ├── twilio_sms.py       # Twilio SMS/WhatsApp
│   │   ├── headless/           # Browser-based integrations
│   │   │   ├── __init__.py
│   │   │   ├── browser_pool.py
│   │   │   ├── onlyfans.py
│   │   │   ├── fansly.py
│   │   │   └── sextpanther.py
│   │   └── normalizer.py       # Normalize messages to common format
│   │
│   └── utils/
│       ├── __init__.py
│       ├── encryption.py       # Credential encryption
│       └── logging.py
│
├── workers/               # Celery background tasks
│   ├── __init__.py
│   ├── celery_app.py
│   ├── tasks/
│   │   ├── process_message.py
│   │   ├── send_response.py
│   │   ├── scrape_inbox.py
│   │   └── notify_creator.py
│
├── tests/
│   ├── __init__.py
│   ├── test_ml_pipeline.py
│   ├── test_routing.py
│   └── fixtures/
│       └── sample_messages.py
│
└── scripts/
    ├── seed_db.py
    └── test_integrations.py
```

## Key Data Models

### Message (Normalized)
```python
{
    "id": "uuid",
    "platform": "onlyfans|fansly|telegram|sextpanther|sms",
    "platform_message_id": "string",
    "conversation_id": "uuid",
    "fan_id": "uuid",
    "creator_id": "uuid",
    "direction": "inbound|outbound",
    "content": "string",
    "media_urls": ["string"],
    "timestamp": "datetime",
    "value_score": 0.0-1.0,
    "value_tier": "HIGH|MID|LOW",
    "intent": "greeting|pricing|custom_request|complaint|boundary|other",
    "response_source": "creator|ai_auto|ai_suggested|null",
    "processed_at": "datetime"
}
```

### Fan Profile
```python
{
    "id": "uuid",
    "creator_id": "uuid",
    "platform_profiles": [
        {
            "platform": "onlyfans",
            "platform_user_id": "string",
            "username": "string",
            "display_name": "string"
        }
    ],
    "total_spend": 0.00,
    "message_count": 0,
    "avg_value_score": 0.0,
    "tags": ["whale", "new", "custom_buyer"],
    "notes": "string",
    "last_contact": "datetime",
    "conversation_summary": "string"
}
```

### Creator Settings
```python
{
    "id": "uuid",
    "routing_rules": {
        "high_value_threshold": 0.7,
        "low_value_threshold": 0.3,
        "auto_respond_low": true,
        "hold_message_after_minutes": 120,
        "never_auto_intents": ["boundary", "complaint"],
        "notification_channel": "telegram|sms"
    },
    "persona": {
        "writing_samples": ["string"],
        "tone": "flirty|friendly|professional",
        "emojis": ["💋", "😘"],
        "boundaries": ["string"],
        "pricing": {
            "custom_video_base": 50,
            "sexting_per_minute": 5
        }
    }
}
```

## ML Pipeline

### Value Scoring (v1 - Rules Based)
```python
def score_value(message, fan_history):
    score = 0.5  # baseline
    
    # Boost for spend history
    if fan_history.total_spend > 500:
        score += 0.3
    elif fan_history.total_spend > 100:
        score += 0.2
    elif fan_history.total_spend > 0:
        score += 0.1
    
    # Boost for buying signals
    buying_signals = ["custom", "video", "price", "cost", "buy", "purchase", "order"]
    if any(signal in message.lower() for signal in buying_signals):
        score += 0.2
    
    # Reduce for low-effort messages
    low_effort = ["hey", "hi", "hello", "sup", "yo", "what's up"]
    if message.strip().lower() in low_effort:
        score -= 0.3
    
    return min(max(score, 0.0), 1.0)
```

### Intent Classification
Use LLM with structured output:
```
Classify this message into one of: greeting, pricing_inquiry, custom_request, general_chat, complaint, boundary_violation, tip_thanks, subscription_question

Message: "{message}"

Respond with only the classification.
```

### Conversation Summarization
```
Summarize this conversation for the creator. Include:
- What the fan wants
- Any pricing discussed
- Any commitments made
- Current status (waiting on creator, waiting on fan, resolved)

Keep it under 50 words.

Conversation:
{messages}
```

## Routing Logic
```python
def route_message(message, creator_settings):
    rules = creator_settings.routing_rules
    
    # Never auto-respond to certain intents
    if message.intent in rules.never_auto_intents:
        return Action.NOTIFY_CREATOR_URGENT
    
    # High value -> immediate notification
    if message.value_score >= rules.high_value_threshold:
        return Action.NOTIFY_CREATOR_URGENT
    
    # Mid value -> queue + suggest response
    if message.value_score >= rules.low_value_threshold:
        return Action.QUEUE_WITH_SUGGESTION
    
    # Low value + auto enabled -> auto respond
    if rules.auto_respond_low:
        return Action.AUTO_RESPOND
    
    # Low value + auto disabled -> queue silently
    return Action.QUEUE_SILENT
```

## Integration Interfaces

All platform integrations implement:
```python
class PlatformIntegration(ABC):
    @abstractmethod
    async def connect(self, credentials: dict) -> bool:
        """Establish connection/session"""
        pass
    
    @abstractmethod
    async def fetch_messages(self, since: datetime) -> list[RawMessage]:
        """Fetch new messages from platform"""
        pass
    
    @abstractmethod
    async def send_message(self, conversation_id: str, content: str) -> bool:
        """Send message to platform"""
        pass
    
    @abstractmethod
    async def get_conversation_history(self, conversation_id: str) -> list[RawMessage]:
        """Get full conversation history"""
        pass
```

## Environment Variables
```
DATABASE_URL=postgresql://user:pass@localhost:5432/creatoros
REDIS_URL=redis://localhost:6379
TOGETHER_API_KEY=xxx
TELEGRAM_BOT_TOKEN=xxx
TWILIO_ACCOUNT_SID=xxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_PHONE_NUMBER=xxx
ENCRYPTION_KEY=xxx  # For credential storage
```

## Testing Approach
- Unit tests for ML pipeline (test_ml_pipeline.py)
- Integration tests with mock platforms
- Sample messages in fixtures/sample_messages.py covering:
  - High value whale messages
  - Low effort greetings
  - Pricing inquiries
  - Custom requests
  - Boundary violations
  - Complaints

## Current Priority
1. Get message intake working (Telegram first - cleanest API)
2. ML pipeline scoring + classification
3. Basic dashboard to view messages + scores
4. Response generation + sending
5. Creator notification system

## Commands
```bash
# Start local dev
docker-compose up -d
uvicorn app.main:app --reload

# Run tests
pytest

# Start Celery worker
celery -A workers.celery_app worker --loglevel=info

# Database migrations
alembic upgrade head
```
```

---

### requirements.txt

```
# Web framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
asyncpg==0.29.0
alembic==1.13.1
pgvector==0.2.4

# Redis + Celery
redis==5.0.1
celery==5.3.6

# LLM + ML
httpx==0.26.0
sentence-transformers==2.3.1
numpy==1.26.3

# Telegram
python-telegram-bot==20.7

# Twilio
twilio==8.12.0

# Headless browser
playwright==1.41.1

# Utils
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0
cryptography==41.0.7

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
```

---

### docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: creatoros
      POSTGRES_PASSWORD: devpassword
      POSTGRES_DB: creatoros
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  pgdata:
```

---

### app/main.py (Starter)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CreatorOS",
    description="Intelligent messaging triage for content creators",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "service": "CreatorOS"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Import and include routers
# from app.api import messages, creators, fans, webhooks
# app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
# app.include_router(creators.router, prefix="/api/creators", tags=["creators"])
# app.include_router(fans.router, prefix="/api/fans", tags=["fans"])
# app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
```

---

### app/services/ml_pipeline.py (Starter)

```python
from dataclasses import dataclass
from enum import Enum
import httpx

class ValueTier(Enum):
    HIGH = "HIGH"
    MID = "MID"
    LOW = "LOW"

class Intent(Enum):
    GREETING = "greeting"
    PRICING = "pricing_inquiry"
    CUSTOM_REQUEST = "custom_request"
    GENERAL_CHAT = "general_chat"
    COMPLAINT = "complaint"
    BOUNDARY = "boundary_violation"
    TIP_THANKS = "tip_thanks"
    SUBSCRIPTION = "subscription_question"
    OTHER = "other"

@dataclass
class MLResult:
    value_score: float
    value_tier: ValueTier
    intent: Intent
    summary: str | None = None

class MLPipeline:
    def __init__(self, together_api_key: str):
        self.api_key = together_api_key
        self.base_url = "https://api.together.xyz/v1"
    
    async def process_message(
        self, 
        message: str, 
        fan_spend_history: float = 0,
        conversation_history: list[str] | None = None
    ) -> MLResult:
        """Process a message through the full ML pipeline."""
        
        # 1. Value scoring (rules-based v1)
        value_score = self._score_value(message, fan_spend_history)
        value_tier = self._score_to_tier(value_score)
        
        # 2. Intent classification (LLM)
        intent = await self._classify_intent(message)
        
        # 3. Summarization (only if we have history)
        summary = None
        if conversation_history and len(conversation_history) > 3:
            summary = await self._summarize_conversation(conversation_history)
        
        return MLResult(
            value_score=value_score,
            value_tier=value_tier,
            intent=intent,
            summary=summary
        )
    
    def _score_value(self, message: str, fan_spend: float) -> float:
        """Rules-based value scoring v1."""
        score = 0.5  # baseline
        
        # Boost for spend history
        if fan_spend > 500:
            score += 0.3
        elif fan_spend > 100:
            score += 0.2
        elif fan_spend > 0:
            score += 0.1
        
        # Boost for buying signals
        buying_signals = ["custom", "video", "price", "cost", "buy", "purchase", 
                         "order", "pay", "tip", "ppv", "exclusive"]
        msg_lower = message.lower()
        if any(signal in msg_lower for signal in buying_signals):
            score += 0.2
        
        # Reduce for low-effort messages
        low_effort = ["hey", "hi", "hello", "sup", "yo", "what's up", "hru", 
                      "how are you", "wyd", "what you doing"]
        if message.strip().lower() in low_effort or len(message) < 10:
            score -= 0.3
        
        return min(max(score, 0.0), 1.0)
    
    def _score_to_tier(self, score: float, high_thresh: float = 0.7, low_thresh: float = 0.3) -> ValueTier:
        if score >= high_thresh:
            return ValueTier.HIGH
        elif score >= low_thresh:
            return ValueTier.MID
        return ValueTier.LOW
    
    async def _classify_intent(self, message: str) -> Intent:
        """Use LLM to classify message intent."""
        prompt = f"""Classify this message into exactly one category:
- greeting (hi, hello, hey, etc.)
- pricing_inquiry (asking about prices, costs, rates)
- custom_request (requesting custom content, personalized video, etc.)
- general_chat (casual conversation)
- complaint (unhappy, problem, issue)
- boundary_violation (inappropriate request, pushy, disrespectful)
- tip_thanks (thanking for tip, acknowledging payment)
- subscription_question (about subscription, renewal, access)
- other (doesn't fit above)

Message: "{message}"

Respond with only the category name, nothing else."""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 20,
                        "temperature": 0
                    },
                    timeout=30.0
                )
                result = response.json()
                intent_str = result["choices"][0]["message"]["content"].strip().lower()
                
                # Map to enum
                intent_map = {
                    "greeting": Intent.GREETING,
                    "pricing_inquiry": Intent.PRICING,
                    "custom_request": Intent.CUSTOM_REQUEST,
                    "general_chat": Intent.GENERAL_CHAT,
                    "complaint": Intent.COMPLAINT,
                    "boundary_violation": Intent.BOUNDARY,
                    "tip_thanks": Intent.TIP_THANKS,
                    "subscription_question": Intent.SUBSCRIPTION,
                }
                return intent_map.get(intent_str, Intent.OTHER)
        except Exception as e:
            print(f"Intent classification error: {e}")
            return Intent.OTHER
    
    async def _summarize_conversation(self, messages: list[str]) -> str:
        """Summarize conversation for creator context."""
        conversation_text = "\n".join(messages[-20:])  # Last 20 messages max
        
        prompt = f"""Summarize this conversation for the creator in under 50 words. Include:
- What the fan wants
- Any pricing discussed  
- Current status (who needs to respond)

Conversation:
{conversation_text}

Summary:"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 100,
                        "temperature": 0.3
                    },
                    timeout=30.0
                )
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"Summarization error: {e}")
            return "Unable to summarize"
```

---

### tests/fixtures/sample_messages.py

```python
"""Sample messages for testing the ML pipeline."""

# High value - should score 0.7+
HIGH_VALUE_MESSAGES = [
    {
        "content": "Hey babe, I want to order a custom video. 10 minutes, just for me. What's the price?",
        "fan_spend": 250,
        "expected_tier": "HIGH",
        "expected_intent": "custom_request"
    },
    {
        "content": "I just tipped you $100, can we do a private video call?",
        "fan_spend": 500,
        "expected_tier": "HIGH",
        "expected_intent": "custom_request"
    },
    {
        "content": "What's the cost for exclusive content? I'm a big spender 💰",
        "fan_spend": 300,
        "expected_tier": "HIGH",
        "expected_intent": "pricing_inquiry"
    },
]

# Mid value - should score 0.3-0.7
MID_VALUE_MESSAGES = [
    {
        "content": "Love your content! Do you do customs?",
        "fan_spend": 50,
        "expected_tier": "MID",
        "expected_intent": "custom_request"
    },
    {
        "content": "How much for a video saying my name?",
        "fan_spend": 0,
        "expected_tier": "MID",
        "expected_intent": "pricing_inquiry"
    },
    {
        "content": "Your last post was so hot, when's the next one coming?",
        "fan_spend": 25,
        "expected_tier": "MID",
        "expected_intent": "general_chat"
    },
]

# Low value - should score <0.3
LOW_VALUE_MESSAGES = [
    {
        "content": "hey",
        "fan_spend": 0,
        "expected_tier": "LOW",
        "expected_intent": "greeting"
    },
    {
        "content": "hi beautiful",
        "fan_spend": 0,
        "expected_tier": "LOW",
        "expected_intent": "greeting"
    },
    {
        "content": "wyd",
        "fan_spend": 0,
        "expected_tier": "LOW",
        "expected_intent": "greeting"
    },
    {
        "content": "🔥🔥🔥",
        "fan_spend": 0,
        "expected_tier": "LOW",
        "expected_intent": "general_chat"
    },
]

# Boundary violations - should always notify creator
BOUNDARY_MESSAGES = [
    {
        "content": "Meet me in real life, I'll pay whatever",
        "fan_spend": 100,
        "expected_tier": "MID",  # Score might be mid, but intent overrides
        "expected_intent": "boundary_violation"
    },
    {
        "content": "What's your real name and where do you live?",
        "fan_spend": 50,
        "expected_tier": "MID",
        "expected_intent": "boundary_violation"
    },
]

# Complaints - should always notify creator
COMPLAINT_MESSAGES = [
    {
        "content": "I paid for a custom 2 weeks ago and never got it, wtf",
        "fan_spend": 150,
        "expected_tier": "HIGH",
        "expected_intent": "complaint"
    },
    {
        "content": "This isn't what I asked for, I want a refund",
        "fan_spend": 75,
        "expected_tier": "MID",
        "expected_intent": "complaint"
    },
]
```

---

### scripts/test_ml_pipeline.py

```python
"""Quick script to test ML pipeline with sample messages."""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Add parent dir to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ml_pipeline import MLPipeline
from tests.fixtures.sample_messages import (
    HIGH_VALUE_MESSAGES, 
    MID_VALUE_MESSAGES, 
    LOW_VALUE_MESSAGES,
    BOUNDARY_MESSAGES,
    COMPLAINT_MESSAGES
)

async def test_pipeline():
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        print("ERROR: Set TOGETHER_API_KEY in .env")
        return
    
    pipeline = MLPipeline(api_key)
    
    all_messages = [
        ("HIGH VALUE", HIGH_VALUE_MESSAGES),
        ("MID VALUE", MID_VALUE_MESSAGES),
        ("LOW VALUE", LOW_VALUE_MESSAGES),
        ("BOUNDARY", BOUNDARY_MESSAGES),
        ("COMPLAINT", COMPLAINT_MESSAGES),
    ]
    
    for category, messages in all_messages:
        print(f"\n{'='*60}")
        print(f"  {category} MESSAGES")
        print(f"{'='*60}")
        
        for msg in messages:
            result = await pipeline.process_message(
                message=msg["content"],
                fan_spend_history=msg["fan_spend"]
            )
            
            tier_match = "✅" if result.value_tier.value == msg["expected_tier"] else "❌"
            intent_match = "✅" if result.intent.value == msg["expected_intent"] else "❌"
            
            print(f"\nMessage: \"{msg['content'][:50]}...\"")
            print(f"  Fan spend: ${msg['fan_spend']}")
            print(f"  Score: {result.value_score:.2f} | Tier: {result.value_tier.value} {tier_match}")
            print(f"  Intent: {result.intent.value} {intent_match}")

if __name__ == "__main__":
    asyncio.run(test_pipeline())
```

---

## Part 3: Immediate Actions (Before You Leave)

### Today/Tomorrow (Phone Only)
1. [ ] Talk to Noelle - align on MVP scope, partnership structure
2. [ ] Get intro to Thrace scheduled for when you're back
3. [ ] Create GitHub repo (can do from phone)
4. [ ] Create Railway account if you don't have one
5. [ ] Get Together.ai API key (sign up at together.ai)
6. [ ] Get Telegram Bot token (talk to @BotFather on Telegram)

### Questions for Noelle Call
1. Messaging-first or content-first for MVP?
2. What platform does Thrace primarily use? (Determines first integration)
3. What's Thrace's message volume? (50/day? 500/day?)
4. Partnership structure - how do we formalize this?
5. Who else can pilot test? (Need 3-5 creators)
6. Timeline pressure - is GPTease likely to add messaging soon?

---

## Part 4: Files to Create

When you get home, create these files in this order:

```bash
# 1. Create repo structure
mkdir -p creatorOS/{app/{api,models,services,integrations/headless,utils},workers/tasks,tests/fixtures,scripts}

# 2. Copy scaffolding files
# - CLAUDE.md (from above)
# - requirements.txt
# - docker-compose.yml
# - app/main.py
# - app/services/ml_pipeline.py
# - tests/fixtures/sample_messages.py
# - scripts/test_ml_pipeline.py

# 3. Create .env
cp .env.example .env
# Fill in API keys

# 4. Start services
docker-compose up -d

# 5. Test ML pipeline
python scripts/test_ml_pipeline.py

# 6. You're off to the races
```

---

## Summary

**You have:**
- Full attack plan (4 weeks to pilot-ready)
- CLAUDE.md context file for Claude Code
- Starter code for ML pipeline
- Test fixtures with sample messages
- Docker setup for local dev

**When you get home:**
1. Create repo with scaffolding
2. Point Claude Code at CLAUDE.md
3. Say "Let's build the Telegram integration first"
4. Ship it

**The competitive advantage:** GPTease generates text. You generate + send + score + route. That's the gap.

