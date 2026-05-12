# Part 3: Thinking Questions — 3 AM Complaint Scenario

## Question A — The Immediate Response

**Drafted message:**

"Hi James, I sincerely apologize for the hot water issue — I understand how critical this is with your guests arriving soon. Our 24/7 caretaker is being contacted immediately to resolve this. A senior team member will follow up with you within 15 minutes regarding your refund request. Thank you for your patience."

**Why this wording:** (1) Lead with empathy and urgency — acknowledge the guest's stress. (2) Concrete action — "caretaker contacted now" is specific, not vague. (3) No refund promise — "senior team member will follow up" delegates the financial decision to a human. (4) Short and direct — guest is upset; no fluff.

---

## Question B — The System Design

**What happens beyond the message:**

**Immediate (0–10 seconds):**
- Classify as `complaint` → action = `escalate`
- Log to escalation queue with `urgent` flag (guest arrival in 4 hours)
- Send SMS to on-call operations manager: "🚨 Complaint: Villa B1 | James Whitfield | Hot water + refund request"

**Manager workflow (next 5–15 minutes):**
- Open dashboard → see guest message, property context, drafted reply
- Review and edit if needed (e.g., offer 20% refund if policy allows)
- Send approved reply via WhatsApp/booking platform
- Log action: who responded, when, what decision

**If no manager response in 30 minutes:**
- Escalate to Property Manager → send critical alert
- Guest auto-receives: "Our team is investigating; callback within 30 minutes guaranteed"
- If still unresponded at 45 min: Alert Head of Operations

**Logging:**
- Every interaction (message → draft → review → send) recorded for audit, compliance, and learning

---

## Question C — The Learning (Pattern Detection)

**Problem:** Third hot water complaint in two months at Villa B1 → systemic issue.

**What the system should do:**

**1. Automated pattern detection:**
- Query daily: complaints containing "hot water" OR "no water" grouped by property
- Alert when count ≥ 2 in 60 days: "Recurring issue at Villa B1 — escalate to maintenance"

**2. Preventive action:**
- Flag Villa B1: "Requires boiler inspection before next check-in"
- Require caretaker sign-off: "Hot water tested and working" before guest arrival
- Create maintenance ticket: "Boiler investigation #4521"

**3. Guest communication:**
- Next booking at Villa B1: proactive message — "We've fixed the hot water issue from previous guests. Here's your caretaker's 24/7 number."
- Builds trust and reduces repeat complaints.

**4. System table to track:**
```
property_issues:
  - property_id, issue_type, complaint_count, last_complaint_date
  - When count ≥ 2 in 60 days → auto-escalate to maintenance
  - Link to maintenance_requests table
```

**Long-term improvement:**
- Build a dashboard: "Top 10 recurring issues by property"
- Use 3-month data to identify patterns before they become problems
- Track: Are maintenance fixes actually working? (Do we see the same complaint again?)

---

**Summary:** The system responds immediately, escalates to a human for judgment, logs everything for audit, and uses recurring patterns to prevent future complaints.
