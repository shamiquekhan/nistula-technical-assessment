import os
import uuid
import logging
import hmac
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.models import InboundMessage, UnifiedMessage, WebhookResponse
from src.classifier import classify_query_details
from src.claude_client import draft_reply

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY is not set. Check your .env file.")
    yield

app = FastAPI(
    title="Nistula Guest Message Handler",
    description="Receives guest messages, classifies them, and drafts AI replies.",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow the interactive test dashboard (or other local tools) to call this API from the browser.
# In production, restrict allow_origins to trusted origins instead of "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Quick endpoint to confirm the server is running."""
    return {"status": "ok"}


async def verify_webhook_secret(
    x_webhook_secret: str | None = Header(default=None, alias="X-Webhook-Secret"),
):
    """Optionally require a shared secret when WEBHOOK_SECRET is configured."""
    expected_secret = os.getenv("WEBHOOK_SECRET")
    if not expected_secret:
        return

    provided_secret = x_webhook_secret or ""
    if not hmac.compare_digest(provided_secret, expected_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )


@app.post(
    "/webhook/message",
    response_model=WebhookResponse,
    dependencies=[Depends(verify_webhook_secret)],
)
async def handle_message(payload: InboundMessage):
    """
    Receives an inbound guest message, normalises it into a unified schema,
    classifies the query type, drafts a reply via Claude, and returns
    the reply with a confidence score and recommended action.
    """
    # 1. Generate a unique ID for this message
    message_id = str(uuid.uuid4())

    # 2. Classify the query
    query_type, matched_types = classify_query_details(payload.message)
    secondary_types = [item for item in matched_types if item != query_type]

    # 3. Normalise into unified schema
    unified = UnifiedMessage(
        message_id=message_id,
        source=payload.source,
        guest_name=payload.guest_name,
        message_text=payload.message,
        timestamp=payload.timestamp,
        booking_ref=payload.booking_ref,
        property_id=payload.property_id,
        query_type=query_type,
        secondary_query_types=secondary_types,
    )

    # 4. Call Claude API
    try:
        drafted_reply, confidence_score, action = await draft_reply(unified)
    except ValueError as exc:
        logger.warning("Guest message flagged for review: %s", str(exc))
        drafted_reply = (
            f"Hi {payload.guest_name.split()[0]}, thanks for reaching out. "
            "This message needs a quick human review before we send a reply. "
            "Our team will follow up shortly."
        )
        confidence_score = 0.0
        action = "escalate"
    except Exception as e:
        logger.error(f"Claude API error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=502,
            detail=f"Claude API error: {str(e)}"
        )

    # 5. Return structured response
    return WebhookResponse(
        message_id=message_id,
        query_type=query_type,
        drafted_reply=drafted_reply,
        confidence_score=confidence_score,
        action=action,
    )
