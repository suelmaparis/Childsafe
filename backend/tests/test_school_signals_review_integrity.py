from app.api.reports import ReportCreate, create_report_record
from app.services.ai_risk_assessment import AIRiskAssessment


def test_review_preserves_original_school_signals(
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

    original_signals = {
        "school_context": True,
        "school_uniform_mentioned": True,
        "school_schedule_mentioned": False,
    }

    # 1. Create a synthetic report internally.
    report = ReportCreate(
        platform="Instagram",
        url="https://example.com/review-integrity",
        reason="potential_child_exposure",
        description="Synthetic school signals test.",
        source_type="automated_monitoring",
        source_channel="test_internal_collector",
        school_signals=original_signals,
    )

    created = create_report_record(
        report=report,
        db=db_session,
    )

    report_id = int(
        created["report_id"].replace("CV-", "")
    )

    # 2. Check the original audit data.
    response = client.get(
        f"/reports/{report_id}/audit",
        headers=auth_headers,
    )

    assert response.status_code == 200
    before = response.json()

    assert before["school_signals"] == original_signals

    # 3. Start human review.
    response = client.patch(
        f"/reports/{report_id}/review",
        headers=auth_headers,
        json={
            "new_status": "under_review",
            "decision": "manual_review_started",
            "notes": "Synthetic human review test.",
        },
    )

    assert response.status_code == 200

    # 4. Verify the original signals are unchanged.
    response = client.get(
        f"/reports/{report_id}/audit",
        headers=auth_headers,
    )

    assert response.status_code == 200
    after = response.json()

    assert after["school_signals"] == original_signals

    # 5. Verify risk assessment was not changed.
    assert (
        after["deterministic_assessment"]
        == before["deterministic_assessment"]
    )

    # 6. Verify review history was recorded.
    response = client.get(
        f"/reports/{report_id}/reviews",
        headers=auth_headers,
    )

    assert response.status_code == 200
    reviews = response.json()

    assert any(
        review["new_status"] == "under_review"
        for review in reviews
    )
