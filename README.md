# Nistula Guest Message Handler

**From:** Shamique Khan | **Assessment:** Nistula Summer Technology Internship 2026  
**Stack:** Python (FastAPI) + PostgreSQL + Claude API

## Overview

A production-ready webhook server that:
- Receives guest messages from multiple channels (WhatsApp, Booking.com, Airbnb, Instagram, direct)
- Classifies query types (pre-sales availability/pricing, post-sales check-in, complaints, etc.)
- Calls the Claude API to draft intelligent replies
- Returns replies with confidence scores and recommended actions (auto-send, agent review, escalate)

## Quick Start

### 1. Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate      # Mac/Linux
# venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and add your Anthropic API key:

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 3. Start the server

```bash
uvicorn src.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for the Swagger UI.

## API Endpoints

### `POST /webhook/message`

**Request:**
```json
{
  "source": "whatsapp",
  "guest_name": "Rahul Sharma",
  "message": "Is the villa available from April 20 to 24?",
  "timestamp": "2026-05-05T10:30:00Z",
  "booking_ref": "NIS-2024-0891",
  "property_id": "villa-b1"
}
```

**Response:**
```json
{
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "query_type": "pre_sales_availability",
  "drafted_reply": "Hi Rahul! Villa B1 is available April 20–24. Check-in is 2 PM, check-out 11 AM...",
  "confidence_score": 0.92,
  "action": "auto_send"
}
```

### `GET /health`

Quick health check.

## Project Structure

- **`src/models.py`** — Pydantic schemas for input validation and unified message format
- **`src/classifier.py`** — Rule-based query type classification
- **`src/property_context.py`** — Mock property data (replace with DB calls)
- **`src/claude_client.py`** — Claude API integration, prompt building, confidence scoring
- **`src/main.py`** — FastAPI application and webhook handler
- **`tests/test_webhook.py`** — Pytest test suite
- **`schema.sql`** — PostgreSQL database schema

## Testing

### Manual curl test

```bash
curl -X POST http://localhost:8000/webhook/message \
  -H "Content-Type: application/json" \
  -d '{
    "source": "whatsapp",
    "guest_name": "Rahul Sharma",
    "message": "Is the villa available from April 20 to 24?",
    "timestamp": "2026-05-05T10:30:00Z",
    "property_id": "villa-b1"
  }'
```

### Automated tests

```bash
pip install pytest pytest-asyncio httpx
pytest tests/test_webhook.py -v
```

## Design Highlights

### 1. Unified Message Schema
All incoming messages are normalised into a single `UnifiedMessage` schema regardless of source. This simplifies downstream processing.

### 2. Rule-Based Classification
Query classification uses keyword matching ordered by specificity. It's fast, transparent, and easy to debug.

### 3. Confidence Scoring Heuristic
- Base score per query type (for example: availability 0.92, pricing 0.90, check-in 0.93, complaint 0.55)
- Penalise short replies, hedging language, and risky promises
- Complaints always escalate regardless of score because the emotional and operational risk is too high for automation
- The score is a routing signal, not a truth score: high-confidence answers go out automatically, mid-confidence answers can be reviewed, and low-confidence or risky cases escalate

### 4. Security Guardrails
- The webhook can optionally require a shared secret via `WEBHOOK_SECRET` and the `X-Webhook-Secret` header
- Guest messages are treated as untrusted input and prompt-injection attempts are flagged for manual review
- Availability is only confirmed for dates explicitly present in the property context

### 5. Tone Guidance
Each query type gets specific tone guidance in the Claude system prompt, ensuring consistent, appropriate responses.

### 6. Property Context Injection
Property details are formatted and injected directly into the system prompt. This is cheaper than retrieval-augmented generation and works well for small datasets.

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| **FastAPI** | Lightweight, auto-generated Swagger docs, async support |
| **Claude Sonnet 4** | Fast, capable, and cost-effective for message handling |
| **Rule-based classification** | Transparent, no hallucinations, easy to audit |
| **Confidence scoring** | Allows operators to focus on high-risk cases |
| **Separate property file** | Easy to swap for DB calls or external API |

## Next Steps

1. **Database:** Replace `PROPERTY_CONTEXT` with PostgreSQL queries
2. **Logging:** Add structured logging (JSON to CloudWatch or similar)
3. **Webhooks:** Integrate with actual Booking.com, Airbnb APIs
4. **Metrics:** Track confidence scores, action distributions, response times
5. **Fine-tuning:** Build a dataset of actual messages + preferred replies; fine-tune a model

## Author

Shamique Khan — Nistula Summer Technology Internship 2026
