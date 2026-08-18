from dataclasses import dataclass


LEVEL_RANK = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


@dataclass
class ReviewQueuePriority:
    priority: str
    priority_score: int
    reason: str


def determine_queue_priority(
    risk_level: str,
    risk_score: int,
    ai_level: str | None = None,
    ai_score: int | None = None,
) -> ReviewQueuePriority:
    """
    Determine review-queue priority.

    The deterministic assessment is always available.
    The AI assessment is optional and only affects priority
    when an actual AI analysis exists.

    This function does not make enforcement or final review decisions.
    It only determines how prominently a pending report should
    appear in the human review queue.
    """

    if risk_level not in LEVEL_RANK:
        raise ValueError(
            f"Invalid deterministic risk level: {risk_level}"
        )

    if not 0 <= risk_score <= 100:
        raise ValueError(
            "Deterministic risk score must be between 0 and 100."
        )

    # No AI analysis available.
    if ai_level is None or ai_score is None:
        if risk_level == "critical":
            return ReviewQueuePriority(
                priority="urgent",
                priority_score=1000,
                reason=(
                    "Deterministic assessment indicates "
                    "critical potential child-safety risk."
                ),
            )

        if risk_level == "high":
            return ReviewQueuePriority(
                priority="priority",
                priority_score=700,
                reason=(
                    "Deterministic assessment indicates "
                    "high potential child-safety risk."
                ),
            )

        if risk_level == "medium":
            return ReviewQueuePriority(
                priority="normal",
                priority_score=500,
                reason=(
                    "Deterministic assessment indicates "
                    "moderate potential child-safety risk."
                ),
            )

        return ReviewQueuePriority(
            priority="normal",
            priority_score=300,
            reason="Standard human review required.",
        )

    if ai_level not in LEVEL_RANK:
        raise ValueError(
            f"Invalid AI risk level: {ai_level}"
        )

    if not 0 <= ai_score <= 100:
        raise ValueError(
            "AI risk score must be between 0 and 100."
        )

    rule_rank = LEVEL_RANK[risk_level]
    ai_rank = LEVEL_RANK[ai_level]

    score_difference = abs(
        ai_score - risk_score
    )

    level_difference = abs(
        ai_rank - rule_rank
    )

    # Critical risk identified by either layer.
    if (
        risk_level == "critical"
        or ai_level == "critical"
    ):
        return ReviewQueuePriority(
            priority="urgent",
            priority_score=1000,
            reason=(
                "Critical potential child-safety "
                "risk identified."
            ),
        )

    # Significant disagreement.
    if (
        level_difference >= 2
        or score_difference >= 30
    ):
        return ReviewQueuePriority(
            priority="urgent",
            priority_score=900,
            reason=(
                "Significant disagreement between "
                "deterministic and AI risk assessments."
            ),
        )

    # High risk identified by either layer.
    if (
        risk_level == "high"
        or ai_level == "high"
    ):
        return ReviewQueuePriority(
            priority="priority",
            priority_score=700,
            reason=(
                "High potential child-safety risk identified."
            ),
        )

    # Medium risk.
    if (
        risk_level == "medium"
        or ai_level == "medium"
    ):
        return ReviewQueuePriority(
            priority="normal",
            priority_score=500,
            reason=(
                "Moderate potential child-safety risk identified."
            ),
        )

    return ReviewQueuePriority(
        priority="normal",
        priority_score=300,
        reason="Standard human review required.",
    )