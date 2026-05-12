-- ============================================================
-- Nistula Unified Messaging Platform — PostgreSQL Schema
-- ============================================================
-- Design decisions are documented inline.
-- =========================================

-- Table: unified_messages
-- Purpose: Central store of all guest messages, normalised.
-- Why: Provides a single source of truth for all communication,
--      regardless of source channel.

CREATE TABLE unified_messages (
    message_id UUID PRIMARY KEY,
    source VARCHAR(50) NOT NULL,  -- 'whatsapp', 'booking_com', 'airbnb', 'instagram', 'direct'
    guest_name VARCHAR(255) NOT NULL,
    message_text TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    booking_ref VARCHAR(50),  -- optional, may be null for pre-sales
    property_id VARCHAR(50),  -- optional, may be null for general enquiries
    query_type VARCHAR(50) NOT NULL,  -- 'pre_sales_*', 'post_sales_*', 'complaint', 'general_enquiry'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_unified_messages_timestamp ON unified_messages(timestamp);
CREATE INDEX idx_unified_messages_query_type ON unified_messages(query_type);
CREATE INDEX idx_unified_messages_property_id ON unified_messages(property_id);


-- Table: drafted_replies
-- Purpose: Store Claude-generated replies linked to incoming messages.
-- Why: Provides audit trail + allows re-drafting without calling Claude again.

CREATE TABLE drafted_replies (
    reply_id UUID PRIMARY KEY,
    message_id UUID NOT NULL REFERENCES unified_messages(message_id),
    drafted_reply TEXT NOT NULL,
    confidence_score FLOAT NOT NULL,
    action VARCHAR(50) NOT NULL,  -- 'auto_send', 'agent_review', 'escalate'
    model VARCHAR(100) DEFAULT 'claude-sonnet-4-20250514',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_drafted_replies_message_id ON drafted_replies(message_id);
CREATE INDEX idx_drafted_replies_action ON drafted_replies(action);


-- Table: sent_replies
-- Purpose: Record when a drafted reply was actually sent to a guest.
-- Why: Tracks which messages were auto-sent vs. reviewed by humans.

CREATE TABLE sent_replies (
    sent_id UUID PRIMARY KEY,
    message_id UUID NOT NULL REFERENCES unified_messages(message_id),
    reply_id UUID REFERENCES drafted_replies(reply_id),
    sent_via VARCHAR(50) NOT NULL,  -- 'whatsapp', 'email', 'booking_com', etc.
    custom_reply TEXT,  -- If agent edited the draft before sending
    sent_by VARCHAR(100),  -- 'system' if auto-sent, else agent name
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Table: bookings
-- Purpose: Guest bookings linked to properties.
-- Why: Allows us to correlate incoming messages with actual reservations.

CREATE TABLE bookings (
    booking_ref VARCHAR(50) PRIMARY KEY,
    property_id VARCHAR(50) NOT NULL REFERENCES properties(property_id),
    guest_name VARCHAR(255) NOT NULL,
    guest_email VARCHAR(255),
    guest_phone VARCHAR(20),
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    number_of_guests INT,
    booking_status VARCHAR(50),  -- 'confirmed', 'completed', 'cancelled'
    total_price INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bookings_property_id ON bookings(property_id);
CREATE INDEX idx_bookings_guest_email ON bookings(guest_email);


-- Table: agent_actions
-- Purpose: Log of all actions taken by agents (e.g., editing a reply, escalating).
-- Why: Compliance, audit trail, performance metrics.

CREATE TABLE agent_actions (
    action_id UUID PRIMARY KEY,
    message_id UUID NOT NULL REFERENCES unified_messages(message_id),
    agent_name VARCHAR(100) NOT NULL,
    action_type VARCHAR(50) NOT NULL,  -- 'reviewed', 'edited', 'sent', 'escalated'
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agent_actions_message_id ON agent_actions(message_id);
CREATE INDEX idx_agent_actions_agent_name ON agent_actions(agent_name);
