from app.monitoring.candidate import (
    MonitoringCandidate,
)

from app.monitoring.collectors.base import (
    BaseCollector,
)


class MockInstagramCollector(BaseCollector):
    platform = "Instagram"
    channel = "mock_instagram_collector"

    def collect(
        self,
    ) -> list[MonitoringCandidate]:

        return [
            MonitoringCandidate(
                platform=self.platform,

                url=(
                    "https://example.com/"
                    "structured-test-002"
                ),

                description=(
                    "Public volunteer post."
                ),

                reason=(
                    "potential_child_exposure"
                ),

                source_channel=self.channel,

                source_reference=(
                    "structured-002"
                ),

                contains_child=True,
                location_detected=True,
                volunteer_context=True,
                tourism_context=False,
            ),
        ]