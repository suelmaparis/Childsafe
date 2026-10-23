from app.api.reports import ReportCreate, create_report_record
from app.models.report import Report
from app.services.ai_risk_assessment import AIRiskAssessment


def test_geo_location_is_saved_as_unverified(
    db_session,
    monkeypatch,
):
    """Uma localidade mencionada não confirma coordenadas."""

    def fake_ai_assessment(reason, description):
        return AIRiskAssessment(
            level="low",
            score=10,
            reasons=["Synthetic test."],
        )

    monkeypatch.setattr(
        "app.api.reports.assess_risk_with_ai",
        fake_ai_assessment,
    )

    report = ReportCreate(
        platform="Instagram",
        url="https://example.com/geo-test-001",
        reason="potential_child_exposure",
        description="Publicação menciona Mindelo.",
        source_type="automated_monitoring",
        source_channel="test_internal_collector",
    )

    created = create_report_record(
        report=report,
        db=db_session,
    )

    report_id = int(
        created["report_id"].replace("CV-", "")
    )

    saved_report = db_session.get(
        Report,
        report_id,
    )

    assert saved_report is not None
    assert saved_report.geo_location_text == "mindelo"
    assert saved_report.geo_source == "publication_text"
    assert saved_report.geo_verification_status == "pending"

    # Uma referência textual não permite determinar coordenadas.
    assert saved_report.geo_latitude is None
    assert saved_report.geo_longitude is None
    assert saved_report.geo_coordinate_type is None
