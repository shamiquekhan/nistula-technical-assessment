-- ============================================================
-- Nistula Unified Messaging Platform — PostgreSQL Schema
-- ============================================================
-- DESIGN DECISION (Hardest Choice):
--   Separating guests from bookings. A single guest may book multiple 
--   times across different properties, channels, and booking sites. We 
--   create a canonical guest_id based on email + phone + name, then link 
--   both bookings and messages to that guest_id. This allows us to track 
--   complaint patterns, refund history, and communication preferences 
--   across the guest's entire relationship with Nistula, not just one booking.
--   
--   We also add a conversations table to group related messages into threads
--   (e.g., multi-turn exchanges about hot water). This enables:
--   - Escalation logic to consider full conversation context
--   - Detection of recurring issues at the same property
--   - Efficient querying of "all messages in this thread"
--
--   All timestamps are TIMESTAMPTZ for timezone-aware audit trails.
-- ============================================================

-- Table: guests
-- Purpose: Canonical guest identity across all bookings and channels.
-- Why: Guests book multiple times. One canonical record per guest 
--      (matched by email + phone combo) allows historical context tracking.

CREATE TABLE guests (
    guest_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    canonical_name VARCHAR(255) NOT NULL,
    primary_email VARCHAR(255) UNIQUE,
    primary_phone VARCHAR(20) UNIQUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_guests_email ON guests(primary_email);
CREATE INDEX idx_guests_phone ON guests(primary_phone);


-- Table: conversations
-- Purpose: Group related messages into threads (e.g., multi-turn exchanges).
-- Why: Escalation and pattern detection need full context, not just one message.
--      Enables: recurring issue detection, conversation history, thread-level escalation.

CREATE TABLE conversations (
    conversation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guest_id UUID NOT NULL REFERENCES guests(guest_id),
    booking_ref VARCHAR(50) REFERENCES bookings(booking_ref),
    property_id VARCHAR(50) REFERENCES properties(property_id),
    source VARCHAR(50) NOT NULL,  -- 'whatsapp', 'booking_com', 'airbnb', 'instagram', 'direct'
    status VARCHAR(50) DEFAULT 'open',  -- 'open', 'in_progress', 'resolved', 'escalated'
    opened_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversations_guest_id ON conversations(guest_id);
CREATE INDEX idx_conversations_property_id ON conversations(property_id);
CREATE INDEX idx_conversations_status ON conversations(status);


-- Table: unified_messages
-- Purpose: Central store of all guest messages, normalised.
-- Why: Provides a single source of truth for all communication,
--      regardless of source channel. Linked to guest + conversation for context.

CREATE TABLE unified_messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(conversation_id),
    guest_id UUID NOT NULL REFERENCES guests(guest_id),
    source VARCHAR(50) NOT NULL,  -- 'whatsapp', 'booking_com', 'airbnb', 'instagram', 'direct'
    message_text TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    booking_ref VARCHAR(50) REFERENCES bookings(booking_ref),
    property_id VARCHAR(50) REFERENCES properties(property_id),
    query_type VARCHAR(50) NOT NULL,  -- 'pre_sales_*', 'post_sales_*', 'complaint', 'general_enquiry', 'special_request'
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_unified_messages_conversation_id ON unified_messages(conversation_id);
CREATE INDEX idx_unified_messages_guest_id ON unified_messages(guest_id);
CREATE INDEX idx_unified_messages_timestamp ON unified_messages(timestamp);
CREATE INDEX idx_unified_messages_query_type ON unified_messages(query_type);
CREATE INDEX idx_unified_messages_property_id ON unified_messages(property_id);


-- Table: drafted_replies
-- Purpose: Store Claude-generated replies linked to incoming messages.
-- Why: Provides audit trail + allows re-drafting without calling Claude again.
--      Tracks confidence score and action recommendation for each draft.

CREATE TABLE drafted_replies (
    reply_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES unified_messages(message_id),
    drafted_reply TEXT NOT NULL,
    confidence_score FLOAT NOT NULL,
    action VARCHAR(50) NOT NULL,  -- 'auto_send', 'agent_review', 'escalate'
    model VARCHAR(100) DEFAULT 'claude-sonnet-4-20250514',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_drafted_replies_message_id ON drafted_replies(message_id);
CREATE INDEX idx_drafted_replies_action ON drafted_replies(action);


-- Table: sent_replies
-- Purpose: Record when a drafted reply was actually sent to a guest.
-- Why: Tracks which messages were auto-sent vs. reviewed/edited by humans.
--      Audit trail for compliance + customer service quality metrics.

CREATE TABLE sent_replies (
    sent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES unified_messages(message_id),
    reply_id UUID REFERENCES drafted_replies(reply_id),
    sent_via VARCHAR(50) NOT NULL,  -- 'whatsapp', 'email', 'booking_com', etc.
    custom_reply TEXT,  -- If agent edited the draft before sending
    sent_by VARCHAR(100),  -- 'system' if auto-sent, else agent name
    sent_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sent_replies_message_id ON sent_replies(message_id);
CREATE INDEX idx_sent_replies_sent_by ON sent_replies(sent_by);


-- Table: properties
-- Purpose: Master record of all Nistula properties.
-- Why: Separates property metadata from message data.

CREATE TABLE properties (
    property_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    bedrooms INT,
    max_guests INT,
    private_pool BOOLEAN,
    check_in_time VARCHAR(50),
    check_out_time VARCHAR(50),
    base_rate_inr INT,
    extra_guest_rate_inr INT,
    wifi_password VARCHAR(255),
    caretaker_hours VARCHAR(255),
    chef_on_call BOOLEAN,
    chef_note TEXT,
    cancellation_policy TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);


-- Table: bookings
-- Purpose: Guest bookings linked to properties and guests.
-- Why: Allows correlation of incoming messages with actual reservations.
--      Links to canonical guest_id for multi-booking history.

CREATE TABLE bookings (
    booking_ref VARCHAR(50) PRIMARY KEY,
    guest_id UUID NOT NULL REFERENCES guests(guest_id),
    property_id VARCHAR(50) NOT NULL REFERENCES properties(property_id),
    guest_name VARCHAR(255) NOT NULL,
    guest_email VARCHAR(255),
    guest_phone VARCHAR(20),
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    number_of_guests INT,
    booking_status VARCHAR(50),  -- 'confirmed', 'completed', 'cancelled'
    total_price INT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bookings_guest_id ON bookings(guest_id);
CREATE INDEX idx_bookings_property_id ON bookings(property_id);
CREATE INDEX idx_bookings_guest_email ON bookings(guest_email);


-- Table: agent_actions
-- Purpose: Log of all actions taken by agents (e.g., editing a reply, escalating).
-- Why: Compliance, audit trail, performance metrics, SLA tracking.

CREATE TABLE agent_actions (
    action_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES unified_messages(message_id),
    agent_name VARCHAR(100) NOT NULL,
    action_type VARCHAR(50) NOT NULL,  -- 'reviewed', 'edited', 'sent', 'escalated'
    details TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agent_actions_message_id ON agent_actions(message_id);
CREATE INDEX idx_agent_actions_agent_name ON agent_actions(agent_name);
