import pytest

from app.services.review_queue_priority import determine_queue_priority


def test_medium_without_ai_is_normal():
    result = determine_queue_priority(
        risk_level="medium",
        risk_score=20,
    )

    assert result.priority == "normal"
    assert result.priority_score == 500


def test_high_without_ai_is_priority():
    result = determine_queue_priority(
        risk_level="high",
        risk_score=50,
    )

    assert result.priority == "priority"
    assert result.priority_score == 700


def test_critical_without_ai_is_urgent():
    result = determine_queue_priority(
        risk_level="critical",
        risk_score=100,
    )

    assert result.priority == "urgent"
    assert result.priority_score == 1000


def test_significant_ai_disagreement_is_urgent():
    result = determine_queue_priority(
        risk_level="medium",
        risk_score=20,
        ai_level="high",
        ai_score=75,
    )

    assert result.priority == "urgent"
    assert result.priority_score == 900


def test_ai_critical_is_urgent():
    result = determine_queue_priority(
        risk_level="medium",
        risk_score=20,
        ai_level="critical",
        ai_score=95,
    )

    assert result.priority == "urgent"
    assert result.priority_score == 1000


def test_rule_critical_with_ai_is_urgent():
    result = determine_queue_priority(
        risk_level="critical",
        risk_score=100,
        ai_level="high",
        ai_score=75,
    )

    assert result.priority == "urgent"
    assert result.priority_score == 1000


def test_invalid_risk_level_is_rejected():
    with pytest.raises(ValueError):
        determine_queue_priority(
            risk_level="invalid",
            risk_score=20,
        )


def test_invalid_ai_score_is_rejected():
    with pytest.raises(ValueError):
        determine_queue_priority(
            risk_level="medium",
            risk_score=20,
            ai_level="high",
            ai_score=101,
        )
