from dataclasses import dataclass


@dataclass
class ReviewTransitionResult:
    allowed: bool
    reason: str


FINAL_STATUSES = {
    "confirmed",
    "dismissed",
    "escalated",
}


ALLOWED_TRANSITIONS = {
    "pending": {
        "under_review",
    },
    "under_review": {
        "reviewed",
    },
    "reviewed": {
        "confirmed",
        "dismissed",
        "escalated",
    },
    "confirmed": set(),
    "dismissed": set(),
    "escalated": set(),
}


VALID_STATUSES = set(
    ALLOWED_TRANSITIONS.keys()
)


def validate_review_transition(
    previous_status: str,
    new_status: str,
) -> ReviewTransitionResult:
    """
    Validate a human-review state transition.

    Final decisions cannot be changed.
    Duplicate or undefined transitions are rejected.

    This function does not make a decision about the report.
    It only validates whether the requested workflow transition
    is permitted.
    """

    if previous_status not in VALID_STATUSES:
        return ReviewTransitionResult(
            allowed=False,
            reason=(
                f"Invalid current review status: "
                f"{previous_status}."
            ),
        )

    if new_status not in VALID_STATUSES:
        return ReviewTransitionResult(
            allowed=False,
            reason=(
                f"Invalid target review status: "
                f"{new_status}."
            ),
        )

    if previous_status in FINAL_STATUSES:
        return ReviewTransitionResult(
            allowed=False,
            reason=(
                "Report has already reached "
                "a final decision."
            ),
        )

    if previous_status == new_status:
        return ReviewTransitionResult(
            allowed=False,
            reason=(
                "Report is already in this "
                "review status."
            ),
        )

    allowed_next_statuses = (
        ALLOWED_TRANSITIONS[previous_status]
    )

    if new_status not in allowed_next_statuses:
        return ReviewTransitionResult(
            allowed=False,
            reason=(
                f"Invalid review transition: "
                f"{previous_status} -> {new_status}."
            ),
        )

    return ReviewTransitionResult(
        allowed=True,
        reason="Review transition is allowed.",
    )