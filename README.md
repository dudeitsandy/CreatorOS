# CreatorOS

An intelligent messaging triage system for content creators.

## Overview

CreatorOS helps content creators manage high volumes of fan messages by automatically scoring message value, classifying intent, and routing messages to the appropriate action — whether that's notifying the creator urgently, generating an AI-suggested reply, or auto-responding.

## Features

- **Multi-platform ingestion**: Telegram, SMS (Twilio), OnlyFans, Fansly, SextPanther
- **ML-powered triage**: Value scoring + intent classification via Together.ai Llama-3.3-70B
- **Smart routing**: Rules-based routing based on creator preferences
- **AI response generation**: Auto-suggest or auto-send responses
- **Conversation summarization**: Condense long conversations into <50-word summaries

## Quick Start

```bash
cp .env.example .env
# Fill in your API keys in .env

docker-compose up -d
pip install -r requirements.txt

uvicorn app.main:app --reload
```

## API Endpoints

- `GET /health` — Health check
- `POST /api/messages/incoming` — Ingest a new message
- `GET /api/messages` — List messages
- `GET /api/creators` — List creators
- `POST /api/creators` — Create a creator
- `GET /api/creators/{creator_id}` — Get a creator
- `PUT /api/creators/{creator_id}` — Update a creator
- `DELETE /api/creators/{creator_id}` — Delete a creator
- `POST /webhooks/telegram` — Telegram webhook
- `POST /webhooks/twilio` — Twilio webhook

## Running Tests

```bash
pytest tests/
```

## Testing the ML Pipeline

```bash
python scripts/test_pipeline.py
```
