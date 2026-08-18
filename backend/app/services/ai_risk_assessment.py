import json
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


AI_MODEL = "gpt-5-mini"


@dataclass
class AIRiskAssessment:
    level: str
    score: int
    reasons: list[str]


api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is not configured."
    )


client = OpenAI(
    api_key=api_key,
)


def assess_risk_with_ai(
    reason: str,
    description: str,
) -> AIRiskAssessment:
    """
    Use AI as a secondary child-safety risk-analysis layer.

    The AI does not determine guilt, enforcement,
    account removal, or final review decisions.
    """

    prompt = f"""
You are a secondary risk-analysis assistant for a child online
safety review system.

Analyze only the information explicitly provided in this report.

Reason:
{reason}

Description:
{description}

Assess potential child-safety risk.

Return ONLY valid JSON with exactly this structure:

{{
  "level": "low|medium|high|critical",
  "score": 0,
  "reasons": [
    "reason 1",
    "reason 2"
  ]
}}

Rules:
- score must be an integer from 0 to 100.
- level must be one of: low, medium, high, critical.
- Do not determine guilt.
- Do not identify a person as a criminal.
- Do not recommend punishment or enforcement.
- Do not recommend removing an account.
- Do not invent facts that are not present in the report.
- Focus only on potential child-safety risk indicators.
- If information is insufficient or ambiguous, reflect that uncertainty.
- Keep reasons concise and factual.
"""

    response = client.responses.create(
        model=AI_MODEL,
        input=prompt,
    )

    try:
        data = json.loads(
            response.output_text
        )
    except json.JSONDecodeError as exc:
        raise ValueError(
            "AI returned invalid JSON."
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            "AI returned an invalid response structure."
        )

    try:
        level = data["level"]
        score = int(data["score"])
        reasons = data["reasons"]
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(
            "AI response is missing required fields."
        ) from exc

    if level not in {
        "low",
        "medium",
        "high",
        "critical",
    }:
        raise ValueError(
            "AI returned an invalid risk level."
        )

    if not 0 <= score <= 100:
        raise ValueError(
            "AI returned an invalid risk score."
        )

    if not isinstance(reasons, list):
        raise ValueError(
            "AI returned invalid risk reasons."
        )

    if not all(
        isinstance(reason_item, str)
        for reason_item in reasons
    ):
        raise ValueError(
            "AI risk reasons must contain only strings."
        )

    return AIRiskAssessment(
        level=level,
        score=score,
        reasons=reasons,
    )