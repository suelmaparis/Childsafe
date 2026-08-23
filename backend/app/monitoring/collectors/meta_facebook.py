from app.core.settings import (
    META_FACEBOOK_ENABLED,
    META_ACCESS_TOKEN,
)

from app.monitoring.candidate import (
    MonitoringCandidate,
)

from app.monitoring.collectors.base import (
    BaseCollector,
)


class MetaFacebookCollector(BaseCollector):
    platform = "Facebook"
    channel = "meta_facebook_collector"

    def collect(
        self,
    ) -> list[MonitoringCandidate]:

        if not META_FACEBOOK_ENABLED:
            return []

        if not META_ACCESS_TOKEN:
            return []

        # Meta API integration will be added later.

        return []