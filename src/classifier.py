import re

from src.models import QueryType


def _compile(patterns: list[str]) -> re.Pattern[str]:
    combined = "|".join(f"(?:{pattern})" for pattern in patterns)
    return re.compile(combined, re.IGNORECASE)


_RE_COMPLAINT = _compile(
    [
        r"\bunacceptable\b",
        r"\bnot working\b",
        r"\bdoesn['`]?t work\b",
        r"\bwon['`]?t work\b",
        r"\bbroken\b",
        r"\brefund\b",
        r"\bterrible\b",
        r"\bawful\b",
        r"\bfurious\b",
        r"\bvery unhappy\b",
        r"\bextremely unhappy\b",
        r"\bvery angry\b",
        r"\bcomplaint\b",
        r"\bdirty\b",
        r"\bnot clean\b",
        r"\boutrageous\b",
        r"\bdisgusting\b",
        r"\bpoor quality\b",
        r"\bno hot water\b",
        r"\bno water\b",
        r"\bno electricity\b",
        r"\bpower cut\b",
        r"\bpower is out\b",
        r"\bac is not working\b",
    ]
)

# Must be checked before generic check-in/check-out patterns.
_RE_SPECIAL_REQUEST = _compile(
    [
        r"\bearly check.?in\b",
        r"\bearly arrival\b",
        r"\blate check.?out\b",
        r"\blate checkout\b",
        r"\blate departure\b",
        r"\blate check out\b",
        r"\bairport (pickup|pick.?up|transfer|drop|collection)\b",
        r"\bpick.?up from (the )?airport\b",
        r"\barrange.*(car|transfer|transport|taxi|pickup)\b",
        r"\bbook.*(chef|cook|private dining)\b",
        r"\bchef for (dinner|lunch|breakfast)\b",
        r"\bprivate chef\b",
        r"\bflower arrangement\b",
        r"\bspecial occasion\b",
        r"\banniversary\b",
        r"\bhoneymoon\b",
        r"\bbirthday (setup|decoration|surprise)\b",
        r"\bwelcome (pack|basket|gift)\b",
        r"\bextra bed\b",
        r"\bbaby cot\b",
        r"\bhigh chair\b",
    ]
)

_RE_AVAILABILITY = _compile(
    [
        r"\bavailable\b",
        r"\bavailability\b",
        r"\bfree from\b",
        r"\bopen from\b",
        r"\bvacant\b",
        r"\bbook from\b",
        r"\bis it free\b",
        r"\banything available\b",
        r"\bslot available\b",
        r"\bbook(ing)?\b",
        r"\bdates\b",
        r"\bstay\b",
    ]
)

_RE_PRICING = _compile(
    [
        r"\b(nightly |per.?night |daily )?rate\b",
        r"\bpric(e|es|ing)\b",
        r"\bhow much\b",
        r"\btotal cost\b",
        r"\bcost for\b",
        r"\bper night\b",
        r"\bnightly\b",
        r"\bfee\b",
        r"\btariff\b",
        r"\bdiscount\b",
        r"\bweekly rate\b",
        r"\bcharge\b",
        r"\bquote\b",
        r"\bamount\b",
        r"\badult\b",
        r"\bperson\b",
    ]
)

_RE_CHECKIN = _compile(
    [
        r"\bcheck.?in\b",
        r"\bcheck.?out\b",
        r"\bwi.?fi\b",
        r"\bpassword\b",
        r"\baccess code\b",
        r"\bfront door code\b",
        r"\bkey collection\b",
        r"\barrival time\b",
        r"\bdeparture time\b",
        r"\bdirections\b",
        r"\bhow do (we|i) get (in|there)\b",
        r"\bself.?check\b",
        r"\bcaretaker\b",
        r"\bcontact\b",
        r"\bphone number\b",
    ]
)

_RE_GENERAL = _compile(
    [
        r"\bpet(s)?\b",
        r"\bdog(s)?\b",
        r"\bcat(s)?\b",
        r"\bparking\b",
        r"\bpool\b",
        r"\bbeach\b",
        r"\bnearby\b",
        r"\bdistance\b",
        r"\bmarket\b",
        r"\brestaurant\b",
        r"\brules?\b",
        r"\bpolicy\b",
        r"\ballow\b",
    ]
)


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
    text = message_text.strip()

    has_complaint = bool(_RE_COMPLAINT.search(text))
    has_special = bool(_RE_SPECIAL_REQUEST.search(text))
    has_availability = bool(_RE_AVAILABILITY.search(text))
    has_pricing = bool(_RE_PRICING.search(text))
    has_checkin = bool(_RE_CHECKIN.search(text))
    has_general = bool(_RE_GENERAL.search(text))

    matched: list[QueryType] = []
    if has_complaint:
        matched.append("complaint")
    if has_special:
        matched.append("special_request")
    if has_availability:
        matched.append("pre_sales_availability")
    if has_pricing:
        matched.append("pre_sales_pricing")
    if has_checkin:
        matched.append("post_sales_checkin")
    if has_general:
        matched.append("general_enquiry")

    if has_complaint:
        return "complaint", matched
    if has_special:
        return "special_request", matched
    if has_availability:
        return "pre_sales_availability", matched
    if has_pricing:
        return "pre_sales_pricing", matched
    if has_checkin:
        return "post_sales_checkin", matched
    if has_general:
        return "general_enquiry", matched

    return "general_enquiry", []
