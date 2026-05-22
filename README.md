# MultiChannel-Guest-Agent 

**Author:** Shamique Khan · 
**Stack:** Python 3.11 · FastAPI · PostgreSQL · Claude API (Sonnet 4)

---

## What it does

A webhook server that sits between guest messaging channels and the Nistula operations team. When a guest sends a message - from WhatsApp, Booking.com, Airbnb, Instagram, or the website - the server:

1. Validates and normalises the incoming payload into a unified schema
2. Classifies the query type using a priority-ordered, regex-based classifier
3. Calls the Claude API to draft an appropriate reply with tone guidance per query type
4. Returns a confidence score and a recommended action (`auto_send`, `agent_review`, or `escalate`)

Complaints always escalate regardless of confidence score. Refund promises are blocked at the prompt layer.

---

## Quick start

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Mac / Linux
# venv\Scripts\activate         # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy and configure the environment file
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

# 4. Start the server
uvicorn src.main:app --reload --port 8000
```

Swagger UI is available at `http://localhost:8000/docs`.

---

## API

### `POST /webhook/message`

Accepts a guest message and returns a drafted reply with routing metadata.

**Request**

| Field | Type | Required | Notes |
|---|---|---|---|
| `source` | string | yes | One of `whatsapp`, `booking_com`, `airbnb`, `instagram`, `direct` |
| `guest_name` | string | yes | |
| `message` | string | yes | Raw guest message text |
| `timestamp` | ISO 8601 | yes | |
| `booking_ref` | string | no | Required for post-sales queries |
| `property_id` | string | no | Defaults to villa-b1 context if omitted |

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

**Response**

| Field | Type | Notes |
|---|---|---|
| `message_id` | UUID | Unique per request |
| `query_type` | string | See classification table below |
| `drafted_reply` | string | Claude-generated, ready to send or review |
| `confidence_score` | float | 0.0 - 1.0; routing signal, not a truth score |
| `action` | string | `auto_send`, `agent_review`, or `escalate` |

```json
{
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "query_type": "pre_sales_availability",
  "drafted_reply": "Hi Rahul! Villa B1 is available April 20-24...",
  "confidence_score": 0.92,
  "action": "auto_send"
}
```

Invalid payloads (wrong source, missing fields, malformed timestamp) return **HTTP 422** with Pydantic validation detail.

### `GET /health`

Returns `{"status": "ok"}`. Use for uptime checks.

---

## Classification

The classifier uses a priority-ordered, regex-based rule engine with word boundaries. Priority runs top to bottom - the first match wins.

| Priority | Query type | Triggers on | Base confidence | Action |
|---|---|---|---|---|
| 1 | `complaint` | "unacceptable", "not working", "refund", "terrible", ... | 0.55 | always `escalate` |
| 2 | `special_request` | "early check-in", "late check-out", "airport pickup", "book the chef", ... | 0.80 | `auto_send` |
| 3 | `pre_sales_availability` | "available", "availability", "free from", ... | 0.92 | `auto_send` |
| 4 | `pre_sales_pricing` | "rate", "price", "how much", "nightly", ... | 0.90 | `auto_send` |
| 5 | `post_sales_checkin` | "check-in", "check-out", "wifi", "password", ... | 0.93 | `auto_send` |
| 6 | `general_enquiry` | *(fallback)* | 0.88 | `auto_send` |

**Multi-intent messages** (e.g. "Is it available April 20-24? What's the rate?") resolve to the highest-priority match - availability wins over pricing because confirming dates is the gating question for any booking.

### Action routing

```text
complaint               -> escalate  (always, regardless of score)
confidence >= 0.85      -> auto_send
confidence 0.60 - 0.84  -> agent_review
confidence < 0.60       -> escalate
```

---

## Project structure

```text
.
|- src/
|  |- main.py              # FastAPI app and webhook handler
|  |- models.py            # Pydantic schemas (input validation + unified message format)
|  |- classifier.py        # Priority-ordered, regex-based query classifier
|  |- property_context.py  # Mock property data (swap for DB calls in production)
|  `- claude_client.py     # Claude API integration, prompt building, confidence scoring
|- tests/
|  |- test_webhook.py
|  |- test_comprehensive.py
|  `- test_gaps_closed.py
|- schema.sql               # PostgreSQL schema
|- requirements.txt
|- .env.example
`- README.md
```

---

## Running tests

```bash
# Install test dependencies (already in requirements.txt)
pip install pytest pytest-asyncio httpx

# Run the full suite
pytest -q
```

Current suite status: **14 tests passing**.

---

## Security

**Webhook secret** - set `WEBHOOK_SECRET` in `.env` and pass `X-Webhook-Secret: <secret>` on every request. Requests without the header are rejected with 401.

**Prompt injection** - guest messages are treated as untrusted input. The system prompt explicitly instructs Claude not to follow instructions embedded in guest messages. Injection attempts are flagged for manual review (action: `escalate`).

**Refund guardrail** - the system prompt forbids Claude from making refund or compensation promises. Refund handling requires manager approval and is routed through the escalation queue.

**Input validation** - Pydantic rejects invalid source values, missing required fields, and malformed timestamps before any processing occurs.

---

## Design decisions

| Decision | Rationale |
|---|---|
| Rule-based classifier | Transparent, zero hallucination risk, fast to audit and iterate |
| Availability before pricing in priority chain | Confirming dates is the prerequisite for any pricing discussion |
| Special request before generic check-in | Prevents "early check-in" from being swallowed by the check-in keyword |
| Complaints always escalate | Financial and legal risk too high for automation regardless of confidence |
| Confidence as routing signal | The score determines human-in-the-loop level, not reply accuracy |
| Property context in system prompt | Cheaper than RAG for small, stable property datasets |
| `claude-sonnet-4` | Balances capability, latency (~2s), and API cost for this use case |

---

## Known issues

These are documented bugs in the previous rule-based classifier, included transparently:

| # | Description | Status |
|---|---|---|
| 7 | "Early check-in" was classified as `post_sales_checkin` instead of `special_request` | **Fixed** - special request patterns now take priority |
| 8 | Multi-intent messages (availability + pricing) returned `pre_sales_pricing` | **Fixed** - availability is checked before pricing in the classifier chain |

---

## Next steps

1. **Database** - replace `property_context.py` with PostgreSQL queries using the provided `schema.sql`
2. **Structured logging** - JSON logs to CloudWatch or Datadog; track `query_type`, `action`, `confidence_score`, and response time per request
3. **Channel integrations** - connect to real Booking.com, Airbnb, and WhatsApp Business APIs
4. **Escalation queue** - build the agent dashboard that receives escalated messages and lets managers review, edit, and send drafted replies
5. **Fine-tuning** - collect a dataset of actual messages and preferred replies; fine-tune a smaller model for faster, cheaper inference on common query types
