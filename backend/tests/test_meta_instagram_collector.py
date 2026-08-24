from app.monitoring.collectors.meta_instagram import (
    MetaInstagramCollector,
)


def test_meta_item_to_candidate():
    collector = MetaInstagramCollector()

    item = {
        "id": "meta-test-001",
        "permalink": (
            "https://www.instagram.com/"
            "p/test001/"
        ),
        "caption": (
            "Volunteer visit with local children."
        ),
        "contains_child": True,
        "location_detected": True,
        "volunteer_context": True,
        "tourism_context": False,
    }

    candidate = collector._to_candidate(item)

    assert candidate.platform == "Instagram"
    assert (
        candidate.source_reference
        == "meta-test-001"
    )
    assert candidate.contains_child is True
    assert candidate.location_detected is True
    assert candidate.volunteer_context is True
    assert candidate.tourism_context is False
def test_collect_returns_empty_when_disabled(
    monkeypatch,
):
    from app.monitoring.collectors import (
        meta_instagram,
    )

    monkeypatch.setattr(
        meta_instagram,
        "META_INSTAGRAM_ENABLED",
        False,
    )

    collector = (
        meta_instagram.MetaInstagramCollector()
    )

    assert collector.collect() == []


def test_collect_returns_empty_without_token(
    monkeypatch,
):
    from app.monitoring.collectors import (
        meta_instagram,
    )

    monkeypatch.setattr(
        meta_instagram,
        "META_INSTAGRAM_ENABLED",
        True,
    )

    class FakeClient:
        def is_configured(self):
            return False

    collector = (
        meta_instagram.MetaInstagramCollector(
            client=FakeClient(),
        )
    )

    assert collector.collect() == []
def test_collect_converts_items_from_client(
    monkeypatch,
):
    from app.monitoring.collectors import (
        meta_instagram,
    )

    monkeypatch.setattr(
        meta_instagram,
        "META_INSTAGRAM_ENABLED",
        True,
    )

    class FakeClient:
        def is_configured(self):
            return True

    collector = (
        meta_instagram.MetaInstagramCollector(
            client=FakeClient(),
        )
    )

    collector._fetch_items = lambda: [
        {
            "id": "meta-test-010",
            "permalink": (
                "https://www.instagram.com/"
                "p/test010/"
            ),
            "caption": (
                "Volunteer activity "
                "with local children."
            ),
            "contains_child": True,
            "location_detected": True,
            "volunteer_context": True,
            "tourism_context": False,
        }
    ]

    candidates = collector.collect()

    assert len(candidates) == 1

    candidate = candidates[0]

    assert (
        candidate.source_reference
        == "meta-test-010"
    )

    assert candidate.contains_child is True
    assert candidate.volunteer_context is True
def test_fetch_items_uses_meta_client(
    monkeypatch,
):
    from app.monitoring.collectors import (
        meta_instagram,
    )

    monkeypatch.setattr(
        meta_instagram,
        "META_INSTAGRAM_USER_ID",
        "17890000000000000",
    )

    class FakeClient:
        def is_configured(self):
            return True

        def get_instagram_media(
            self,
            instagram_user_id,
            limit=25,
        ):
            assert (
                instagram_user_id
                == "17890000000000000"
            )

            return [
                {
                    "id": "meta-test-020",
                    "permalink": (
                        "https://www.instagram.com/"
                        "p/test020/"
                    ),
                    "caption": "Test post",
                }
            ]

    collector = (
        meta_instagram.MetaInstagramCollector(
            client=FakeClient(),
        )
    )

    items = collector._fetch_items()

    assert len(items) == 1
    assert items[0]["id"] == "meta-test-020"
def test_fetch_items_returns_empty_without_user_id(
    monkeypatch,
):
    from app.monitoring.collectors import (
        meta_instagram,
    )

    monkeypatch.setattr(
        meta_instagram,
        "META_INSTAGRAM_USER_ID",
        "",
    )

    class FakeClient:
        def is_configured(self):
            return True

    collector = (
        meta_instagram.MetaInstagramCollector(
            client=FakeClient(),
        )
    )

    assert collector._fetch_items() == []

def test_collect_full_flow_with_fake_client(
    monkeypatch,
):
    from app.monitoring.collectors import (
        meta_instagram,
    )

    monkeypatch.setattr(
        meta_instagram,
        "META_INSTAGRAM_ENABLED",
        True,
    )

    monkeypatch.setattr(
        meta_instagram,
        "META_INSTAGRAM_USER_ID",
        "17890000000000000",
    )

    class FakeClient:
        def is_configured(self):
            return True

        def get_instagram_media(
            self,
            instagram_user_id,
            limit=25,
        ):
            assert (
                instagram_user_id
                == "17890000000000000"
            )

            return [
                {
                    "id": "meta-flow-001",
                    "permalink": (
                        "https://www.instagram.com/"
                        "p/flow001/"
                    ),
                    "caption": (
                        "Volunteer visit "
                        "with local children."
                    ),
                    "contains_child": True,
                    "location_detected": True,
                    "volunteer_context": True,
                    "tourism_context": False,
                },
                {
                    "id": "meta-flow-002",
                    "permalink": (
                        "https://www.instagram.com/"
                        "p/flow002/"
                    ),
                    "caption": (
                        "Tourist activity "
                        "in a local community."
                    ),
                    "contains_child": True,
                    "location_detected": True,
                    "volunteer_context": False,
                    "tourism_context": True,
                },
            ]

    collector = (
        meta_instagram.MetaInstagramCollector(
            client=FakeClient(),
        )
    )

    candidates = collector.collect()

    assert len(candidates) == 2

    first = candidates[0]
    second = candidates[1]

    assert (
        first.source_reference
        == "meta-flow-001"
    )

    assert first.platform == "Instagram"
    assert first.contains_child is True
    assert first.location_detected is True
    assert first.volunteer_context is True
    assert first.tourism_context is False

    assert (
        second.source_reference
        == "meta-flow-002"
    )

    assert second.platform == "Instagram"
    assert second.contains_child is True
    assert second.location_detected is True
    assert second.volunteer_context is False
    assert second.tourism_context is True