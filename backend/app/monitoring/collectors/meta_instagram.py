from app.core.settings import (
    META_INSTAGRAM_ENABLED,
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
from app.core.settings import (
    META_INSTAGRAM_ENABLED,
    META_INSTAGRAM_USER_ID,
)
from app.monitoring.signal_extractor import (
    extract_signals,
)

class MetaInstagramCollector(BaseCollector):
    platform = "Instagram"
    channel = "meta_instagram_collector"
    
    def __init__(
        self,
        client: MetaClient | None = None,
    ):
        self.client = client or MetaClient()
    def _fetch_items(
    self,
  ) -> list[dict]:

     if not META_INSTAGRAM_USER_ID:
        return []

     return self.client.get_instagram_media(
        instagram_user_id=(
            META_INSTAGRAM_USER_ID
        )
    )

    def collect(
        self,
    ) -> list[MonitoringCandidate]:

        if not META_INSTAGRAM_ENABLED:
            return []

        if not self.client.is_configured():
            return []

        items = self._fetch_items()

        return [
            self._to_candidate(item)
            for item in items
        ]
    def _to_candidate(
    self,
        item: dict,
    ) -> MonitoringCandidate:

        description = (
            item.get("caption")
            or ""
        )

        signals = extract_signals(
            description
        )

        return MonitoringCandidate(
            platform=self.platform,

            url=(
                item.get("permalink")
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
        )