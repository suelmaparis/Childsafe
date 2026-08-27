def test_admin_can_assign_report(
    client,
    admin_auth_headers,
):
    created_response = client.post(
        "/reports/",
        json={
            "platform": "Instagram",
            "url": (
                "https://example.com/"
                "assign-001"
            ),
            "reason": (
                "potential_child_exposure"
            ),
            "description": (
                "Assignment test."
            ),
        },
    )

    assert created_response.status_code == 200

    created = created_response.json()

    report_id = int(
        created["report_id"].replace(
            "CV-",
            "",
        )
    )

    reviewer_response = client.post(
        "/auth/reviewers",
        headers=admin_auth_headers,
        json={
            "username": (
                "assignment_reviewer"
            ),
            "password": (
                "AssignmentTest123!"
            ),
            "role": "reviewer",
        },
    )

    assert (
        reviewer_response.status_code
        == 201
    )

    reviewer = reviewer_response.json()

    response = client.patch(
        f"/reports/{report_id}/assign",
        headers=admin_auth_headers,
        json={
            "reviewer_id": reviewer["id"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "assigned"

    assert (
        data["assigned_reviewer"]["id"]
        == reviewer["id"]
    )

    assert (
        data[
            "assigned_reviewer"
        ]["username"]
        == "assignment_reviewer"
    )
def test_reviewer_cannot_assign_report(
    client,
    auth_headers,
):
    response = client.patch(
        "/reports/1/assign",
        headers=auth_headers,
        json={
            "reviewer_id": 1,
        },
    )

    assert response.status_code == 403


def test_assign_unknown_reviewer_returns_404(
    client,
    admin_auth_headers,
):
    created = client.post(
        "/reports/",
        json={
            "platform": "Instagram",
            "url": (
                "https://example.com/"
                "assign-002"
            ),
            "reason": (
                "potential_child_exposure"
            ),
            "description": (
                "Assignment test."
            ),
        },
    ).json()

    report_id = int(
        created["report_id"].replace(
            "CV-",
            "",
        )
    )

    response = client.patch(
        f"/reports/{report_id}/assign",
        headers=admin_auth_headers,
        json={
            "reviewer_id": 999999,
        },
    )

    assert response.status_code == 404
def login_reviewer(
    client,
    username,
    password,
):
    response = client.post(
        "/auth/login",
        data={
            "username": username,
            "password": password,
        },
    )

    assert response.status_code == 200

    token = response.json()[
        "access_token"
    ]

    return {
        "Authorization": (
            f"Bearer {token}"
        ),
    }


def test_reviewer_claims_unassigned_report(
    client,
    admin_auth_headers,
):
    reviewer_response = client.post(
        "/auth/reviewers",
        headers=admin_auth_headers,
        json={
            "username": "claim_reviewer",
            "password": "ClaimTest123!",
            "role": "reviewer",
        },
    )

    assert reviewer_response.status_code == 201

    reviewer = reviewer_response.json()

    reviewer_headers = login_reviewer(
        client,
        "claim_reviewer",
        "ClaimTest123!",
    )

    created = client.post(
        "/reports/",
        json={
            "platform": "Instagram",
            "url": (
                "https://example.com/"
                "claim-test"
            ),
            "reason": (
                "potential_child_exposure"
            ),
            "description": (
                "Report for assignment claim test."
            ),
        },
    ).json()

    report_id = int(
        created["report_id"].replace(
            "CV-",
            "",
        )
    )

    response = client.patch(
        f"/reports/{report_id}/review",
        headers=reviewer_headers,
        json={
            "new_status": "under_review",
            "decision": "review_started",
            "notes": (
                "Reviewer claimed report."
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["report"][
            "assigned_reviewer_id"
        ]
        == reviewer["id"]
    )


def test_reviewer_cannot_review_report_assigned_to_another(
    client,
    admin_auth_headers,
):
    reviewer_a_response = client.post(
        "/auth/reviewers",
        headers=admin_auth_headers,
        json={
            "username": "reviewer_a",
            "password": "ReviewerA123!",
            "role": "reviewer",
        },
    )

    assert reviewer_a_response.status_code == 201

    reviewer_a = (
        reviewer_a_response.json()
    )

    reviewer_b_response = client.post(
        "/auth/reviewers",
        headers=admin_auth_headers,
        json={
            "username": "reviewer_b",
            "password": "ReviewerB123!",
            "role": "reviewer",
        },
    )

    assert reviewer_b_response.status_code == 201

    reviewer_b_headers = login_reviewer(
        client,
        "reviewer_b",
        "ReviewerB123!",
    )

    created = client.post(
        "/reports/",
        json={
            "platform": "Facebook",
            "url": (
                "https://example.com/"
                "assignment-access-test"
            ),
            "reason": (
                "potential_child_exposure"
            ),
            "description": (
                "Report assigned to reviewer A."
            ),
        },
    ).json()

    report_id = int(
        created["report_id"].replace(
            "CV-",
            "",
        )
    )

    assigned = client.patch(
        f"/reports/{report_id}/assign",
        headers=admin_auth_headers,
        json={
            "reviewer_id": (
                reviewer_a["id"]
            ),
        },
    )

    assert assigned.status_code == 200

    response = client.patch(
        f"/reports/{report_id}/review",
        headers=reviewer_b_headers,
        json={
            "new_status": "under_review",
            "decision": "review_started",
            "notes": (
                "Reviewer B should "
                "not access this case."
            ),
        },
    )

    assert response.status_code == 403

    assert (
        response.json()["detail"]
        == (
            "This report is assigned "
            "to another reviewer."
        )
    )