import socket
import ipaddress
from app.core import settings
from urllib.parse import urlsplit
import httpx

class MediaAnalysisDisabledError(RuntimeError):
    """Media analysis is disabled by configuration."""


def ensure_media_analysis_enabled() -> None:
    """
    Prevent automatic media analysis when
    the feature is disabled.
    """
    if not settings.MEDIA_ANALYSIS_ENABLED:
        raise MediaAnalysisDisabledError(
            "Automatic media analysis is disabled."
        )
def validate_media_url(media_url: str) -> str:
    """
    Perform preliminary validation of a media URL.

    This does not authorize downloading the image
    or establish that the destination is safe.
    """
    if not isinstance(media_url, str) or not media_url:
        raise ValueError("Media URL is required.")

    if len(media_url) > 2048:
        raise ValueError("Media URL is too long.")

    try:
        parsed = urlsplit(media_url)
        port = parsed.port
    except ValueError as exc:
        raise ValueError("Invalid media URL.") from exc

    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or port is not None
    ):
        raise ValueError("Invalid media URL.")
    try:
        ipaddress.ip_address(parsed.hostname)
    except ValueError:
        pass
    else:
        raise ValueError(
            "IP addresses are not allowed as media hosts."
        )

    return media_url

ALLOWED_MEDIA_HOSTS: frozenset[str] = frozenset(
    host.strip().lower()
    for host in __import__("os")
    .getenv("MEDIA_ALLOWED_HOSTS", "")
    .split(",")
    if host.strip()
)


def validate_media_host(media_url: str) -> str:
    """
    Check whether the media URL belongs to an
    explicitly authorized host.

    An empty allowlist blocks every host.
    """
    validated_url = validate_media_url(media_url)

    hostname = urlsplit(validated_url).hostname

    if hostname not in ALLOWED_MEDIA_HOSTS:
        raise ValueError(
            "Media host is not authorized."
        )

    return validated_url
def validate_resolved_ips(hostname: str) -> list[str]:
    """
    Resolve a hostname and reject any destination
    that is not a globally routable IP address.

    This is a preliminary DNS safety check.
    """
    try:
        results = socket.getaddrinfo(
            hostname,
            443,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as exc:
        raise ValueError(
            "Unable to resolve media host."
        ) from exc

    addresses = {
        result[4][0]
        for result in results
    }

    if not addresses:
        raise ValueError(
            "Media host has no IP addresses."
        )

    for address in addresses:
        ip = ipaddress.ip_address(address)

        if not ip.is_global:
            raise ValueError(
                "Media host resolves to a non-public IP address."
            )

    return sorted(addresses)

def create_media_http_client() -> httpx.Client:
    """
    Create an HTTP client with restrictive defaults.

    This client must not be used to fetch media
    until destination IP pinning and authorization
    checks are implemented.
    """
    return httpx.Client(
        follow_redirects=False,
        timeout=httpx.Timeout(10.0),
        trust_env=False,
    )
def validate_media_content_length(
    content_length: str | None,
) -> None:
    """
    Validate the declared response size.

    This is only a preliminary check.
    Actual downloaded bytes must also be limited.
    """
    if content_length is None:
        return

    try:
        size = int(content_length)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Invalid media content length."
        ) from exc

    if size < 0:
        raise ValueError(
            "Invalid media content length."
        )

    if size > settings.MEDIA_MAX_IMAGE_BYTES:
        raise ValueError(
            "Media exceeds the maximum allowed size."
        )
def read_limited_media_chunks(chunks) -> bytes:
    """
    Read image data with a strict size limit.

    Stops processing if the received data exceeds
    the configured maximum size.
    """
    max_bytes = settings.MEDIA_MAX_IMAGE_BYTES
    received = bytearray()

    for chunk in chunks:
        if not isinstance(chunk, bytes):
            raise ValueError(
                "Invalid media data chunk."
            )

        if len(received) + len(chunk) > max_bytes:
            raise ValueError(
                "Media exceeds the maximum allowed size."
            )

        received.extend(chunk)

    return bytes(received)

class PinnedMediaNetworkBackend:
    """
    Network backend for authorized media connections.

    This initial implementation only validates
    the configured IP addresses.
    """

    def __init__(
            self,
            allowed_ips: set[str],
            authorized_host: str | None = None,
        ):
        if not allowed_ips:
            raise ValueError(
                "At least one authorized IP address is required."
            )

        validated_ips = set()

        for address in allowed_ips:
            try:
                ip = ipaddress.ip_address(address)
            except ValueError as exc:
                raise ValueError(
                    "Invalid IP address."
                ) from exc

            if not ip.is_global:
                raise ValueError(
                    "Non-public IP address is not allowed."
                )

            validated_ips.add(str(ip))

        self.allowed_ips = frozenset(validated_ips)

        if authorized_host is not None:
            if (
                not isinstance(authorized_host, str)
                or not authorized_host
                or authorized_host != authorized_host.lower()
                or not authorized_host.isascii()
                or len(authorized_host) > 253
                or not all(
                    label
                    and len(label) <= 63
                    and label[0].isalnum()
                    and label[-1].isalnum()
                    and all(
                        character.isascii()
                        and (character.isalnum() or character == "-")
                        for character in label
                    )
                    for label in authorized_host.split(".")
                )
            ):
                raise ValueError("Invalid authorized media host.")

        self._authorized_host = authorized_host
    @property
    def authorized_host(self) -> str | None:
        return self._authorized_host

    def connect_tcp(
        self,
        host: str,
        port: int,
        timeout: float | None = None,
        local_address: str | None = None,
        socket_options=None,
    ):
        if type(port) is not int or port != 443:
            raise ValueError(
                "Only HTTPS port 443 is allowed."
            )

        if self.authorized_host is None:
            raise ValueError(
                "No authorized media host configured."
            )

        if host != self.authorized_host:
            raise ValueError(
                "Media host does not match authorized host."
            )

        import httpcore

        pinned_ip = sorted(self.allowed_ips)[0]

        backend = httpcore.SyncBackend()

        return backend.connect_tcp(
            host=pinned_ip,
            port=443,
            timeout=timeout,
            local_address=local_address,
            socket_options=socket_options,
                        )
def download_monitored_image(media_url: str) -> bytes:
    """
    Download an image from an explicitly authorized HTTPS host,
    using a connection pinned to its validated IP address.
    """
    import httpcore
    from app.services.image_validation import validate_image

    url = validate_media_host(media_url)
    hostname = urlsplit(url).hostname

    allowed_ips = set(validate_resolved_ips(hostname))

    network_backend = PinnedMediaNetworkBackend(
        allowed_ips=allowed_ips,
        authorized_host=hostname,
    )

    with httpcore.ConnectionPool(
        network_backend=network_backend,
        retries=0,
        max_connections=1,
    ) as pool:
        with pool.stream(
            "GET",
            url,
            headers=[
                (b"accept", b"image/jpeg, image/png"),
            ],
        ) as response:

            if response.status != 200:
                raise ValueError(
                    f"Media download failed: HTTP {response.status}"
                )

            headers = {
                key.decode("ascii").lower(): value.decode(
                    "ascii", errors="ignore"
                )
                for key, value in response.headers
            }

            content_type = (
                headers.get("content-type", "")
                .split(";")[0]
                .strip()
                .lower()
            )
            if content_type not in {
                "image/jpeg",
                "image/png",
            }:
                raise ValueError(
                    "Unsupported media content type."
                )

            content_length = headers.get("content-length")


            image_bytes = read_limited_media_chunks(
                response.iter_stream()
            )

    validate_image(image_bytes)

    return image_bytes
def analyze_monitored_image(media_url: str):
    """
    Analyze an image obtained from an authorized source.
    """
    ensure_media_analysis_enabled()

    from app.services.media_risk_assessment import (
        assess_image_with_rekognition,
    )

    image_bytes = download_monitored_image(media_url)

    return assess_image_with_rekognition(
        image_bytes=image_bytes
    )