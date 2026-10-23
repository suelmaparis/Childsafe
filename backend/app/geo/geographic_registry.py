"""Registo geográfico do ChildSafeCV.

As coordenadas devem ser obtidas de fontes
públicas verificáveis e identificadas.
"""

GEOGRAPHIC_REGISTRY: dict[str, dict] = {}


def find_geographic_location(name: str) -> dict | None:
    """Procura uma localidade ou instituição no registo."""
    return GEOGRAPHIC_REGISTRY.get(
        name.strip().casefold()
    )


def register_geographic_location(
    name: str,
    latitude: float,
    longitude: float,
    source: str,
    source_url: str,
    location_type: str = "locality",
) -> None:
    """Regista coordenadas com identificação da fonte."""
    if not (-90 <= latitude <= 90):
        raise ValueError("Latitude inválida")

    if not (-180 <= longitude <= 180):
        raise ValueError("Longitude inválida")

    if not source.strip() or not source_url.strip():
        raise ValueError("A fonte é obrigatória")

    GEOGRAPHIC_REGISTRY[name.strip().casefold()] = {
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
        "source": source,
        "source_url": source_url,
        "location_type": location_type,
        "verification_status": "pending",
    }
