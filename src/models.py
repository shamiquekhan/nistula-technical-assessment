from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime
import uuid


# ── Inbound webhook payload ──────────────────────────────────────────────────

class InboundMessage(BaseModel):
    source: Literal["whatsapp", "booking_com", "airbnb", "instagram", "direct"]
    guest_name: str
    message: str
    timestamp: datetime
    booking_ref: Optional[str] = None
    property_id: Optional[str] = None


# ── Query types ──────────────────────────────────────────────────────────────

QueryType = Literal[
    "pre_sales_availability",
    "pre_sales_pricing",
    "post_sales_checkin",
    "special_request",
    "complaint",
    "general_enquiry",
]


# ── Unified internal schema ──────────────────────────────────────────────────

class UnifiedMessage(BaseModel):
    message_id: str
    source: str
    guest_name: str
    message_text: str
    timestamp: datetime
    booking_ref: Optional[str] = None
    property_id: Optional[str] = None
    query_type: QueryType
    secondary_query_types: list[QueryType] = Field(default_factory=list)


# ── Webhook response ─────────────────────────────────────────────────────────

class WebhookResponse(BaseModel):
    message_id: str
    query_type: QueryType
    drafted_reply: str
    confidence_score: float
    action: Literal["auto_send", "agent_review", "escalate"]
