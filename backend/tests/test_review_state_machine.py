from app.services.review_state_machine import validate_review_transition


def test_pending_to_under_review_is_allowed():
    result = validate_review_transition(
        "pending",
        "under_review",
    )

    assert result.allowed is True


def test_under_review_to_reviewed_is_allowed():
    result = validate_review_transition(
        "under_review",
        "reviewed",
    )

    assert result.allowed is True


def test_reviewed_to_confirmed_is_allowed():
    result = validate_review_transition(
        "reviewed",
        "confirmed",
    )

    assert result.allowed is True


def test_pending_to_confirmed_is_blocked():
    result = validate_review_transition(
        "pending",
        "confirmed",
    )

    assert result.allowed is False


def test_confirmed_to_dismissed_is_blocked():
    result = validate_review_transition(
        "confirmed",
        "dismissed",
    )

    assert result.allowed is False


def test_duplicate_status_is_blocked():
    result = validate_review_transition(
        "under_review",
        "under_review",
    )

    assert result.allowed is False
