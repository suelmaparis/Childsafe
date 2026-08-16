from dataclasses import dataclass


@dataclass
class RiskAssessment:
    level: str
    score: int
    reasons: list[str]


def assess_risk(
    reason: str,
    description: str,
) -> RiskAssessment:
    """
    Perform a basic rule-based risk assessment.

    This is an initial development version.
    It does not determine guilt or make enforcement decisions.
    """

    text = f"{reason} {description}".lower()

    score = 0
    reasons = []

    # Potential exposure of a child.
    if "potential_child_exposure" in text:
        score += 20
        reasons.append("Potential exposure of a minor.")

    # Vulnerability indicators.
    vulnerability_terms = [
        "vulnerable",
        "vulnerability",
        "danger",
        "unsafe",
        "abuse",
    ]

    if any(term in text for term in vulnerability_terms):
        score += 30
        reasons.append("Possible vulnerability or safety concern.")

    # Sexual exploitation indicators.
    exploitation_terms = [
        "sexual exploitation",
        "sexualized",
        "sexualisation",
        "sexualization",
        "exploitation",
    ]

    if any(term in text for term in exploitation_terms):
        score += 40
        reasons.append("Possible sexual exploitation indicator.")

    # Immediate danger indicators.
    danger_terms = [
        "immediate danger",
        "imminent danger",
        "child trafficking",
        "trafficking",
    ]

    if any(term in text for term in danger_terms):
        score += 50
        reasons.append("Possible immediate or severe danger.")

    # Convert score into a risk level.
    if score >= 70:
        level = "critical"
    elif score >= 40:
        level = "high"
    elif score >= 20:
        level = "medium"
    else:
        level = "low"
    return RiskAssessment(
        level=level,
        score=score,
        reasons=reasons,
    )