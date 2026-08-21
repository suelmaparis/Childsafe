from dataclasses import dataclass


@dataclass
class MonitoringCandidate:
    platform: str
    url: str
    description: str

    reason: str = "potential_child_exposure"

    source_channel: str = "unknown_collector"
    source_reference: str | None = None