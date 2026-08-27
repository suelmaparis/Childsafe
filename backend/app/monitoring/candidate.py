from dataclasses import dataclass, field


@dataclass
class MonitoringCandidate:
    platform: str
    url: str
    description: str

    reason: str = "potential_child_exposure"

    source_channel: str = "unknown_collector"
    source_reference: str | None = None

    contains_child: bool | None = None
    location_detected: bool | None = None
    volunteer_context: bool | None = None
    tourism_context: bool | None = None

    metadata: dict = field(
        default_factory=dict
    )
    signal_score: int = 0
    signal_confidence: float = 0.0