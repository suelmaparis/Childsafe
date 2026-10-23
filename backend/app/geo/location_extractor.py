import re

from app.monitoring.signal_extractor import (
    LOCATION_TERMS,
    normalize_text,
)


def extract_locations(text: str | None) -> dict:
    """Identifica referências geográficas explícitas no texto."""
    normalized = normalize_text(text)

    matches = []

    found_locations = []

    for location in LOCATION_TERMS:
            normalized_location = normalize_text(location)

            pattern = (
                r"(?<!\w)"
                + re.escape(normalized_location)
                + r"(?!\w)"
            )

            match = re.search(pattern, normalized)

            if match:
                found_locations.append(
                    (match.start(), location)
                )

    matches = [
            location
            for _, location in sorted(found_locations)
        ]
    return {
        "locations": matches,
        "location_detected": bool(matches),
        "source": "publication_text",
        "latitude": None,
        "longitude": None,
        "verification_status": "pending" if matches else "unknown",
    }
