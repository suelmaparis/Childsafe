import pytest
from pydantic import ValidationError

from app.api.reports import ReportCreate


def make_report(**extra):
    return ReportCreate(
        platform="Instagram",
        url="https://example.com/school-validation",
        reason="potential_child_exposure",
        description="Synthetic test report.",
        **extra,
    )


def test_valid_school_signals():
    signals = {
        "school_context": True,
        "school_uniform_mentioned": False,
        "school_schedule_mentioned": True,
    }

    report = make_report(school_signals=signals)

    assert report.school_signals == signals


def test_school_signals_are_optional():
    report = make_report()

    assert report.school_signals is None


@pytest.mark.parametrize(
    "invalid_signals",
    [
        {},
        {"school_context": True},
        {
            "school_context": True,
            "school_uniform_mentioned": False,
            "school_schedule_mentioned": True,
            "child_name": "Test",
        },
        {
            "school_context": "true",
            "school_uniform_mentioned": False,
            "school_schedule_mentioned": True,
        },
        {
            "school_context": 1,
            "school_uniform_mentioned": False,
            "school_schedule_mentioned": True,
        },
    ],
)
def test_invalid_school_signals_are_rejected(
    invalid_signals,
):
    with pytest.raises(ValidationError):
        make_report(school_signals=invalid_signals)
