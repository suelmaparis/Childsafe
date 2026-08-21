from dataclasses import dataclass

from app.monitoring.candidate import (
    MonitoringCandidate,
)


@dataclass
class DetectionResult:
    relevant: bool
    reason: str | None
    confidence: float
    signals: list[str]


CHILD_TERMS = {
    "child",
    "children",
    "kid",
    "kids",
    "minor",
    "boy",
    "girl",
    "student",
    "schoolchild",
}

LOCATION_TERMS = {
    "school",
    "home",
    "address",
    "location",
    "village",
    "neighborhood",
    "neighbourhood",
    "street",
    "routine",
    "every day",
    "everyday",
}

VOLUNTEER_TERMS = {
    "volunteer",
    "volunteering",
    "mission",
    "orphanage",
    "community visit",
}

TOURISM_TERMS = {
    "tourist",
    "tourism",
    "vacation",
    "holiday",
    "trip",
    "travel",
}


def detect_candidate(
    candidate: MonitoringCandidate,
) -> DetectionResult:

    text = candidate.description.lower().strip()

    signals = []

    # --------------------------------------------------
    # Structured signals
    # --------------------------------------------------

    if candidate.contains_child is True:
        signals.append(
            "child_detected"
        )

    if candidate.location_detected is True:
        signals.append(
            "location_detected"
        )

    if candidate.volunteer_context is True:
        signals.append(
            "volunteer_context"
        )

    if candidate.tourism_context is True:
        signals.append(
            "tourism_context"
        )

    # --------------------------------------------------
    # Text fallback signals
    # --------------------------------------------------

    if (
        candidate.contains_child is None
        and any(
            term in text
            for term in CHILD_TERMS
        )
    ):
        signals.append(
            "child_reference"
        )

    if (
        candidate.location_detected is None
        and any(
            term in text
            for term in LOCATION_TERMS
        )
    ):
        signals.append(
            "location_reference"
        )

    if (
        candidate.volunteer_context is None
        and any(
            term in text
            for term in VOLUNTEER_TERMS
        )
    ):
        signals.append(
            "volunteer_context"
        )

    if (
        candidate.tourism_context is None
        and any(
            term in text
            for term in TOURISM_TERMS
        )
    ):
        signals.append(
            "tourism_context"
        )

    # --------------------------------------------------
    # Scoring
    # --------------------------------------------------

    score = 0.0

    if (
        "child_detected" in signals
        or "child_reference" in signals
    ):
        score += 0.50

    if (
        "location_detected" in signals
        or "location_reference" in signals
    ):
        score += 0.25

    if "volunteer_context" in signals:
        score += 0.15

    if "tourism_context" in signals:
        score += 0.10

    confidence = min(
        round(score, 2),
        1.0,
    )

    has_child_signal = (
        "child_detected" in signals
        or "child_reference" in signals
    )

    relevant = (
        has_child_signal
        and confidence >= 0.50
    )

    reason = (
        "potential_child_exposure"
        if relevant
        else None
    )

    return DetectionResult(
        relevant=relevant,
        reason=reason,
        confidence=confidence,
        signals=signals,
    )