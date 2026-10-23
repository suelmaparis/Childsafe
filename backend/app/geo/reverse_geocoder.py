import json
import urllib.parse
import urllib.request


def reverse_geocode(
    latitude: float,
    longitude: float,
) -> dict:
    """Converte coordenadas numa localização por extenso."""

    if not (-90 <= latitude <= 90):
        raise ValueError("Latitude inválida")

    if not (-180 <= longitude <= 180):
        raise ValueError("Longitude inválida")

    params = urllib.parse.urlencode({
        "lat": latitude,
        "lon": longitude,
        "format": "jsonv2",
        "addressdetails": 1,
        "accept-language": "pt",
    })

    url = (
        "https://nominatim.openstreetmap.org/reverse?"
        + params
    )

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "ChildSafeCV-Geo/0.1",
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=10,
    ) as response:
        data = json.load(response)

    address = data.get("address", {})

    return {
        "latitude": latitude,
        "longitude": longitude,
        "location_text": data.get("display_name"),
        "city": (
            address.get("city")
            or address.get("town")
            or address.get("village")
        ),
        "municipality": address.get("municipality"),
        "country": address.get("country"),
        "source": "OpenStreetMap / Nominatim",
        "verification_status": "pending",
    }
