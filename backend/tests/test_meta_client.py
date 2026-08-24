from app.integrations.meta.client import (
    MetaClient,
)


def test_get_instagram_media_uses_expected_endpoint(
    monkeypatch,
):
    client = MetaClient(
        access_token="test-token",
    )

    captured = {}

    def fake_get(
        path,
        params=None,
    ):
        captured["path"] = path
        captured["params"] = params

        return {
            "data": [
                {
                    "id": "media-001",
                    "caption": "Test post",
                }
            ]
        }

    monkeypatch.setattr(
        client,
        "get",
        fake_get,
    )

    items = client.get_instagram_media(
        instagram_user_id=(
            "17890000000000000"
        ),
        limit=10,
    )

    assert (
        captured["path"]
        == "17890000000000000/media"
    )

    assert captured["params"]["limit"] == 10

    assert "id" in captured["params"]["fields"]
    assert "caption" in captured["params"]["fields"]
    assert "permalink" in captured["params"]["fields"]

    assert len(items) == 1
    assert items[0]["id"] == "media-001"
def test_get_instagram_media_returns_empty_without_data(
    monkeypatch,
):
    client = MetaClient(
        access_token="test-token",
    )

    monkeypatch.setattr(
        client,
        "get",
        lambda path, params=None: {},
    )

    items = client.get_instagram_media(
        instagram_user_id=(
            "17890000000000000"
        )
    )

    assert items == []
def test_get_all_pages_collects_multiple_pages(
    monkeypatch,
):
    client = MetaClient(
        access_token="test-token",
    )

    first_page = {
        "data": [
            {
                "id": "media-001",
            }
        ],
        "paging": {
            "next": (
                "https://example.com/page-2"
            )
        },
    }

    second_page = {
        "data": [
            {
                "id": "media-002",
            }
        ]
    }

    monkeypatch.setattr(
        client,
        "get",
        lambda path, params=None: first_page,
    )

    monkeypatch.setattr(
        client,
        "get_url",
        lambda url: second_page,
    )

    items = client.get_all_pages(
        "test/media"
    )

    assert len(items) == 2
    assert items[0]["id"] == "media-001"
    assert items[1]["id"] == "media-002"
def test_get_all_pages_stops_without_next(
    monkeypatch,
):
    client = MetaClient(
        access_token="test-token",
    )

    monkeypatch.setattr(
        client,
        "get",
        lambda path, params=None: {
            "data": [
                {
                    "id": "media-001",
                }
            ]
        },
    )

    items = client.get_all_pages(
        "test/media"
    )

    assert len(items) == 1
    assert items[0]["id"] == "media-001"