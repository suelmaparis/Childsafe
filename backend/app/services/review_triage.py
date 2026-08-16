from dataclasses import dataclass


@dataclass
class ReviewTriage:
    priority: str
    recommended_queue: str


def determine_review_priority(risk_level: str) -> ReviewTriage:
    """
    Determine the review priority based on the automated risk level.

    This function does not make enforcement decisions.
    It only determines how urgently a report should be reviewed.
    """

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

    if risk_level == "medium":
        return ReviewTriage(
            priority="normal",
            recommended_queue="standard_review",
        )

    return ReviewTriage(
        priority="normal",
        recommended_queue="standard_review",
    )
