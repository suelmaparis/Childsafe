from dataclasses import dataclass


VALID_RISK_LEVELS = {
    "low",
    "medium",
    "high",
    "critical",
}


@dataclass
class ReviewTriage:
    priority: str
    recommended_queue: str


def determine_review_priority(
    risk_level: str,
) -> ReviewTriage:
    """
    Determine the initial review triage based only
    on the deterministic risk level.

    This function does not make enforcement decisions.
    It only determines the initial review routing.
    """

    if risk_level not in VALID_RISK_LEVELS:
        raise ValueError(
            f"Invalid risk level: {risk_level}"
        )

    if risk_level == "critical":
        return ReviewTriage(
            priority="urgent",
            recommended_queue="urgent_review",
        )

    if risk_level == "high":
        return ReviewTriage(
            priority="priority",
            recommended_queue="priority_review",
        )

    return ReviewTriage(
        priority="normal",
        recommended_queue="standard_review",
    )