from dataclasses import dataclass
from app.monitoring.signal_extractor import normalize_text

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

    The score is normalized to a 0-100 range.

    This assessment does not determine guilt
    or make enforcement decisions.
    """

    text = f"{reason} {description}".lower()

    score = 0
    reasons: list[str] = []

    # Potential child exposure is a reason for review,
    # not automatic proof of harmful exposure.
    # These indicators support preliminary triage.
    # They do not establish that the assessed post
    # directly exposed a child.
    normalized_description = normalize_text(description)

    exposure_indicators = (
        "child appears in a public post",
        "nome completo",
        "morada da crianca",
        "endereco da crianca",
        "horario de saida",
        "localizacao exata",
        "school address",
        "home address",
        "full name",
        "where the child regularly spends time",
    )

    potential_exposure = any(
        indicator in normalized_description
        for indicator in exposure_indicators
    )

    if (
        reason == "potential_child_exposure"
        and potential_exposure
    ):
        score += 20
        reasons.append(
            "Potential disclosure of child-related information."
        )
    # Vulnerability indicators.
    vulnerability_terms = [
        "vulnerable",
        "vulnerability",
        "danger",
        "unsafe",
        "abuse",
    ]

    if any(
        term in text
        for term in vulnerability_terms
    ):
        score += 30
        reasons.append(
            "Possible vulnerability or safety concern."
        )

    # Sexual exploitation indicators.
    exploitation_terms = [
        "sexual exploitation",
        "sexualized",
        "sexualisation",
        "sexualization",
        "exploitation",
    ]

    if any(
        term in text
        for term in exploitation_terms
    ):
        score += 40
        reasons.append(
            "Possible sexual exploitation indicator."
        )

    # Immediate danger indicators.
    danger_terms = [
        "immediate danger",
        "imminent danger",
        "child trafficking",
        "trafficking",
    ]

    if any(
        term in text
        for term in danger_terms
    ):
        score += 50
        reasons.append(
            "Possible immediate or severe danger."
        )

    # Normalize score to the same 0-100 scale
    # used by the AI risk assessment.
    score = min(score, 100)

    # Convert normalized score into a risk level.
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