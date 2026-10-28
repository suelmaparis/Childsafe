import pytest
from unittest.mock import Mock

from app.services.media_risk_assessment import (
    assess_image_signals,
    risk_level_from_score,
)

from app.integrations.aws.rekognition import (
    parse_rekognition_results,
    analyze_image_with_rekognition,
)


# ============================================================
# IMAGE RISK ASSESSMENT TESTS
# ============================================================

def test_image_with_strong_signals():
    result = assess_image_signals(0.9, 0.8)

    assert result.score == 39
    assert result.level == "medium"
    assert result.media_type == "image"


def test_image_without_strong_signals():
    result = assess_image_signals(0.1, 0.1)

    assert result.score == 1
    assert result.level == "low"


def test_image_with_one_strong_signal():
    result = assess_image_signals(0.9, 0.0)

    assert result.score == 0
    assert result.level == "low"


@pytest.mark.parametrize(
    "minor, sensitive",
    [
        (-0.1, 0.5),
        (1.1, 0.5),
        (0.5, -0.1),
        (0.5, 1.1),
    ],
)
def test_invalid_image_signals(minor, sensitive):
    with pytest.raises(ValueError):
        assess_image_signals(minor, sensitive)


def test_risk_level_boundaries():
    assert risk_level_from_score(0) == "low"
    assert risk_level_from_score(20) == "medium"
    assert risk_level_from_score(40) == "high"
    assert risk_level_from_score(70) == "critical"
    assert risk_level_from_score(100) == "critical"


# ============================================================
# REKOGNITION RESPONSE TESTS
# ============================================================

def test_rekognition_detects_possible_minor_and_sensitive_content():
    signals = parse_rekognition_results(
        faces_response={
            "FaceDetails": [
                {"AgeRange": {"Low": 10, "High": 15}}
            ]
        },
        moderation_response={
            "ModerationLabels": [
                {
                    "Name": "Suggestive",
                    "ParentName": "",
                    "Confidence": 85.0,
                }
            ]
        },
    )

    assert signals["minor_likelihood"] == 0.7
    assert signals["sensitive_score"] == 0.85


def test_rekognition_without_faces_or_sensitive_labels():
    signals = parse_rekognition_results(
        faces_response={"FaceDetails": []},
        moderation_response={"ModerationLabels": []},
    )

    assert signals["minor_likelihood"] == 0.0
    assert signals["sensitive_score"] == 0.0


def test_rekognition_with_uncertain_age():
    signals = parse_rekognition_results(
        faces_response={
            "FaceDetails": [
                {"AgeRange": {"Low": 15, "High": 25}}
            ]
        },
        moderation_response={"ModerationLabels": []},
    )

    assert signals["minor_likelihood"] == 0.4
    assert signals["sensitive_score"] == 0.0


def test_rekognition_limits_confidence_to_one():
    signals = parse_rekognition_results(
        faces_response={"FaceDetails": []},
        moderation_response={
            "ModerationLabels": [
                {
                    "Name": "Explicit Nudity",
                    "ParentName": "",
                    "Confidence": 150.0,
                }
            ]
        },
    )

    assert signals["sensitive_score"] == 1.0


# ============================================================
# AWS REKOGNITION MOCK TESTS
# ============================================================

def test_analyze_image_with_mock_rekognition():
    fake_client = Mock()

    fake_client.detect_faces.return_value = {
        "FaceDetails": [
            {"AgeRange": {"Low": 10, "High": 15}}
        ]
    }

    fake_client.detect_moderation_labels.return_value = {
        "ModerationLabels": [
            {
                "Name": "Suggestive",
                "ParentName": "",
                "Confidence": 85.0,
            }
        ]
    }

    signals = analyze_image_with_rekognition(
        image_bytes=b"simulated-image",
        client=fake_client,
    )

    assert signals == {
        "minor_likelihood": 0.7,
        "sensitive_score": 0.85,
    }
    fake_client.detect_moderation_labels.assert_called_once_with(
        Image={"Bytes": b"simulated-image"},
        MinConfidence=50,
    )
    fake_client.detect_faces.assert_called_once_with(
        Image={"Bytes": b"simulated-image"},
        Attributes=["ALL"],
    )

def test_rekognition_swimwear_does_not_trigger_sensitive_score():
    signals = parse_rekognition_results(
        faces_response={"FaceDetails": []},
        moderation_response={
            "ModerationLabels": [
                {
                    "Name": "Swimwear or Underwear",
                    "ParentName": "",
                    "Confidence": 93.45,
                },
                {
                    "Name": "Non-Explicit Nudity",
                    "ParentName": "Non-Explicit Nudity of Intimate parts and Kissing",
                    "Confidence": 92.32,
                },
                {
                    "Name": "Partially Exposed Female Breast",
                    "ParentName": "Non-Explicit Nudity",
                    "Confidence": 92.32,
                },
            ]
        },
    )

    assert signals["minor_likelihood"] == 0.0
    assert signals["sensitive_score"] == 0.0
def test_analyze_image_rejects_empty_bytes():
    fake_client = Mock()

    with pytest.raises(ValueError):
        analyze_image_with_rekognition(
            image_bytes=b"",
            client=fake_client,
        )

    fake_client.detect_faces.assert_not_called()
    fake_client.detect_moderation_labels.assert_not_called()


def test_analyze_image_rejects_oversized_image():
    fake_client = Mock()

    with pytest.raises(ValueError):
        analyze_image_with_rekognition(
            image_bytes=b"x" * (5 * 1024 * 1024 + 1),
            client=fake_client,
        )

    fake_client.detect_faces.assert_not_called()
    fake_client.detect_moderation_labels.assert_not_called()
    