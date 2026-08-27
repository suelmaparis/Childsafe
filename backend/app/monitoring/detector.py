from app.monitoring.candidate import (
    MonitoringCandidate,
)


def detect_candidate(
    candidate: MonitoringCandidate,
) -> dict:
    signals = []

    if candidate.contains_child:
        signals.append(
            "child_detected"
        )

    if candidate.location_detected:
        signals.append(
            "location_detected"
        )

    if candidate.volunteer_context:
        signals.append(
            "volunteer_context"
        )

    if candidate.tourism_context:
        signals.append(
            "tourism_context"
        )

    derived_signal_score = len(
        signals
    )

    candidate_signal_score = getattr(
        candidate,
        "signal_score",
        0,
    )

    candidate_signal_confidence = getattr(
        candidate,
        "signal_confidence",
        0.0,
    )

    # Older/mock candidates may have the default
    # score/confidence even though boolean signals
    # are already present.
    if (
        derived_signal_score > 0
        and candidate_signal_score == 0
    ):
        signal_score = (
            derived_signal_score
        )
    else:
        signal_score = (
            candidate_signal_score
        )

    confidence_map = {
        0: 0.0,
        1: 0.25,
        2: 0.55,
        3: 0.8,
        4: 0.95,
    }

    if (
        signal_score > 0
        and candidate_signal_confidence == 0.0
    ):
        signal_confidence = (
            confidence_map.get(
                signal_score,
                0.0,
            )
        )
    else:
        signal_confidence = (
            candidate_signal_confidence
        )

    relevant = (
        candidate.contains_child
        and signal_confidence >= 0.55
    )

    return {
        "relevant": relevant,

        "reason": (
            "potential_child_exposure"
            if relevant
            else None
        ),

        "confidence": (
            signal_confidence
        ),

        "signal_score": (
            signal_score
        ),

        "signals": signals,

        "source": (
            "monitoring_detector_v2"
        ),
    }