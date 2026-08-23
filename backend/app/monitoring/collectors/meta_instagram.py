from app.core.settings import (
    META_INSTAGRAM_ENABLED,
    META_ACCESS_TOKEN,
)

from app.monitoring.candidate import (
    MonitoringCandidate,
)

from app.monitoring.collectors.base import (
    BaseCollector,
)


class MetaInstagramCollector(BaseCollector):
    platform = "Instagram"
    channel = "meta_instagram_collector"

    def collect(
        self,
    ) -> list[MonitoringCandidate]:

        if not META_INSTAGRAM_ENABLED:
            return []

        if not META_ACCESS_TOKEN:
            return []

        # API integration will be added here later.
        #
        # For now this collector is intentionally empty
        # until Meta credentials and permissions are ready.

        return []