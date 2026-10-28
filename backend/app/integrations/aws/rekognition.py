from typing import Any
from app.services.image_validation import validate_image

SENSITIVE_LABELS = {
    "Explicit Nudity",
    "Nudity",
    "Suggestive",
}

def parse_rekognition_results(
    faces_response: dict[str, Any],
    moderation_response: dict[str, Any],
) -> dict[str, float]:
    """
    Convert AWS Rekognition responses into preliminary
    visual indicators for human review.

    Age estimates are uncertain and do not confirm
    whether a person is a minor.
    """

    minor_likelihood = 0.0

    for face in faces_response.get("FaceDetails", []):
        age_range = face.get("AgeRange", {})

        low = age_range.get("Low")
        high = age_range.get("High")

        if not isinstance(low, (int, float)):
            continue

        if not isinstance(high, (int, float)):
            continue

        if high <= 17:
            minor_likelihood = max(
                minor_likelihood,
                0.7,
            )
        elif low <= 17:
            minor_likelihood = max(
                minor_likelihood,
                0.4,
            )

    sensitive_score = 0.0

    for label in moderation_response.get(
        "ModerationLabels", []
    ):
        name = label.get("Name", "")
        parent = label.get("ParentName", "")
        confidence = label.get("Confidence", 0)

        if (
            name in SENSITIVE_LABELS
            or parent in SENSITIVE_LABELS
        ):
            if isinstance(confidence, (int, float)):
                sensitive_score = max(
                    sensitive_score,
                    min(max(confidence / 100, 0.0), 1.0),
                )

    return {
        "minor_likelihood": minor_likelihood,
        "sensitive_score": sensitive_score,
    }
def analyze_image_with_rekognition(
    image_bytes: bytes,
    client=None,
) -> dict[str, float]:
    """
    Analyze image bytes using AWS Rekognition.

    Returns preliminary visual indicators.
    Does not store the image locally.
    """
    from app.core import settings

    if not settings.MEDIA_ANALYSIS_ENABLED:
        raise RuntimeError(
            "Media analysis is disabled."
        )
      # Validate the image before sending it to AWS.
    validate_image(image_bytes)
    
    if client is None:
        import boto3

        client = boto3.client("rekognition")

    faces_response = client.detect_faces(
        Image={"Bytes": image_bytes},
        Attributes=["ALL"],
    )

    moderation_response = client.detect_moderation_labels(
        Image={"Bytes": image_bytes},
        MinConfidence=50,
    )

    return parse_rekognition_results(
        faces_response=faces_response,
        moderation_response=moderation_response,
    )
