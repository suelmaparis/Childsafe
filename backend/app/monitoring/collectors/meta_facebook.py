from app.core.settings import (
    META_FACEBOOK_ENABLED,
    META_FACEBOOK_PAGE_ID,
)

from app.integrations.meta.client import (
    MetaClient,
)

from app.monitoring.candidate import (
    MonitoringCandidate,
)

from app.monitoring.collectors.base import (
    BaseCollector,
)

from app.monitoring.signal_extractor import (
    extract_signals,
)


class MetaFacebookCollector(BaseCollector):
    platform = "Facebook"
    channel = "meta_facebook_collector"

    def __init__(
        self,
        client: MetaClient | None = None,
    ):
        self.client = client or MetaClient()

    def collect(
        self,
    ) -> list[MonitoringCandidate]:

        if not META_FACEBOOK_ENABLED:
            return []

        if not self.client.is_configured():
            return []

        items = self._fetch_items()

        return [
            self._to_candidate(item)
            for item in items
        ]

    def _fetch_items(
        self,
    ) -> list[dict]:

        if not META_FACEBOOK_PAGE_ID:
            return []

        return self.client.get_facebook_posts(
            page_id=META_FACEBOOK_PAGE_ID
        )

    def _to_candidate(
        self,
        item: dict,
    ) -> MonitoringCandidate:

        description = (
            item.get("message")
            or item.get("description")
            or ""
        )

        signals = extract_signals(
            description
        )

        return MonitoringCandidate(
            platform=self.platform,

            url=(
                item.get("permalink_url")
                or item.get("url")
                or ""
            ),

            description=description,

            reason=(
                "potential_child_exposure"
            ),

            source_channel=self.channel,

            source_reference=str(
                item.get("id")
                or ""
            ),

            contains_child=signals[
                "contains_child"
            ],

            location_detected=signals[
                "location_detected"
            ],

            volunteer_context=signals[
                "volunteer_context"
            ],

            tourism_context=signals[
                "tourism_context"
            ],
            signal_score=signals[
                "signal_score"
            ],

            signal_confidence=signals[
                "signal_confidence"
            ],
        )