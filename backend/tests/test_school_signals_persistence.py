import json

from app.models.report import Report
from app.monitoring.collectors.meta_instagram import (
    MetaInstagramCollector,
)
from app.monitoring.engine import process_candidate


def test_school_signals_are_saved_in_report(db_session):
    collector = MetaInstagramCollector(client=object())

    candidate = collector._to_candidate({
        "id": "TEST-SCHOOL-PERSISTENCE-001",
        "permalink": "https://example.com/school-persistence",
        "caption": (
            "Crianças com uniforme escolar durante "
            "o horário escolar em Mindelo."
        ),
    })

    result = process_candidate(
        candidate=candidate,
        db=db_session,
    )

    assert result.get("status") not in (
        "ignored",
        "duplicate",
    )

    report = db_session.query(Report).filter(
        Report.source_reference
        == "TEST-SCHOOL-PERSISTENCE-001"
    ).one()

    school = json.loads(report.school_signals)

    assert school["school_context"] is True
    assert school["school_uniform_mentioned"] is True
    assert school["school_schedule_mentioned"] is True

    assert report.detection_signal_score == 2
    assert report.source_type == "automated_monitoring"
