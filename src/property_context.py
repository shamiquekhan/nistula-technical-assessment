PROPERTY_CONTEXT = {
    "villa-b1": {
        "name": "Villa B1",
        "location": "Assagao, North Goa",
        "bedrooms": 3,
        "max_guests": 6,
        "private_pool": True,
        "check_in": "2:00 PM",
        "check_out": "11:00 AM",
        "base_rate_inr": 18000,
        "base_rate_guests": 4,
        "extra_guest_rate_inr": 2000,
        "wifi_password": "Nistula@2024",
        "caretaker_hours": "8:00 AM to 10:00 PM",
        "chef_on_call": True,
        "chef_note": "Pre-booking required",
        "availability_april_20_24": True,
        "availability_note": (
            "For assessment purposes, April 20-24 is available. "
            "Do not confirm availability for other dates unless explicitly provided."
        ),
        "cancellation_policy": "Free cancellation up to 7 days before check-in",
    }
}


def get_property_context_string(property_id: str) -> str:
    """Return a formatted string of property details for injection into Claude prompt."""
    ctx = PROPERTY_CONTEXT.get(property_id)
    if not ctx:
        return "No property data available."

    availability = "Available" if ctx["availability_april_20_24"] else "Not available"

    return f"""
Property: {ctx['name']}, {ctx['location']}
Bedrooms: {ctx['bedrooms']} | Max guests: {ctx['max_guests']} | Private pool: {'Yes' if ctx['private_pool'] else 'No'}
Check-in: {ctx['check_in']} | Check-out: {ctx['check_out']}
Base rate: INR {ctx['base_rate_inr']:,} per night (up to {ctx['base_rate_guests']} guests)
Extra guest: INR {ctx['extra_guest_rate_inr']:,} per night per person
WiFi password: {ctx['wifi_password']}
Caretaker: Available {ctx['caretaker_hours']}
Chef on call: {'Yes' if ctx['chef_on_call'] else 'No'} — {ctx['chef_note']}
Availability April 20–24: {availability}
Availability scope: {ctx['availability_note']}
Cancellation: {ctx['cancellation_policy']}
""".strip()
