from app.monitoring.collectors.meta_facebook import (
    MetaFacebookCollector,
)


def test_facebook_item_to_candidate():
    collector = MetaFacebookCollector()

    item = {
        "id": "facebook-test-001",
        "permalink_url": (
            "https://www.facebook.com/"
            "example/posts/001"
        ),
        "message": (
            "Volunteer activity with local children "
            "in Praia, Cabo Verde."
        ),
    }

    candidate = collector._to_candidate(
        item
    )

    assert candidate.platform == "Facebook"

    assert (
        candidate.source_reference
        == "facebook-test-001"
    )

    assert candidate.contains_child is True
    assert candidate.location_detected is True
    assert candidate.volunteer_context is True
    assert candidate.tourism_context is False
    assert candidate.signal_score == 3
    assert candidate.signal_confidence == 0.8



def test_collect_returns_empty_when_disabled(
    monkeypatch,
):
    from app.monitoring.collectors import (
        meta_facebook,
    )

    monkeypatch.setattr(
        meta_facebook,
        "META_FACEBOOK_ENABLED",
        False,
    )

    collector = (
        meta_facebook.MetaFacebookCollector()
    )

    assert collector.collect() == []


def test_collect_returns_empty_without_token(
    monkeypatch,
):
    from app.monitoring.collectors import (
        meta_facebook,
    )

    monkeypatch.setattr(
        meta_facebook,
        "META_FACEBOOK_ENABLED",
        True,
    )

    class FakeClient:
        def is_configured(self):
            return False

    collector = (
        meta_facebook.MetaFacebookCollector(
            client=FakeClient(),
        )
    )

    assert collector.collect() == []


def test_collect_full_flow_with_fake_client(
    monkeypatch,
):
    from app.monitoring.collectors import (
        meta_facebook,
    )

    monkeypatch.setattr(
        meta_facebook,
        "META_FACEBOOK_ENABLED",
        True,
    )

    class FakeClient:
        def is_configured(self):
            return True

    collector = (
        meta_facebook.MetaFacebookCollector(
            client=FakeClient(),
        )
    )

    collector._fetch_items = lambda: [
        {
            "id": "facebook-flow-001",
            "permalink_url": (
                "https://www.facebook.com/"
                "example/posts/001"
            ),
            "message": (
                "Volunteer activity with local children "
                "in Praia, Cabo Verde."
            ),
        },
        {
            "id": "facebook-flow-002",
            "permalink_url": (
                "https://www.facebook.com/"
                "example/posts/002"
            ),
            "message": (
                "Tourist trip with local children "
                "in Sal, Cabo Verde."
            ),
        },
    ]

    candidates = collector.collect()

    assert len(candidates) == 2

    first = candidates[0]
    second = candidates[1]

    assert (
        first.source_reference
        == "facebook-flow-001"
    )

    assert first.platform == "Facebook"
    assert first.contains_child is True
    assert first.location_detected is True
    assert first.volunteer_context is True
    assert first.tourism_context is False

    assert (
        second.source_reference
        == "facebook-flow-002"
    )

    assert second.platform == "Facebook"
    assert second.contains_child is True
    assert second.location_detected is True
    assert second.volunteer_context is False
    assert second.tourism_context is True


def test_fetch_items_uses_meta_client(
    monkeypatch,
):
    from app.monitoring.collectors import (
        meta_facebook,
    )

    monkeypatch.setattr(
        meta_facebook,
        "META_FACEBOOK_PAGE_ID",
        "123456789",
    )

    class FakeClient:
        def is_configured(self):
            return True

        def get_facebook_posts(
            self,
            page_id,
            limit=25,
        ):
            assert page_id == "123456789"

            return [
                {
                    "id": "facebook-test-020",
                    "message": "Test post",
                    "permalink_url": (
                        "https://www.facebook.com/"
                        "example/posts/020"
                    ),
                }
            ]

    collector = (
        meta_facebook.MetaFacebookCollector(
            client=FakeClient(),
        )
    )

    items = collector._fetch_items()

    assert len(items) == 1

    assert (
        items[0]["id"]
        == "facebook-test-020"
    )


def test_fetch_items_returns_empty_without_page_id(
    monkeypatch,
):
    from app.monitoring.collectors import (
        meta_facebook,
    )

    monkeypatch.setattr(
        meta_facebook,
        "META_FACEBOOK_PAGE_ID",
        "",
    )

    class FakeClient:
        def is_configured(self):
            return True

    collector = (
        meta_facebook.MetaFacebookCollector(
            client=FakeClient(),
        )
    )

    assert collector._fetch_items() == []
  