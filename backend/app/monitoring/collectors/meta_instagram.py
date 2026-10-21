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
    extract_school_signals,
)

class MetaInstagramCollector(BaseCollector):
    platform = "Instagram"
    channel = "meta_instagram_collector"
    
    def __init__(
        self,
        client: MetaClient | None = None,
        hashtags: list[str] | None = None,
    ):
        self.client = client or MetaClient()
        self.hashtags = [
            tag.strip().lstrip("#")
            for tag in (hashtags or [])
            if tag.strip().lstrip("#")
        ]

    def _fetch_items(self) -> list[dict]:
        if not META_INSTAGRAM_USER_ID:
            return []

        items = self.client.get_instagram_media(
            instagram_user_id=META_INSTAGRAM_USER_ID
        )

        seen_ids = {
            str(item["id"])
            for item in items
            if item.get("id")
        }

        for hashtag in self.hashtags:
            hashtag_items = self.client.search_instagram_hashtag(
                instagram_user_id=META_INSTAGRAM_USER_ID,
                hashtag=hashtag,
            )

            for item in hashtag_items:
                item_id = str(item.get("id") or "")

                if item_id and item_id in seen_ids:
                    continue

                items.append(item)

                if item_id:
                    seen_ids.add(item_id)

        return items

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

        school_signals = extract_school_signals(
            description
        )


        return MonitoringCandidate(
            metadata={
                "school_signals": school_signals,
            },
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
            signal_score=signals[
                "signal_score"
            ],

            signal_confidence=signals[
                "signal_confidence"
            ],
        )