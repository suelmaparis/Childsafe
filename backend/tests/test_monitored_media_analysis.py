import pytest

from app.core import settings

from app.services.monitored_media_analysis import (
    MediaAnalysisDisabledError,
    PinnedMediaNetworkBackend,
    create_media_http_client,
    ensure_media_analysis_enabled,
    read_limited_media_chunks,
    validate_media_content_length,
    validate_media_host,
    validate_media_url,
    validate_resolved_ips,
)


# ============================================================
# MEDIA ANALYSIS FEATURE FLAG
# ============================================================

def test_automatic_media_analysis_disabled(monkeypatch):
    monkeypatch.setattr(
        settings,
        "MEDIA_ANALYSIS_ENABLED",
        False,
    )

    with pytest.raises(
        MediaAnalysisDisabledError,
        match="Automatic media analysis is disabled.",
    ):
        ensure_media_analysis_enabled()


def test_automatic_media_analysis_enabled(monkeypatch):
    monkeypatch.setattr(
        settings,
        "MEDIA_ANALYSIS_ENABLED",
        True,
    )

    assert ensure_media_analysis_enabled() is None


# ============================================================
# MEDIA URL VALIDATION
# ============================================================

@pytest.mark.parametrize(
    "media_url",
    [
        "",
        "http://example.com/image.jpg",
        "ftp://example.com/image.jpg",
        "https://",
        "https://user:password@example.com/image.jpg",
        "https://example.com:8443/image.jpg",
        "https://example.com/" + "a" * 2048,
        "not-a-url",
    ],
)
def test_validate_media_url_rejects_invalid_urls(media_url):
    with pytest.raises(ValueError):
        validate_media_url(media_url)


def test_validate_media_url_accepts_https():
    media_url = "https://example.com/image.jpg"

    assert validate_media_url(media_url) == media_url


@pytest.mark.parametrize(
    "media_url",
    [
        "https://example.com/image.jpg",
        "https://www.instagram.com/image.jpg",
        "https://cdninstagram.com/image.jpg",
        "https://example.org/photo.png",
    ],
)
def test_media_host_is_blocked_by_default(media_url):
    with pytest.raises(
        ValueError,
        match="Media host is not authorized.",
    ):
        validate_media_host(media_url)


def test_media_host_accepts_exact_allowed_host(monkeypatch):
    from app.services import monitored_media_analysis

    monkeypatch.setattr(
        monitored_media_analysis,
        "ALLOWED_MEDIA_HOSTS",
        frozenset({"images.example.com"}),
    )

    url = "https://images.example.com/photo.jpg"

    assert validate_media_host(url) == url


@pytest.mark.parametrize(
    "url",
    [
        "https://images.example.com.evil.org/photo.jpg",
        "https://evil-images.example.com/photo.jpg",
        "https://example.com/photo.jpg",
    ],
)
def test_media_host_rejects_similar_domains(
    monkeypatch,
    url,
):
    from app.services import monitored_media_analysis

    monkeypatch.setattr(
        monitored_media_analysis,
        "ALLOWED_MEDIA_HOSTS",
        frozenset({"images.example.com"}),
    )

    with pytest.raises(
        ValueError,
        match="Media host is not authorized.",
    ):
        validate_media_host(url)


@pytest.mark.parametrize(
    "media_url",
    [
        "https://127.0.0.1/image.jpg",
        "https://192.168.1.1/image.jpg",
        "https://10.0.0.1/image.jpg",
        "https://169.254.169.254/image.jpg",
        "https://8.8.8.8/image.jpg",
        "https://[::1]/image.jpg",
        "https://[2001:db8::1]/image.jpg",
    ],
)
def test_validate_media_url_rejects_ip_addresses(media_url):
    with pytest.raises(
        ValueError,
        match="IP addresses are not allowed as media hosts.",
    ):
        validate_media_url(media_url)


# ============================================================
# DNS AND IP VALIDATION
# ============================================================

@pytest.mark.parametrize(
    "ip_address",
    [
        "127.0.0.1",
        "192.168.1.10",
        "10.0.0.5",
        "169.254.169.254",
        "::1",
        "fc00::1",
    ],
)
def test_resolved_ips_reject_private_addresses(
    monkeypatch,
    ip_address,
):
    def fake_getaddrinfo(*args, **kwargs):
        return [
            (
                None,
                None,
                None,
                None,
                (ip_address, 443),
            )
        ]

    monkeypatch.setattr(
        "app.services.monitored_media_analysis.socket.getaddrinfo",
        fake_getaddrinfo,
    )

    with pytest.raises(
        ValueError,
        match="Media host resolves to a non-public IP address.",
    ):
        validate_resolved_ips("images.example.com")


def test_resolved_ips_accept_public_address(monkeypatch):
    def fake_getaddrinfo(*args, **kwargs):
        return [
            (
                None,
                None,
                None,
                None,
                ("8.8.8.8", 443),
            )
        ]

    monkeypatch.setattr(
        "app.services.monitored_media_analysis.socket.getaddrinfo",
        fake_getaddrinfo,
    )

    assert validate_resolved_ips(
        "images.example.com"
    ) == ["8.8.8.8"]


def test_resolved_ips_reject_mixed_addresses(monkeypatch):
    def fake_getaddrinfo(*args, **kwargs):
        return [
            (None, None, None, None, ("8.8.8.8", 443)),
            (None, None, None, None, ("127.0.0.1", 443)),
        ]

    monkeypatch.setattr(
        "app.services.monitored_media_analysis.socket.getaddrinfo",
        fake_getaddrinfo,
    )

    with pytest.raises(
        ValueError,
        match="Media host resolves to a non-public IP address.",
    ):
        validate_resolved_ips("images.example.com")


# ============================================================
# HTTP CLIENT SECURITY
# ============================================================

def test_media_http_client_security_settings():
    with create_media_http_client() as client:
        assert client.follow_redirects is False
        assert client.timeout.connect == 10.0
        assert client.timeout.read == 10.0
        assert client.timeout.write == 10.0
        assert client.timeout.pool == 10.0
        assert client.trust_env is False


# ============================================================
# CONTENT LENGTH VALIDATION
# ============================================================

@pytest.mark.parametrize(
    "content_length",
    [
        "-1",
        "invalid",
        "5.5",
        "",
        "999999999999",
    ],
)
def test_media_content_length_rejects_invalid_values(
    content_length,
):
    with pytest.raises(ValueError):
        validate_media_content_length(content_length)


def test_media_content_length_accepts_valid_size():
    validate_media_content_length("1024")


def test_media_content_length_accepts_maximum_size():
    validate_media_content_length(
        str(settings.MEDIA_MAX_IMAGE_BYTES)
    )


def test_media_content_length_accepts_missing_header():
    assert validate_media_content_length(None) is None


# ============================================================
# MEDIA CHUNK VALIDATION
# ============================================================

def test_media_chunks_accept_valid_data():
    chunks = [
        b"hello",
        b"world",
    ]

    result = read_limited_media_chunks(chunks)

    assert result == b"helloworld"


def test_media_chunks_accept_maximum_size():
    chunks = [
        b"a" * settings.MEDIA_MAX_IMAGE_BYTES
    ]

    result = read_limited_media_chunks(chunks)

    assert len(result) == settings.MEDIA_MAX_IMAGE_BYTES


def test_media_chunks_reject_oversized_data():
    chunks = [
        b"a" * settings.MEDIA_MAX_IMAGE_BYTES,
        b"b",
    ]

    with pytest.raises(
        ValueError,
        match="Media exceeds the maximum allowed size.",
    ):
        read_limited_media_chunks(chunks)


def test_media_chunks_reject_invalid_data():
    with pytest.raises(
        ValueError,
        match="Invalid media data chunk.",
    ):
        read_limited_media_chunks([b"valid", "invalid"])


# ============================================================
# PINNED NETWORK BACKEND: IP VALIDATION
# ============================================================

def test_pinned_media_backend_rejects_private_ip():
    with pytest.raises(
        ValueError,
        match="Non-public IP address is not allowed.",
    ):
        PinnedMediaNetworkBackend(
            allowed_ips={"127.0.0.1"}
        )


def test_pinned_media_backend_rejects_empty_ip_list():
    with pytest.raises(
        ValueError,
        match="At least one authorized IP address is required.",
    ):
        PinnedMediaNetworkBackend(
            allowed_ips=set()
        )


@pytest.mark.parametrize(
    "invalid_ip",
    [
        "not-an-ip",
        "999.999.999.999",
        "192.168.1",
        "",
    ],
)
def test_pinned_media_backend_rejects_invalid_ip(invalid_ip):
    with pytest.raises(
        ValueError,
        match="Invalid IP address.",
    ):
        PinnedMediaNetworkBackend(
            allowed_ips={invalid_ip}
        )


def test_pinned_media_backend_accepts_public_ip():
    backend = PinnedMediaNetworkBackend(
        allowed_ips={"8.8.8.8"}
    )

    assert backend.allowed_ips == frozenset({"8.8.8.8"})


# ============================================================
# PINNED NETWORK BACKEND: AUTHORIZED IP CONNECTION
# ============================================================

def test_pinned_media_backend_uses_authorized_ip(monkeypatch):
    import httpcore

    connections = []
    fake_stream = object()

    def fake_connect_tcp(
        self,
        host,
        port,
        timeout=None,
        local_address=None,
        socket_options=None,
    ):
        connections.append((host, port))
        return fake_stream

    monkeypatch.setattr(
        httpcore.SyncBackend,
        "connect_tcp",
        fake_connect_tcp,
    )

    backend = PinnedMediaNetworkBackend(
        allowed_ips={"8.8.8.8"},
        authorized_host="example.com",
    )

    result = backend.connect_tcp(
        host="example.com",
        port=443,
    )

    assert result is fake_stream
    assert connections == [("8.8.8.8", 443)]


@pytest.mark.parametrize(
    "private_ip",
    [
        "::1",
        "fc00::1",
        "fe80::1",
        "::ffff:127.0.0.1",
    ],
)
def test_pinned_media_backend_rejects_non_public_ipv6(private_ip):
    with pytest.raises(
        ValueError,
        match="Non-public IP address is not allowed.",
    ):
        PinnedMediaNetworkBackend(
            allowed_ips={private_ip}
        )


# ============================================================
# PINNED NETWORK BACKEND: PORT SECURITY
# ============================================================

@pytest.mark.parametrize(
    "port",
    [
        80,
        22,
        8080,
        8000,
    ],
)
def test_pinned_media_backend_rejects_unauthorized_ports(port):
    backend = PinnedMediaNetworkBackend(
        allowed_ips={"8.8.8.8"},
        authorized_host="example.com",
    )

    with pytest.raises(
        ValueError,
        match="Only HTTPS port 443 is allowed.",
    ):
        backend.connect_tcp(
            host="example.com",
            port=port,
        )


def test_pinned_backend_rejects_port_without_network(monkeypatch):
    import socket

    def forbidden_connection(*args, **kwargs):
        raise AssertionError(
            "A network connection must not be attempted."
        )

    monkeypatch.setattr(
        socket,
        "create_connection",
        forbidden_connection,
    )

    backend = PinnedMediaNetworkBackend(
        allowed_ips={"8.8.8.8"},
    )

    with pytest.raises(
        ValueError,
        match="Only HTTPS port 443 is allowed.",
    ):
        backend.connect_tcp(
            host="example.com",
            port=80,
        )


# ============================================================
# PINNED NETWORK BACKEND: CONNECTION SECURITY
# ============================================================

def test_pinned_backend_connects_only_to_authorized_ip(monkeypatch):
    import httpcore

    connections = []
    fake_stream = object()

    def fake_connect_tcp(
        self,
        host,
        port,
        timeout=None,
        local_address=None,
        socket_options=None,
    ):
        connections.append((host, port))
        return fake_stream

    monkeypatch.setattr(
        httpcore.SyncBackend,
        "connect_tcp",
        fake_connect_tcp,
    )

    backend = PinnedMediaNetworkBackend(
        allowed_ips={"8.8.8.8"},
        authorized_host="images.example.com",
    )

    result = backend.connect_tcp(
        host="images.example.com",
        port=443,
    )

    assert result is fake_stream
    assert connections == [("8.8.8.8", 443)]


def test_pinned_backend_https_uses_only_authorized_ip(monkeypatch):
    import httpcore

    connections = []
    fake_stream = object()

    def fake_connect_tcp(
        self,
        host,
        port,
        timeout=None,
        local_address=None,
        socket_options=None,
    ):
        connections.append((host, port))
        return fake_stream

    monkeypatch.setattr(
        httpcore.SyncBackend,
        "connect_tcp",
        fake_connect_tcp,
    )

    backend = PinnedMediaNetworkBackend(
        allowed_ips={"8.8.8.8"},
        authorized_host="example.com",
    )

    result = backend.connect_tcp(
        host="example.com",
        port=443,
    )

    assert result is fake_stream
    assert connections == [("8.8.8.8", 443)]


def test_pinned_backend_does_not_connect_to_unverified_host(
    monkeypatch,
):
    import socket

    def forbidden_connection(*args, **kwargs):
        raise AssertionError(
            "A network connection must not be attempted."
        )

    monkeypatch.setattr(
        socket,
        "create_connection",
        forbidden_connection,
    )

    backend = PinnedMediaNetworkBackend(
        allowed_ips={"8.8.8.8"},
        authorized_host="media.example.com",
    )

    with pytest.raises(
        ValueError,
        match="Media host does not match authorized host.",
    ):
        backend.connect_tcp(
            host="unverified.example",
            port=443,
        )


# ============================================================
# PINNED NETWORK BACKEND: AUTHORIZED HOST
# ============================================================

def test_pinned_backend_starts_without_authorized_host():
    backend = PinnedMediaNetworkBackend(
        allowed_ips={"8.8.8.8"}
    )

    assert backend.authorized_host is None


def test_pinned_backend_rejects_different_host():
    backend = PinnedMediaNetworkBackend(
        allowed_ips={"8.8.8.8"},
        authorized_host="media.example.com",
    )

    with pytest.raises(
        ValueError,
        match="Media host does not match authorized host.",
    ):
        backend.connect_tcp(
            host="other.example.com",
            port=443,
        )


def test_pinned_backend_rejects_missing_authorized_host():
    backend = PinnedMediaNetworkBackend(
        allowed_ips={"8.8.8.8"}
    )

    with pytest.raises(
        ValueError,
        match="No authorized media host configured.",
    ):
        backend.connect_tcp(
            host="example.com",
            port=443,
        )


@pytest.mark.parametrize(
    "invalid_host",
    [
        "",
        "EXAMPLE.COM",
        "example.com:443",
        "https://example.com",
        "example.com/path",
        "-example.com",
        "example..com",
        "example.com.",
        "example_com",
    ],
)
def test_pinned_backend_rejects_invalid_authorized_host(
    invalid_host,
):
    with pytest.raises(
        ValueError,
        match="Invalid authorized media host.",
    ):
        PinnedMediaNetworkBackend(
            allowed_ips={"8.8.8.8"},
            authorized_host=invalid_host,
        )


def test_pinned_backend_accepts_valid_authorized_host():
    backend = PinnedMediaNetworkBackend(
        allowed_ips={"8.8.8.8"},
        authorized_host="images.example.com",
    )

    assert backend.authorized_host == "images.example.com"
    assert backend.allowed_ips == frozenset({"8.8.8.8"})


def test_pinned_backend_authorized_host_cannot_be_changed():
    backend = PinnedMediaNetworkBackend(
        allowed_ips={"8.8.8.8"},
        authorized_host="images.example.com",
    )

    with pytest.raises(AttributeError):
        backend.authorized_host = "evil.example.com"

    assert backend.authorized_host == "images.example.com"