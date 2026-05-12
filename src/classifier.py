from src.models import QueryType


# Keyword lists ordered from most specific to least specific.
# The first match wins.
CLASSIFICATION_RULES: list[tuple[QueryType, list[str]]] = [
    (
        "complaint",
        [
            "not working", "broken", "unacceptable", "refund", "complain",
            "disappointed", "disgusting", "worst", "unhappy", "terrible",
            "no hot water", "no water", "no electricity", "power cut", "dirty",
        ],
    ),
    (
        "post_sales_checkin",
        [
            "check in", "check-in", "checkin", "check out", "check-out", "checkout",
            "wifi", "wi-fi", "password", "key", "access", "arrival", "directions",
            "caretaker", "contact", "phone number",
        ],
    ),
    (
        "special_request",
        [
            "early check", "late check", "airport transfer", "pickup", "drop",
            "birthday", "anniversary", "decoration", "extra bed", "cot", "baby",
            "chef", "cook", "meal", "breakfast", "dinner",
        ],
    ),
    (
        "pre_sales_pricing",
        [
            "rate", "price", "cost", "charge", "fee", "how much", "per night",
            "total", "amount", "quote", "pricing", "adult", "person",
        ],
    ),
    (
        "pre_sales_availability",
        [
            "available", "availability", "book", "booking", "dates", "stay",
            "april", "may", "june", "july", "august", "september",
            "october", "november", "december", "january", "february", "march",
        ],
    ),
    (
        "general_enquiry",
        [
            "pet", "dog", "cat", "parking", "pool", "beach", "nearby",
            "distance", "market", "restaurant", "rules", "policy", "allow",
        ],
    ),
]


def classify_query(message_text: str) -> QueryType:
    """
    Return the query type for a guest message.
    Lowercases the text and matches keywords in priority order.
    Falls back to 'general_enquiry' if nothing matches.
    """
    return classify_query_details(message_text)[0]


def classify_query_details(message_text: str) -> tuple[QueryType, list[QueryType]]:
    """
    Return the primary query type plus all matched types in priority order.
    """
    text = message_text.lower()
    matched: list[QueryType] = []
    for query_type, keywords in CLASSIFICATION_RULES:
        if any(kw in text for kw in keywords):
            matched.append(query_type)

    if not matched:
        return "general_enquiry", []

    return matched[0], matched
