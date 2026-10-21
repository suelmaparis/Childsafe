from app.api.reports import ReportCreate, create_report_record
from app.services.ai_risk_assessment import AIRiskAssessment


def test_review_cannot_overwrite_school_signals(
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

    original = {
        "school_context": True,
        "school_uniform_mentioned": True,
        "school_schedule_mentioned": False,
    }

    report = ReportCreate(
        platform="Instagram",
        url="https://example.com/tampering-test",
        reason="potential_child_exposure",
        description="Synthetic integrity test.",
        source_type="automated_monitoring",
        source_channel="test_internal_collector",
        school_signals=original,
    )

    created = create_report_record(
        report=report,
        db=db_session,
    )

    report_id = int(
        created["report_id"].replace("CV-", "")
    )

    # Attempt to overwrite the original indicators.
    response = client.patch(
        f"/reports/{report_id}/review",
        headers=auth_headers,
        json={
            "new_status": "under_review",
            "decision": "manual_review_started",
            "notes": "Synthetic test.",
            "school_signals": {
                "school_context": False,
                "school_uniform_mentioned": False,
                "school_schedule_mentioned": False,
            },
        },
    )

    # The API may reject or ignore the extra field.
    assert response.status_code == 422

    # In either case, original evidence must remain intact.
    response = client.get(
        f"/reports/{report_id}/audit",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["school_signals"] == original
