from app.monitoring.candidate import (
    MonitoringCandidate,
)


def collect_candidates() -> list[MonitoringCandidate]:
    """
    Development collector.

    Simulates public social-media content discovered
    by the ChildSafe monitoring system.
    """

    return [
        MonitoringCandidate(
            platform="Instagram",
            url=(
                "https://example.com/"
                "automated-monitoring-test-001"
            ),
            description=(
                "Public post appears to show a child "
                "and reveals information about a "
                "regular location."
            ),
            reason="potential_child_exposure",
            source_channel="mock_instagram_collector",
            source_reference="mock-post-001",
        ),
    ]