import json

from app.models.report import Report
from app.monitoring.candidate import MonitoringCandidate
from app.monitoring.engine import process_candidate


def test_automated_report_persists_signal_score(db_session):
    candidate = MonitoringCandidate(
        platform="Instagram",
        url="https://example.com/monitoring-score-test",
        description="Synthetic monitoring test candidate.",
        reason="potential_child_exposure",
        source_channel="meta_instagram_collector",
        source_reference="TEST-SIGNAL-SCORE-001",
        contains_child=True,
        location_detected=True,
        volunteer_context=False,
        tourism_context=False,
        signal_score=2,
        signal_confidence=0.55,
    )

    result = process_candidate(
        candidate=candidate,
        db=db_session,
    )

    assert result.get("status") not in (
        "ignored",
        "duplicate",
    )

    report = (
        db_session.query(Report)
        .filter(
            Report.source_reference
            == "TEST-SIGNAL-SCORE-001"
        )
        .one()
    )

    assert report.source_type == "automated_monitoring"
    assert report.detection_signal_score == 2
    assert report.detection_confidence == 0.55

    assert set(json.loads(report.detection_signals)) == {
        "child_detected",
        "location_detected",
    }
