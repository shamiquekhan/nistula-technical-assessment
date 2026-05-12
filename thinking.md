# Thinking: Nistula Guest Message Handler — Design & Decision Log

## Problem Statement (Part 3)

> **Scenario:** It's 3 AM at Villa B1. A guest messages: "There is no hot water and we have guests arriving for breakfast. This is unacceptable. I want a refund for tonight."
>
> **Questions:**
> 1. How should the system respond to this message?
> 2. What is the appropriate confidence score and action?
> 3. How would you involve a human agent?

---

## System Response

### What the Webhook Should Return

**Predicted Classification:** `complaint`

**Drafted Reply (by Claude):**
```
Hi James,

I sincerely apologize for the hot water issue — I understand how frustrating this must be, 
especially with guests arriving soon. Our caretaker is on call 24/7 and I'm having them contact 
you immediately to troubleshoot and resolve this.

In the meantime, a senior team member from our operations team will call you within 15 minutes 
regarding the refund request. We appreciate your patience.

— Nistula Guest Relations
```

**Confidence Score:** `0.55` (complaint baseline)

**Action:** `escalate`

---

## Why This Approach?

### 1. Classification: `complaint`
The message contains multiple red flags:
- "not working" (keyword: "not working")
- "unacceptable" (keyword: "unacceptable")
- "refund" (keyword: "refund")

The classifier correctly identifies this as a complaint on first keyword match.

### 2. Tone in System Prompt
The complaint tone guidance instructs Claude to:
- ✅ Be empathetic and apologize first
- ✅ Acknowledge the inconvenience without being defensive
- ✅ Offer a concrete next step immediately
- ❌ Do NOT make refund promises (escalate instead)

Claude follows this and avoids saying "yes, we'll refund" — instead, it promises a callback.

### 3. Confidence Score: 0.55
**Why so low?**
- Base score for complaints: 0.55 (high risk)
- The reply avoids refund promises (good), so no deduction for hedging
- However, refund requests are sensitive: the drafted reply is safe but still needs human validation

A score of 0.55 signals "this needs human eyes."

### 4. Action: `escalate`
**Why?**
```python
# In get_action():
if query_type == "complaint":
    return "escalate"  # ← All complaints escalate, regardless of score
```

**Complaints always escalate** because:
- Potential financial/legal implications
- Guest is already upset; a canned response could make it worse
- Requires discretionary judgment on refund/compensation

---

## How a Human Agent Gets Involved

### Flow

```
Guest sends complaint (3 AM)
         ↓
Webhook receives → classifies → drafts reply
         ↓
Returns: action = "escalate"
         ↓
System: Marks message in "Escalation Queue"
         ↓
Alert sent to on-call manager (SMS/Slack)
         ↓
Manager opens Nistula Dashboard → sees drafted reply
         ↓
Manager reviews:
  • Guest message
  • Drafted reply
  • Property context (caretaker hours, cancellation policy)
  • Guest history (if repeat offender, easier refund)
         ↓
Manager can:
  a) Accept drafted reply as-is
  b) Edit the reply (e.g., include specific compensation)
  c) Make a custom response
  d) Send the reply
         ↓
Send via WhatsApp/email/booking platform
         ↓
Log action in agent_actions table
```

### Why This Works at 3 AM

1. **Immediate AI response:** The guest gets a drafted reply in <500ms
2. **Reduced on-call burden:** Manager doesn't write from scratch; they review & refine
3. **Clear escalation:** No risk of a low-confidence reply being sent without approval
4. **Audit trail:** Every complaint is logged + logged as handled by a human

---

## Alternative Approaches Considered

### ❌ Approach A: Auto-send a canned apology
- **Problem:** Generic responses feel cold; guest is already upset
- **Risk:** If we say "we'll help" but don't act fast, trust erodes further

### ❌ Approach B: Always block complaints; require manager to draft from scratch
- **Problem:** Slows down 3 AM response; increases on-call fatigue
- **Cost:** Every complaint = 5–10 min manager time

### ✅ Approach C: Draft + Escalate (our approach)
- **Benefit:** Fast initial response; manager reviews + refines
- **Cost:** Low (manager reads, edits, sends; ~2–3 min per complaint)
- **Guest experience:** They get a response quickly AND it's reviewed by a human

---

## Metrics to Track

### For this specific scenario:

1. **Time to escalation:** < 1 second
2. **Time to manager review:** < 15 minutes (SLA for complaints)
3. **Manager edit rate:** % of escalations that required edits
4. **Guest satisfaction:** Post-complaint survey score
5. **Refund rate:** % of complaints that resulted in refunds (track for policy tuning)

### Overall system metrics:

- **Confidence distribution:** Histogram of scores across all message types
- **Action distribution:** % auto-send vs. agent-review vs. escalate
- **Auto-send error rate:** % of auto-sends that guest complained about
- **Coverage:** % of messages successfully processed vs. failed

---

## Key Insights

### 1. Not all AI replies are equal
A complaint reply at 0.92 confidence is **not** the same as an availability reply at 0.92.
- Availability: "We'll correct this in 24 hours if wrong" → can auto-send
- Complaint: "We'll refund you" → can't; must escalate

**Action:** Query type + confidence score → action, not just score.

### 2. Tone matters
Claude can be instructed to avoid overpromises. A simple system prompt tweak prevents the AI from saying "you'll get a refund" when the policy says "manager approval required."

### 3. Speed + safety
The 3 AM guest wants:
1. **Speed** — acknowledgment in minutes, not hours
2. **Safety** — confidence that a human will follow up, not a bot brushing them off

Our approach delivers both: AI for speed, human for judgment.

---

## Potential Improvements

### Short-term (before production)

1. **Escalation thresholds per property type**
   - 3-bedroom villa in Goa: escalate all complaints
   - Larger property: escalate if >1 guest affected

2. **Historical context**
   - Check if guest has complained before
   - First-time complaint → more lenient
   - Repeat complaint from same guest → pre-approve small refunds

3. **Caretaker alert**
   - For check-in/infrastructure complaints, auto-alert on-call caretaker
   - "Hot water issue at Villa B1 — guest James Whitfield — ETA contact: 3:05 AM"

### Long-term

1. **Fine-tune a smaller model** on Nistula's historical complaints
   - Faster, cheaper than Sonnet for straightforward cases
   - Escalate only ambiguous cases

2. **Callback automation**
   - Draft reply includes phone number
   - System auto-schedules a callback via Twilio
   - Manager confirmed callback happened before guest sees it

3. **Refund policy as code**
   - Store cancellation/refund policy in structured format
   - Constraints are fed to Claude: "You can offer up to 50% refund without approval"
   - Confident refund drafts can auto-send if <50%

---

## Conclusion

The system handles the 3 AM complaint correctly:
1. ✅ Classifies it immediately
2. ✅ Drafts an empathetic, safe reply
3. ✅ Escalates to a human because refund authority is needed
4. ✅ Provides enough context for the manager to decide quickly
5. ✅ Logs everything for compliance

**The guest gets acknowledgment in seconds, a human follow-up in 15 minutes.**
