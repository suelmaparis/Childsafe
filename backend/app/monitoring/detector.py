from app.core import settings
from app.monitoring.candidate import MonitoringCandidate

WEIGHTS = {
    "volunteer_context": 2,
    "school_uniform": 3,
    "school_schedule": 3,
    "school_context": 1,
    "location_detected": 1,
    "tourism_context": 1,
}
STRONG = {"volunteer_context", "school_uniform", "school_schedule"}
MIN_SCORE = 3


def detect_candidate(candidate: MonitoringCandidate) -> dict:
    school = (candidate.metadata or {}).get("school_signals") or {}

    active = {
        "volunteer_context": candidate.volunteer_context,
        "school_uniform": school.get("school_uniform_mentioned"),
        "school_schedule": school.get("school_schedule_mentioned"),
        "school_context": school.get("school_context"),
        "location_detected": candidate.location_detected,
        "tourism_context": candidate.tourism_context,
    }
    signals = [name for name, on in active.items() if on]
    score = sum(WEIGHTS[name] for name in signals)

    require_location = getattr(settings, "MONITORING_REQUIRE_LOCATION", True)
    location_ok = bool(candidate.location_detected) or not require_location

    relevant = (
        bool(candidate.contains_child)
        and location_ok
        and score >= MIN_SCORE
        and bool(STRONG & set(signals))
    )

    return {
        "relevant": relevant,
        "reason": "potential_child_exposure" if relevant else None,
        "confidence": min(score / 6, 1.0),
        "signal_score": score,
        "signals": (["child_detected"] if candidate.contains_child else []) + signals,
        "source": "monitoring_detector_v3",
    }