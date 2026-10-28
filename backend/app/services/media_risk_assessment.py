from dataclasses import dataclass, field


@dataclass
class MediaRiskAssessment:
    """
    Preliminary media risk assessment.

    Scores are indicators for human review,
    not proof of exploitation or criminal activity.
    """

    media_type: str
    score: int
    level: str
    reasons: list[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)


def risk_level_from_score(score: int) -> str:
    """
    Convert a 0-100 score into a risk level.

    Uses the same thresholds as the existing
    rule-based risk assessment.
    """
    if not 0 <= score <= 100:
        raise ValueError("Risk score must be between 0 and 100.")

    if score >= 70:
        return "critical"
    if score >= 40:
        return "high"
    if score >= 20:
        return "medium"
    return "low"
def assess_image_signals(
    minor_likelihood: float,
    sensitive_score: float,
) -> MediaRiskAssessment:
    """
    Assess preliminary visual signals from an image.

    Both inputs must be between 0.0 and 1.0.

    This function does not confirm age, abuse,
    exploitation, or criminal activity.
    """

    for value in (minor_likelihood, sensitive_score):
        if not 0.0 <= value <= 1.0:
            raise ValueError(
                "Image signals must be between 0.0 and 1.0."
            )

    # Both signals are required for a combined
    # preliminary visual risk indicator.
    combined_signal = minor_likelihood * sensitive_score

    # Limit automated visual assessment to medium.
    # Higher levels require additional contextual evidence.
    score = min(round(combined_signal * 100), 39)

    reasons = []

    if minor_likelihood >= 0.5:
        reasons.append(
            "Possible minor detected; age is unverified."
        )

    if sensitive_score >= 0.5:
        reasons.append(
            "Potentially sensitive visual content detected."
        )

    if not reasons:
        reasons.append(
            "No strong visual risk indicators detected."
        )

    return MediaRiskAssessment(
        media_type="image",
        score=score,
        level=risk_level_from_score(score),
        reasons=reasons,
        details={
            "minor_likelihood": minor_likelihood,
            "sensitive_score": sensitive_score,
        },
    )
