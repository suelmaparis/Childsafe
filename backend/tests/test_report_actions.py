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
                "report-action-test"
            ),
            "reason": (
                "potential_child_exposure"
            ),
            "description": (
                "Test report for "
                "report action workflow."
            ),
        },
    )

    assert response.status_code == 200

    return response.json()


def test_reviewer_can_create_internal_action(
    client,
    auth_headers,
):
    report = _create_report(
        client,
        auth_headers,
    )

    report_id = int(
        report["report_id"]
        .replace(
            "CV-",
            ""
        )
    )

    response = client.post(
        f"/reports/{report_id}/actions",
        headers=auth_headers,
        json={
            "action_type":
                "internal_escalation",
            "notes":
                "Needs senior review.",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert (
        data["report_id"]
        == report_id
    )

    assert (
        data["action_type"]
        == "internal_escalation"
    )

    assert data["status"] == "pending"


def test_external_action_requires_confirmed_or_escalated_report(
    client,
    admin_auth_headers,
):
    report = _create_report(
        client,
        admin_auth_headers,
    )

    report_id = int(
        report["report_id"]
        .replace(
            "CV-",
            ""
        )
    )

    response = client.post(
        f"/reports/{report_id}/actions",
        headers=admin_auth_headers,
        json={
            "action_type":
                "platform_report",
            "notes":
                "Report to platform.",
        },
    )

    assert response.status_code == 409


def test_reviewer_cannot_create_external_action(
    client,
    auth_headers,
):
    report = _create_report(
        client,
        auth_headers,
    )

    report_id = int(
        report["report_id"]
        .replace(
            "CV-",
            ""
        )
    )

    response = client.post(
        f"/reports/{report_id}/actions",
        headers=auth_headers,
        json={
            "action_type":
                "platform_report",
        },
    )

    assert response.status_code in {
        403,
        409,
    }


def test_can_list_report_actions(
    client,
    auth_headers,
):
    report = _create_report(
        client,
        auth_headers,
    )

    report_id = int(
        report["report_id"]
        .replace(
            "CV-",
            ""
        )
    )

    create_response = client.post(
        f"/reports/{report_id}/actions",
        headers=auth_headers,
        json={
            "action_type":
                "evidence_preservation",
            "notes":
                "Preserve metadata.",
        },
    )

    assert (
        create_response.status_code
        == 201
    )

    response = client.get(
        f"/reports/{report_id}/actions",
        headers=auth_headers,
    )

    assert response.status_code == 200

    actions = response.json()

    assert len(actions) >= 1

    assert (
        actions[-1]["action_type"]
        == "evidence_preservation"
    )

def test_admin_can_update_report_action(
    client,
    admin_auth_headers,
):
    report = _create_report(
        client,
        admin_auth_headers,
    )

    report_id = int(
        report["report_id"]
        .replace(
            "CV-",
            ""
        )
    )

    create_response = client.post(
        f"/reports/{report_id}/actions",
        headers=admin_auth_headers,
        json={
            "action_type":
                "internal_escalation",
            "notes":
                "Initial action.",
        },
    )

    assert (
        create_response.status_code
        == 201
    )

    action_id = (
        create_response.json()["id"]
    )

    start_response = client.patch(
        (
            f"/reports/{report_id}"
            f"/actions/{action_id}"
        ),
        headers=admin_auth_headers,
        json={
            "status":
                "in_progress",
            "notes":
                "Action started.",
            "external_reference":
                None,
        },
    )

    assert (
        start_response.status_code
        == 200
    )

    response = client.patch(
        (
            f"/reports/{report_id}"
            f"/actions/{action_id}"
        ),
        headers=admin_auth_headers,
        json={
            "status":
                "completed",
            "notes":
                "Action completed.",
            "external_reference":
                "TEST-REF-001",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"

    assert (
        data["external_reference"]
        == "TEST-REF-001"
    )

def test_report_actions_return_404_for_missing_report(
    client,
    auth_headers,
):
    response = client.get(
        "/reports/999999/actions",
        headers=auth_headers,
    )

    assert response.status_code == 404

def test_action_status_transition_pending_to_in_progress(
    client,
    admin_auth_headers,
):
    report = _create_report(
        client,
        admin_auth_headers,
    )

    report_id = int(
        report["report_id"].replace(
            "CV-",
            "",
        )
    )

    create_response = client.post(
        f"/reports/{report_id}/actions",
        headers=admin_auth_headers,
        json={
            "action_type":
                "internal_escalation",
            "notes":
                "Transition test.",
        },
    )

    assert create_response.status_code == 201

    action_id = (
        create_response.json()["id"]
    )

    response = client.patch(
        (
            f"/reports/{report_id}"
            f"/actions/{action_id}"
        ),
        headers=admin_auth_headers,
        json={
            "status": "in_progress",
            "notes": "In progress.",
            "external_reference": None,
        },
    )

    assert response.status_code == 200
    assert (
        response.json()["status"]
        == "in_progress"
    )


def test_action_status_transition_pending_to_cancelled(
    client,
    admin_auth_headers,
):
    report = _create_report(
        client,
        admin_auth_headers,
    )

    report_id = int(
        report["report_id"].replace(
            "CV-",
            "",
        )
    )

    create_response = client.post(
        f"/reports/{report_id}/actions",
        headers=admin_auth_headers,
        json={
            "action_type":
                "internal_escalation",
        },
    )

    action_id = (
        create_response.json()["id"]
    )

    response = client.patch(
        (
            f"/reports/{report_id}"
            f"/actions/{action_id}"
        ),
        headers=admin_auth_headers,
        json={
            "status": "cancelled",
            "notes": "Cancelled.",
            "external_reference": None,
        },
    )

    assert response.status_code == 200
    assert (
        response.json()["status"]
        == "cancelled"
    )


def test_action_status_transition_in_progress_to_completed(
    client,
    admin_auth_headers,
):
    report = _create_report(
        client,
        admin_auth_headers,
    )

    report_id = int(
        report["report_id"].replace(
            "CV-",
            "",
        )
    )

    create_response = client.post(
        f"/reports/{report_id}/actions",
        headers=admin_auth_headers,
        json={
            "action_type":
                "internal_escalation",
        },
    )

    action_id = (
        create_response.json()["id"]
    )

    first_update = client.patch(
        (
            f"/reports/{report_id}"
            f"/actions/{action_id}"
        ),
        headers=admin_auth_headers,
        json={
            "status": "in_progress",
            "notes": "Started.",
            "external_reference": None,
        },
    )

    assert first_update.status_code == 200

    response = client.patch(
        (
            f"/reports/{report_id}"
            f"/actions/{action_id}"
        ),
        headers=admin_auth_headers,
        json={
            "status": "completed",
            "notes": "Completed.",
            "external_reference":
                "TEST-COMPLETE-001",
        },
    )

    assert response.status_code == 200
    assert (
        response.json()["status"]
        == "completed"
    )


def test_completed_action_cannot_return_to_in_progress(
    client,
    admin_auth_headers,
):
    report = _create_report(
        client,
        admin_auth_headers,
    )

    report_id = int(
        report["report_id"].replace(
            "CV-",
            "",
        )
    )

    create_response = client.post(
        f"/reports/{report_id}/actions",
        headers=admin_auth_headers,
        json={
            "action_type":
                "internal_escalation",
        },
    )

    action_id = (
        create_response.json()["id"]
    )

    client.patch(
        (
            f"/reports/{report_id}"
            f"/actions/{action_id}"
        ),
        headers=admin_auth_headers,
        json={
            "status": "in_progress",
            "notes": None,
            "external_reference": None,
        },
    )

    client.patch(
        (
            f"/reports/{report_id}"
            f"/actions/{action_id}"
        ),
        headers=admin_auth_headers,
        json={
            "status": "completed",
            "notes": None,
            "external_reference": None,
        },
    )

    response = client.patch(
        (
            f"/reports/{report_id}"
            f"/actions/{action_id}"
        ),
        headers=admin_auth_headers,
        json={
            "status": "in_progress",
            "notes": None,
            "external_reference": None,
        },
    )

    assert response.status_code == 409


def test_cancelled_action_cannot_be_completed(
    client,
    admin_auth_headers,
):
    report = _create_report(
        client,
        admin_auth_headers,
    )

    report_id = int(
        report["report_id"].replace(
            "CV-",
            "",
        )
    )

    create_response = client.post(
        f"/reports/{report_id}/actions",
        headers=admin_auth_headers,
        json={
            "action_type":
                "internal_escalation",
        },
    )

    action_id = (
        create_response.json()["id"]
    )

    cancel_response = client.patch(
        (
            f"/reports/{report_id}"
            f"/actions/{action_id}"
        ),
        headers=admin_auth_headers,
        json={
            "status": "cancelled",
            "notes": None,
            "external_reference": None,
        },
    )

    assert cancel_response.status_code == 200

    response = client.patch(
        (
            f"/reports/{report_id}"
            f"/actions/{action_id}"
        ),
        headers=admin_auth_headers,
        json={
            "status": "completed",
            "notes": None,
            "external_reference": None,
        },
    )

    assert response.status_code == 409
def test_external_action_sets_submitted_at_when_started(
    client,
    admin_auth_headers,
):
    report = _create_report(
        client,
        admin_auth_headers,
    )

    report_id = int(
        report["report_id"].replace(
            "CV-",
            "",
        )
    )

    # O report precisa estar num estado que permita ação externa.
    client.patch(
        f"/reports/{report_id}/review",
        headers=admin_auth_headers,
        json={
            "new_status": "under_review",
            "decision": "Start review.",
            "notes": "Testing external action.",
        },
    )

    client.patch(
        f"/reports/{report_id}/review",
        headers=admin_auth_headers,
        json={
            "new_status": "reviewed",
            "decision": "Reviewed.",
            "notes": "Ready for decision.",
        },
    )

    client.patch(
        f"/reports/{report_id}/review",
        headers=admin_auth_headers,
        json={
            "new_status": "confirmed",
            "decision": "Confirmed.",
            "notes": "External action allowed.",
        },
    )

    create_response = client.post(
        f"/reports/{report_id}/actions",
        headers=admin_auth_headers,
        json={
            "action_type":
                "platform_report",
            "platform":
                "Instagram",
            "destination":
                "Meta reporting channel",
            "notes":
                "Submit to platform.",
        },
    )

    assert create_response.status_code == 201

    action = create_response.json()

    assert action["submitted_at"] is None
    assert action["responded_at"] is None

    action_id = action["id"]

    response = client.patch(
        (
            f"/reports/{report_id}"
            f"/actions/{action_id}"
        ),
        headers=admin_auth_headers,
        json={
            "status":
                "in_progress",
            "notes":
                "Submitted to Meta.",
            "external_reference":
                "META-TEST-001",
            "platform":
                "Instagram",
            "destination":
                "Meta reporting channel",
            "external_result":
                None,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "in_progress"
    assert data["submitted_at"] is not None
    assert data["responded_at"] is None

    assert (
        data["external_reference"]
        == "META-TEST-001"
    )


def test_external_action_sets_responded_at_when_completed(
    client,
    admin_auth_headers,
):
    report = _create_report(
        client,
        admin_auth_headers,
    )

    report_id = int(
        report["report_id"].replace(
            "CV-",
            "",
        )
    )

    for new_status in [
        "under_review",
        "reviewed",
        "confirmed",
    ]:
        response = client.patch(
            f"/reports/{report_id}/review",
            headers=admin_auth_headers,
            json={
                "new_status":
                    new_status,
                "decision":
                    f"Move to {new_status}.",
                "notes":
                    "External workflow test.",
            },
        )

        assert response.status_code == 200

    create_response = client.post(
        f"/reports/{report_id}/actions",
        headers=admin_auth_headers,
        json={
            "action_type":
                "takedown_request",
            "platform":
                "Instagram",
            "destination":
                "Meta",
            "notes":
                "Request removal.",
        },
    )

    assert create_response.status_code == 201

    action_id = (
        create_response.json()["id"]
    )

    start_response = client.patch(
        (
            f"/reports/{report_id}"
            f"/actions/{action_id}"
        ),
        headers=admin_auth_headers,
        json={
            "status":
                "in_progress",
            "notes":
                "Request submitted.",
            "external_reference":
                "META-TAKEDOWN-001",
            "platform":
                "Instagram",
            "destination":
                "Meta",
            "external_result":
                None,
        },
    )

    assert start_response.status_code == 200
    assert (
        start_response.json()["submitted_at"]
        is not None
    )

    response = client.patch(
        (
            f"/reports/{report_id}"
            f"/actions/{action_id}"
        ),
        headers=admin_auth_headers,
        json={
            "status":
                "completed",
            "notes":
                "Platform responded.",
            "external_reference":
                "META-TAKEDOWN-001",
            "platform":
                "Instagram",
            "destination":
                "Meta",
            "external_result":
                "Content removed.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"
    assert data["submitted_at"] is not None
    assert data["responded_at"] is not None
    assert (
        data["external_result"]
        == "Content removed."
    )