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

def test_get_facebook_posts_uses_expected_endpoint(
    monkeypatch,
):
    client = MetaClient(
        access_token="test-token",
    )

    captured = {}

    def fake_get_all_pages(
        path,
        params=None,
        max_pages=10,
    ):
        captured["path"] = path
        captured["params"] = params

        return [
            {
                "id": "facebook-post-001",
                "message": "Test post",
            }
        ]

    monkeypatch.setattr(
        client,
        "get_all_pages",
        fake_get_all_pages,
    )

    posts = client.get_facebook_posts(
        page_id="123456789",
        limit=10,
    )

    assert (
        captured["path"]
        == "123456789/posts"
    )

    assert captured["params"]["limit"] == 10

    assert "id" in captured["params"]["fields"]
    assert "message" in captured["params"]["fields"]
    assert "permalink_url" in (
        captured["params"]["fields"]
    )

    assert len(posts) == 1
    assert (
        posts[0]["id"]
        == "facebook-post-001"
    )

def test_search_instagram_hashtag(monkeypatch):
    client = MetaClient(access_token="test-token")
    captured = {}

    def fake_get(path, params=None):
        captured["search_path"] = path
        captured["search_params"] = params
        return {
            "data": [{"id": "hashtag-test-001"}]
        }

    def fake_get_all_pages(path, params=None, max_pages=10):
        captured["media_path"] = path
        captured["media_params"] = params
        captured["max_pages"] = max_pages
        return [
            {
                "id": "post-test-001",
                "caption": "Cabo Verde",
                "permalink": "https://www.instagram.com/p/test001/",
            }
        ]

    monkeypatch.setattr(client, "get", fake_get)
    monkeypatch.setattr(client, "get_all_pages", fake_get_all_pages)

    posts = client.search_instagram_hashtag(
        instagram_user_id="17841478120220644",
        hashtag="#CaboVerde",
    )

    assert captured["search_path"] == "ig_hashtag_search"
    assert captured["search_params"]["q"] == "CaboVerde"
    assert captured["media_path"] == "hashtag-test-001/recent_media"
    assert captured["media_params"]["user_id"] == "17841478120220644"
    assert captured["max_pages"] == 1
    assert len(posts) == 1
    assert posts[0]["id"] == "post-test-001"


def test_meta_pagination_stops_at_page_limit_regression():
    from unittest.mock import patch
    from app.integrations.meta.client import MetaClient

    client = MetaClient(access_token="fake-test-token")

    first_page = {
        "data": [{"id": "123"}],
        "paging": {
            "next": "https://example.com/second-page"
        },
    }

    with patch.object(client, "get", return_value=first_page):
        with patch.object(client, "get_url") as next_page:
            result = client.get_all_pages(
                "test-media",
                max_pages=1,
            )

    assert result == [{"id": "123"}]
    next_page.assert_not_called()


def test_meta_timeout_is_handled_regression():
    from unittest.mock import patch
    import pytest

    from app.integrations.meta.client import (
        MetaClient,
        MetaApiError,
    )

    client = MetaClient(access_token="fake-test-token")

    with patch(
        "app.integrations.meta.client.urllib.request.urlopen",
        side_effect=TimeoutError("The read operation timed out"),
    ):
        with pytest.raises(MetaApiError, match="timed out"):
            client.get_url("https://example.com/test")
