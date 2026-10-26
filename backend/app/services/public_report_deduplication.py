import hashlib
from urllib.parse import urlsplit, urlunsplit


def normalize_public_report_url(url: str) -> str:
    """
    Normalize URLs without removing parameters that may
    identify different content.
    """
    parsed = urlsplit(str(url).strip())

    scheme = parsed.scheme.lower()
    hostname = (parsed.hostname or "").lower()

    if hostname.startswith("www."):
        hostname = hostname[4:]

    if parsed.port and parsed.port not in (80, 443):
        hostname = f"{hostname}:{parsed.port}"

    path = parsed.path.rstrip("/") or "/"

    # Only remove query parameters from Instagram post/reel URLs.
    instagram_content = (
        hostname == "instagram.com"
        and len(path.split("/")) >= 3
        and path.split("/")[1] in {"p", "reel", "tv"}
        and bool(path.split("/")[2])
    )

    query = "" if instagram_content else parsed.query

    return urlunsplit(
        (
            scheme,
            hostname,
            path,
            query,
            "",
        )
    )


def public_report_reference(platform: str, url: str) -> str:
    """
    Generate a stable reference for a public report.
    """
    normalized_url = normalize_public_report_url(url)

    identity = (
        f"{platform.strip().lower()}:{normalized_url}"
    )

    digest = hashlib.sha256(
        identity.encode("utf-8")
    ).hexdigest()

    return f"public:{digest}"