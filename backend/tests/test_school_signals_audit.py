from app.api.reports import ReportCreate, create_report_record
from app.services.ai_risk_assessment import AIRiskAssessment


def test_school_signals_in_audit(
    client,
    auth_headers,
    monkeypatch,
    db_session,
):
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

    school_signals = {
        "school_context": True,
        "school_uniform_mentioned": True,
        "school_schedule_mentioned": True,
    }

    def create_and_audit(url, signals=None):
        report = ReportCreate(
            platform="Instagram",
            url=url,
            reason="potential_child_exposure",
            description="Synthetic child protection test.",
            source_type="automated_monitoring",
            source_channel="test_internal_collector",
            school_signals=signals,
        )

        created = create_report_record(
            report=report,
            db=db_session,
        )

        report_id = int(
            created["report_id"].replace("CV-", "")
        )

        response = client.get(
            f"/reports/{report_id}/audit",
            headers=auth_headers,
        )
        assert response.status_code == 200

        return response.json()

    with_school = create_and_audit(
        "https://example.com/audit-school-001",
        school_signals,
    )

    without_school = create_and_audit(
        "https://example.com/audit-school-002",
    )

    assert (
        with_school["school_signals"]
        == school_signals
    )

    assert without_school["school_signals"] is None

    assert (
        with_school["deterministic_assessment"]
        == without_school["deterministic_assessment"]
    )
