# thinking.md

## Question A — The Immediate Response

Hi [Guest Name], I'm very sorry you're experiencing no hot water right now — I know this is especially disruptive with guests arriving soon. I've escalated this immediately to the on-call caretaker who is being contacted now and will call you within 15 minutes. In the meantime, please try the guest bathroom shower which runs on a separate unit; we'll arrange an alternative if needed. Thank you for your patience — we're on this and will follow up shortly.

I chose this wording because: it acknowledges urgency, avoids robotic phrasing, and buys a short, concrete window for a human to respond without promising refunds or definitive outcomes.

## Question B — System Design Beyond the Message

Flow: complaint classified → conversation created → escalation record written → on-call caretaker + operations manager notified (SMS/Slack) → message queued in escalation dashboard → caretaker auto-notified separately → full audit log entry.

If no human responds within 30 minutes: a second alert is sent to the backup on-call and senior manager; SLA breach is logged and the guest receives an automated follow-up: "We haven't forgotten you — a senior manager is now handling this and will call you within 5 minutes." The escalation remains flagged for post-incident review.

## Question C — The Learning

Pattern detection: run a query like

SELECT count(*) FROM unified_messages
WHERE query_type='complaint' AND message_text ILIKE '%hot water%'
  AND property_id='villa-b1' AND timestamp > NOW() - INTERVAL '60 days';

If count >= 3: auto-create a Property Alert, generate a maintenance ticket, and flag future bookings for pre-stay inspection. What I'd build: a Predictive Maintenance module (IoT + ticketing), a pre-stay checklist for flagged properties, and a dashboard metric showing recurring complaint rate per property. After the second complaint, create a maintenance task; after the third, require a pre-stay inspection before accepting new bookings.

