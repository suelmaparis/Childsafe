def test_unauthenticated_request_cannot_claim_automated_origin(
    client,
):
    response = client.post(
        "/reports/",
        json={
            "platform": "Instagram",
            "url": "https://example.com/security-test",
            "reason": "potential_child_exposure",
            "description": (
                "Synthetic security test without real child data."
            ),
            "source_type": "automated_monitoring",
            "source_channel": "meta_instagram_collector",
            "source_reference": "FAKE-AUTOMATED-001",
            "school_signals": {
                "school_context": True,
                "school_uniform_mentioned": True,
                "school_schedule_mentioned": True,
            },
        },
    )

    assert response.status_code in (401, 403, 422)
