from app.core.settings import (
    MOCK_INSTAGRAM_ENABLED,
    META_INSTAGRAM_ENABLED,
    META_FACEBOOK_ENABLED,
)

from app.monitoring.collectors.mock import (
    MockInstagramCollector,
)

from app.monitoring.collectors.meta_instagram import (
    MetaInstagramCollector,
)

from app.monitoring.collectors.meta_facebook import (
    MetaFacebookCollector,
)


def get_enabled_collectors():
    collectors = []

    if MOCK_INSTAGRAM_ENABLED:
        collectors.append(
            MockInstagramCollector()
        )

    if META_INSTAGRAM_ENABLED:
        collectors.append(
            MetaInstagramCollector()
        )

    if META_FACEBOOK_ENABLED:
        collectors.append(
            MetaFacebookCollector()
        )

    return collectors