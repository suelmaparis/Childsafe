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
        return MonitoringCandidate(
            platform=self.platform,

            url=(
                item.get("permalink")
                or item.get("url")
                or ""
            ),

            description=(
                item.get("caption")
                or ""
            ),

            reason=(
                "potential_child_exposure"
            ),

            source_channel=self.channel,

            source_reference=str(
                item.get("id")
                or ""
            ),

            contains_child=bool(
                item.get(
                    "contains_child",
                    False,
                )
            ),

            location_detected=bool(
                item.get(
                    "location_detected",
                    False,
                )
            ),

            volunteer_context=bool(
                item.get(
                    "volunteer_context",
                    False,
                )
            ),

            tourism_context=bool(
                item.get(
                    "tourism_context",
                    False,
                )
            ),
        )