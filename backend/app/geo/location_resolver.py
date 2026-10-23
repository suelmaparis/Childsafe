from app.geo.location_extractor import extract_locations
from app.geo.geographic_registry import find_geographic_location


def resolve_location(text: str | None) -> dict:
    """Identifica locais e consulta coordenadas registadas."""
    extracted = extract_locations(text)
    results = []

    for name in extracted["locations"]:
        registered = find_geographic_location(name)

        if registered:
            results.append({
                **registered,
                "match_source": "publication_text",
            })
        else:
            results.append({
                "name": name,
                "latitude": None,
                "longitude": None,
                "source": "publication_text",
                "source_url": None,
                "verification_status": "pending",
            })

    return {
        "locations": results,
        "location_detected": bool(results),
    }
