from collections import defaultdict, deque
from datetime import datetime, timedelta


def _normalize_issue_signature(message_text: str) -> str:
    text = message_text.lower()
    if "hot water" in text:
        return "hot_water"
    if "ac" in text or "air condition" in text:
        return "ac"
    if "power" in text or "electric" in text:
        return "power"
    if "wifi" in text or "wi-fi" in text:
        return "wifi"
    if "pool" in text:
        return "pool"
    if "refund" in text:
        return "refund_request"
    return "general_complaint"


class RecurringIssueTracker:
    """Tracks repeated complaints by property and normalized issue signature."""

    def __init__(self, threshold: int = 3, lookback_days: int = 30):
        self.threshold = threshold
        self.lookback_window = timedelta(days=lookback_days)
        self._events: dict[tuple[str, str], deque[datetime]] = defaultdict(deque)

    def reset(self) -> None:
        self._events.clear()

    def record_complaint(self, property_id: str | None, message_text: str, when: datetime) -> tuple[bool, int, str]:
        property_key = property_id or "unknown_property"
        issue_signature = _normalize_issue_signature(message_text)
        key = (property_key, issue_signature)

        events = self._events[key]
        cutoff = when - self.lookback_window
        while events and events[0] < cutoff:
            events.popleft()

        events.append(when)
        count = len(events)
        is_recurring = count >= self.threshold
        return is_recurring, count, issue_signature


tracker = RecurringIssueTracker()