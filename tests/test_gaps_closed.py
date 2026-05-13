import pytest
from httpx import AsyncClient, ASGITransport

from src.claude_client import get_action
from src.main import app
from src.recurring_issues import tracker


@pytest.mark.asyncio
async def test_agent_review_routing_band():
    # Covers the explicit 0.60-0.85 routing band required by the brief.
    assert get_action(0.72, "general_enquiry") == "agent_review"


@pytest.mark.asyncio
async def test_special_request_classification_early_checkin():
    payload = {
        "source": "booking_com",
        "guest_name": "Monica Patel",
        "message": "Can we arrange an early check-in? We arrive at 10am.",
        "timestamp": "2026-05-10T14:30:00Z",
        "booking_ref": "NIS-2024-0950",
        "property_id": "villa-b1",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/webhook/message", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["query_type"] == "special_request"


@pytest.mark.asyncio
async def test_recurring_complaint_detection_escalates_and_flags(monkeypatch):
    tracker.reset()

    async def fake_draft_reply(_message):
        return (
            "I am sorry for the inconvenience. We are escalating this right away.",
            0.55,
            "escalate",
        )

    monkeypatch.setattr("src.main.draft_reply", fake_draft_reply)

    payload = {
        "source": "whatsapp",
        "guest_name": "James Whitfield",
        "message": "There is no hot water and this is unacceptable.",
        "timestamp": "2026-05-07T03:00:00Z",
        "property_id": "villa-b1",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r1 = await ac.post("/webhook/message", json=payload)
        r2 = await ac.post("/webhook/message", json=payload)
        r3 = await ac.post("/webhook/message", json=payload)

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r3.status_code == 200

    d1 = r1.json()
    d2 = r2.json()
    d3 = r3.json()

    assert d1["action"] == "escalate"
    assert d2["action"] == "escalate"
    assert d3["action"] == "escalate"

    assert "recurring issue" not in d1["drafted_reply"].lower()
    assert "recurring issue" not in d2["drafted_reply"].lower()
    assert "recurring issue" in d3["drafted_reply"].lower()

    tracker.reset()
