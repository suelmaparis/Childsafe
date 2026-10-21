def test_report_submission_rejects_invalid_url(
    client,
    monkeypatch,
):
    def fake_create_report_record(report, db):
        return {
            "report_id": "CV-000001",
            "status": "received",
        }

    monkeypatch.setattr(
        "app.api.reports.create_report_record",
        fake_create_report_record,
    )

    response = client.post(
        "/reports/",
        json={
            "platform": "Instagram",
            "url": "not-a-valid-url",
            "reason": "potential_child_exposure",
            "description": (
                "Synthetic security test without real child data."
            ),
        },
    )

    assert response.status_code == 422
