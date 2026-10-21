from app.api.reports import limiter


def test_report_submission_is_rate_limited(
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

    payload = {
        "platform": "Instagram",
        "url": "https://example.com/rate-limit-test",
        "reason": "potential_child_exposure",
        "description": (
            "Synthetic security test without real child data."
        ),
    }

    limiter.reset()

    try:
        for _ in range(5):
            response = client.post(
                "/reports/",
                json=payload,
            )
            assert response.status_code == 200

        response = client.post(
            "/reports/",
            json=payload,
        )

        assert response.status_code == 429

    finally:
        limiter.reset()
