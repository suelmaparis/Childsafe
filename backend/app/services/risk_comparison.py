from dataclasses import dataclass


LEVEL_ORDER = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


@dataclass
class RiskComparison:
    relationship: str
    level_difference: int
    score_difference: int
    needs_attention: bool


def compare_risk_assessments(
    rule_level: str,
    rule_score: int,
    ai_level: str,
    ai_score: int,
) -> RiskComparison:
    """
    Compare the deterministic risk assessment
    with the AI assessment.

    Positive differences mean the AI assessment
    is higher than the deterministic assessment.

    This function does not make enforcement
    or final review decisions.
    """

    if rule_level not in LEVEL_ORDER:
        raise ValueError(
            f"Invalid deterministic risk level: {rule_level}"
        )

    if ai_level not in LEVEL_ORDER:
        raise ValueError(
            f"Invalid AI risk level: {ai_level}"
        )

    if not 0 <= rule_score <= 100:
        raise ValueError(
            "Deterministic risk score must be between 0 and 100."
        )

    if not 0 <= ai_score <= 100:
        raise ValueError(
            "AI risk score must be between 0 and 100."
        )

    rule_rank = LEVEL_ORDER[rule_level]
    ai_rank = LEVEL_ORDER[ai_level]

    level_difference = ai_rank - rule_rank
    score_difference = ai_score - rule_score

    if level_difference == 0:
        relationship = "aligned"
    elif level_difference > 0:
        relationship = "ai_higher"
    else:
        relationship = "rule_higher"

    needs_attention = (
        abs(level_difference) >= 2
        or abs(score_difference) >= 30
    )

    return RiskComparison(
        relationship=relationship,
        level_difference=level_difference,
        score_difference=score_difference,
        needs_attention=needs_attention,
    )