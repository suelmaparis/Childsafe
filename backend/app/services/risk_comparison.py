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
    Compare the deterministic risk assessment with the AI assessment.

    This function does not make enforcement or final review decisions.
    It only identifies agreement or disagreement between the two
    assessment layers.
    """

    rule_rank = LEVEL_ORDER.get(rule_level, 0)
    ai_rank = LEVEL_ORDER.get(ai_level, 0)

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
