from app.services.risk_assessment import assess_risk


def test_low_risk():
    result = assess_risk(
        "general_content",
        "A normal family photo with no safety concern.",
    )

    assert result.level == "low"
    assert result.score == 0


def test_medium_risk():
    result = assess_risk(
        "potential_child_exposure",
        "A child appears in a public post.",
    )

    assert result.level == "medium"
    assert result.score == 20


def test_critical_risk_score_is_capped_at_100():
    result = assess_risk(
        "suspected_exploitation",
        (
            "Possible sexual exploitation and immediate danger "
            "involving a vulnerable child."
        ),
    )

    assert result.level == "critical"
    assert result.score == 100
    assert result.score <= 100
