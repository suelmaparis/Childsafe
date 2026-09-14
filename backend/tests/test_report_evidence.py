def _create_report(
    client,
    auth_headers,
):
    response = client.post(
        "/reports/",
        headers=auth_headers,
        json={
            "platform": "Instagram",
            "url": (
                "https://example.com/"
                "evidence-test"
            ),
            "reason":
                "potential_child_exposure",
            "description":
                "Report for evidence tests.",
        },
    )

    assert response.status_code == 200

    return response.json()


def test_reviewer_can_create_report_evidence(
    client,
    auth_headers,
):
    report = _create_report(
        client,
        auth_headers,
    )

    report_id = int(
        report["report_id"].replace(
            "CV-",
            "",
        )
    )

    response = client.post(
        f"/reports/{report_id}/evidence",
        headers=auth_headers,
        json={
            "evidence_type":
                "url_snapshot",
            "source_url":
                "https://example.com/content",
            "platform":
                "Instagram",
            "external_reference":
                "REF-001",
            "content_hash":
                "abc123",
            "notes":
                "Captured during review.",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["report_id"] == report_id
    assert (
        data["evidence_type"]
        == "url_snapshot"
    )
    assert (
        data["external_reference"]
        == "REF-001"
    )


def test_can_list_report_evidence(
    client,
    auth_headers,
):
    report = _create_report(
        client,
        auth_headers,
    )

    report_id = int(
        report["report_id"].replace(
            "CV-",
            "",
        )
    )

    create_response = client.post(
        f"/reports/{report_id}/evidence",
        headers=auth_headers,
        json={
            "evidence_type":
                "reviewer_note",
            "notes":
                "Evidence note.",
        },
    )

    assert (
        create_response.status_code
        == 201
    )

    response = client.get(
        f"/reports/{report_id}/evidence",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 1
    assert (
        data[-1]["evidence_type"]
        == "reviewer_note"
    )


def test_invalid_evidence_type_returns_422(
    client,
    auth_headers,
):
    report = _create_report(
        client,
        auth_headers,
    )

    report_id = int(
        report["report_id"].replace(
            "CV-",
            "",
        )
    )

    response = client.post(
        f"/reports/{report_id}/evidence",
        headers=auth_headers,
        json={
            "evidence_type":
                "invalid_type",
            "notes":
                "Invalid evidence.",
        },
    )

    assert response.status_code == 422


def test_create_evidence_for_missing_report_returns_404(
    client,
    auth_headers,
):
    response = client.post(
        "/reports/999999/evidence",
        headers=auth_headers,
        json={
            "evidence_type":
                "reviewer_note",
            "notes":
                "Missing report.",
        },
    )

    assert response.status_code == 404


def test_list_evidence_for_missing_report_returns_404(
    client,
    auth_headers,
):
    response = client.get(
        "/reports/999999/evidence",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_report_evidence_requires_authentication(
    client,
):
    response = client.get(
        "/reports/1/evidence"
    )

    assert response.status_code == 401