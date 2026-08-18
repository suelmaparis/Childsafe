import pytest

from app.services.risk_comparison import compare_risk_assessments


def test_aligned_assessments():
    result = compare_risk_assessments(
        rule_level="medium",
        rule_score=20,
        ai_level="medium",
        ai_score=25,
    )

    assert result.relationship == "aligned"
    assert result.level_difference == 0
    assert result.score_difference == 5
    assert result.needs_attention is False


def test_ai_higher_with_significant_score_difference():
    result = compare_risk_assessments(
        rule_level="medium",
        rule_score=20,
        ai_level="high",
        ai_score=75,
    )

    assert result.relationship == "ai_higher"
    assert result.level_difference == 1
    assert result.score_difference == 55
    assert result.needs_attention is True


def test_rule_higher():
    result = compare_risk_assessments(
        rule_level="high",
        rule_score=70,
        ai_level="medium",
        ai_score=45,
    )

    assert result.relationship == "rule_higher"
    assert result.level_difference == -1
    assert result.score_difference == -25
    assert result.needs_attention is False


def test_two_level_difference_needs_attention():
    result = compare_risk_assessments(
        rule_level="low",
        rule_score=10,
        ai_level="high",
        ai_score=20,
    )

    assert result.level_difference == 2
    assert result.needs_attention is True


def test_invalid_rule_level_is_rejected():
    with pytest.raises(ValueError):
        compare_risk_assessments(
            rule_level="invalid",
            rule_score=20,
            ai_level="high",
            ai_score=75,
        )


def test_invalid_ai_score_is_rejected():
    with pytest.raises(ValueError):
        compare_risk_assessments(
            rule_level="medium",
            rule_score=20,
            ai_level="high",
            ai_score=101,
        )
