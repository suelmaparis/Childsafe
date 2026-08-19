from app.services.ai_risk_assessment import AIRiskAssessment


def test_create_report_with_ai_assessment(
    client,
    monkeypatch,
):
    """
    A report should be created with both the deterministic
    assessment and the mocked secondary AI assessment.

    No real OpenAI API request is made.
    """

    def fake_ai_assessment(
        reason: str,
        description: str,
    ):
        return AIRiskAssessment(
            level="high",
            score=75,
            reasons=[
                "Public child exposure.",
                "Location information may be disclosed.",
            ],
        )

    monkeypatch.setattr(
        "app.api.reports.assess_risk_with_ai",
        fake_ai_assessment,
    )

    response = client.post(
        "/reports/",
        json={
            "platform": "Instagram",
            "url": "https://example.com/test-api-001",
            "reason": "potential_child_exposure",
            "description": (
                "A public social media post shows a child "
                "and includes information that could reveal "
                "where the child regularly spends time."
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "received"
    assert data["report"]["risk_level"] == "medium"
    assert data["report"]["risk_score"] == 20

    assert (
        data["report"]["ai_assessment"]["level"]
        == "high"
    )
    assert (
        data["report"]["ai_assessment"]["score"]
        == 75
    )

    assert (
        data["report"]["risk_comparison"]["relationship"]
        == "ai_higher"
    )
    assert (
        data["report"]["risk_comparison"]["needs_attention"]
        is True
    )


def test_create_report_when_ai_is_unavailable(
    client,
    monkeypatch,
):
    """
    AI failure must not prevent a report from being created.
    """

    def fake_ai_failure(
        reason: str,
        description: str,
    ):
        raise RuntimeError(
            "Simulated AI failure."
        )

    monkeypatch.setattr(
        "app.api.reports.assess_risk_with_ai",
        fake_ai_failure,
    )

    response = client.post(
        "/reports/",
        json={
            "platform": "Instagram",
            "url": "https://example.com/test-api-002",
            "reason": "potential_child_exposure",
            "description": (
                "A public post containing a child."
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "received"

    assert data["report"]["ai_assessment"] == {
        "status": "unavailable",
    }

    assert data["report"]["risk_comparison"] == {
        "status": "unavailable",
    }


def test_created_report_can_be_retrieved(
    client,
    monkeypatch,
):
    """
    A newly created report should be persisted in the
    isolated test database and retrievable through the API.
    """

    def fake_ai_failure(
        reason: str,
        description: str,
    ):
        raise RuntimeError(
            "Simulated AI failure."
        )

    monkeypatch.setattr(
        "app.api.reports.assess_risk_with_ai",
        fake_ai_failure,
    )

    create_response = client.post(
        "/reports/",
        json={
            "platform": "Instagram",
            "url": "https://example.com/test-api-003",
            "reason": "potential_child_exposure",
            "description": "API persistence test.",
        },
    )

    assert create_response.status_code == 200

    created = create_response.json()

    report_id = int(
        created["report_id"].replace(
            "CV-",
            "",
        )
    )

    get_response = client.get(
        f"/reports/{report_id}"
    )

    assert get_response.status_code == 200

    report = get_response.json()

    assert report["report_id"] == created["report_id"]
    assert report["platform"] == "Instagram"
    assert report["review_status"] == "pending"
    assert report["risk_score"] == 20
    
    def test_root_endpoint(client):
        response = client.get("/")

        assert response.status_code == 200

        assert response.json() == {
            "message": "ChildSafe API",
            "status": "online",
    }


def test_report_not_found_returns_404(client):
    response = client.get(
        "/reports/999999"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Report not found."
    }

def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "message": "ChildSafe API",
        "status": "online",
    }

def test_complete_report_review_workflow(
    client,
    monkeypatch,
    auth_headers,
):
    """
    Test the complete ChildSafe report and human-review workflow:

    create report
        -> pending
        -> review queue
        -> under_review
        -> reviewed
        -> confirmed
        -> review history
        -> audit

    Also verifies that invalid workflow transitions are blocked.
    """

    from app.services.ai_risk_assessment import AIRiskAssessment

    # ---------------------------------------------------------
    # Mock AI
    # ---------------------------------------------------------

    def fake_ai_assessment(
        reason: str,
        description: str,
    ):
        return AIRiskAssessment(
            level="high",
            score=75,
            reasons=[
                "Public child exposure.",
                "Location information may be disclosed.",
            ],
        )

    monkeypatch.setattr(
        "app.api.reports.assess_risk_with_ai",
        fake_ai_assessment,
    )

    # ---------------------------------------------------------
    # 1. Create report
    # ---------------------------------------------------------

    response = client.post(
        "/reports/",
        json={
            "platform": "Instagram",
            "url": "https://example.com/workflow-test",
            "reason": "potential_child_exposure",
            "description": (
                "A public social media post shows a child "
                "and includes information that could reveal "
                "where the child regularly spends time."
            ),
        },
    )

    assert response.status_code == 200

    created = response.json()

    assert created["status"] == "received"
    assert created["report"]["review_status"] == "pending"

    report_id = int(
        created["report_id"].replace(
            "CV-",
            "",
        )
    )

    # ---------------------------------------------------------
    # 2. Report should appear in review queue
    # ---------------------------------------------------------

    response = client.get(
        "/reports/review-queue"
    )

    assert response.status_code == 200

    queue = response.json()

    assert len(queue) == 1

    assert (
        queue[0]["report_id"]
        == created["report_id"]
    )

    assert (
        queue[0]["queue_priority"]
        == "urgent"
    )

    assert (
        queue[0]["queue_priority_score"]
        == 900
    )

    # ---------------------------------------------------------
    # 3. Invalid pending -> confirmed transition
    # ---------------------------------------------------------

    response = client.patch(
        f"/reports/{report_id}/review",
        headers=auth_headers,
        json={
            "new_status": "confirmed",
            "decision": "invalid_direct_confirmation",
            "notes": (
                "This transition should be rejected."
            ),
            
        },
    )

    assert response.status_code == 409

    # Verify failed transition did not change the report.
    response = client.get(
        f"/reports/{report_id}"
    )

    assert response.status_code == 200
    assert (
        response.json()["review_status"]
        == "pending"
    )

    # ---------------------------------------------------------
    # 4. pending -> under_review
    # ---------------------------------------------------------

    response = client.patch(
        f"/reports/{report_id}/review",
        headers=auth_headers,
        json={
            "new_status": "under_review",
            "decision": "manual_review_started",
            "notes": "Human review started.",
           
        },
    )

    assert response.status_code == 200

    assert (
        response.json()["report"]["review_status"]
        == "under_review"
    )

    # ---------------------------------------------------------
    # 5. under_review -> reviewed
    # ---------------------------------------------------------

    response = client.patch(
        f"/reports/{report_id}/review",
        headers=auth_headers,
        json={
            "new_status": "reviewed",
            "decision": "manual_review_completed",
            "notes": "Human review completed.",
            
        },
    )

    assert response.status_code == 200

    assert (
        response.json()["report"]["review_status"]
        == "reviewed"
    )

    # ---------------------------------------------------------
    # 6. reviewed -> confirmed
    # ---------------------------------------------------------

    response = client.patch(
        f"/reports/{report_id}/review",
        headers=auth_headers,
        json={
            "new_status": "confirmed",
            "decision": "confirmed_child_safety_concern",
            "notes": (
                "Human reviewer confirmed the concern."
            ),
            
        },
    )

    assert response.status_code == 200

    assert (
        response.json()["report"]["review_status"]
        == "confirmed"
    )

    # ---------------------------------------------------------
    # 7. Final decision cannot be changed
    # ---------------------------------------------------------

    response = client.patch(
        f"/reports/{report_id}/review",
        headers=auth_headers,
        json={
            "new_status": "dismissed",
            "decision": "invalid_final_change",
            "notes": (
                "Final decisions must not be changed."
            ),
           
        },
    )

    assert response.status_code == 409

    # ---------------------------------------------------------
    # 8. Review history
    # ---------------------------------------------------------

    response = client.get(
        f"/reports/{report_id}/reviews"
    )

    assert response.status_code == 200

    reviews = response.json()

    # Invalid transitions must not create history records.
    assert len(reviews) == 3

    assert [
        review["new_status"]
        for review in reviews
    ] == [
        "under_review",
        "reviewed",
        "confirmed",
    ]

    # ---------------------------------------------------------
    # 9. Confirmed report must leave pending queue
    # ---------------------------------------------------------

    response = client.get(
        "/reports/review-queue"
    )

    assert response.status_code == 200

    queue = response.json()

    assert all(
        item["report_id"]
        != created["report_id"]
        for item in queue
    )

    # ---------------------------------------------------------
    # 10. Audit
    # ---------------------------------------------------------

    response = client.get(
        f"/reports/{report_id}/audit"
    )

    assert response.status_code == 200

    audit = response.json()

    assert (
        audit["report_id"]
        == created["report_id"]
    )

    assert (
        audit["deterministic_assessment"]["level"]
        == "medium"
    )

    assert (
        audit["deterministic_assessment"]["score"]
        == 20
    )

    assert (
        audit["ai_assessment"]["level"]
        == "high"
    )

    assert (
        audit["ai_assessment"]["score"]
        == 75
    )

    assert (
        audit["risk_comparison"]["relationship"]
        == "ai_higher"
    )

    assert (
        audit["risk_comparison"]["needs_attention"]
        is True
    )

    assert (
        audit["review"]["current_status"]
        == "confirmed"
    )

    assert (
        audit["review"]["review_count"]
        == 3
    )

    assert (
        audit["queue_priority"]["active"]
        is False
    )

    assert (
        audit["queue_priority"]["priority"]
        == "urgent"
    )

    assert (
        audit["queue_priority"]["priority_score"]
        == 900
    )


def test_ai_analysis_is_persisted(
    client,
    monkeypatch,
    db_session,
):
    """
    A successful AI assessment must be persisted in
    report_ai_analyses and linked to the created report.
    """

    import json

    from app.models.report_ai_analysis import ReportAIAnalysis
    from app.services.ai_risk_assessment import AIRiskAssessment

    def fake_ai_assessment(
        reason: str,
        description: str,
    ):
        return AIRiskAssessment(
            level="high",
            score=75,
            reasons=[
                "Public child exposure.",
                "Location information may be disclosed.",
            ],
        )

    monkeypatch.setattr(
        "app.api.reports.assess_risk_with_ai",
        fake_ai_assessment,
    )

    response = client.post(
        "/reports/",
        json={
            "platform": "Instagram",
            "url": "https://example.com/ai-persistence-test",
            "reason": "potential_child_exposure",
            "description": (
                "A public post shows a child and may reveal "
                "where the child regularly spends time."
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    report_id = int(
        data["report_id"].replace(
            "CV-",
            "",
        )
    )

    analyses = (
        db_session.query(ReportAIAnalysis)
        .filter(
            ReportAIAnalysis.report_id
            == report_id
        )
        .all()
    )

    assert len(analyses) == 1

    analysis = analyses[0]

    assert analysis.report_id == report_id
    assert analysis.model == "gpt-5-mini"
    assert analysis.level == "high"
    assert analysis.score == 75

    reasons = json.loads(
        analysis.reasons
    )

    assert reasons == [
        "Public child exposure.",
        "Location information may be disclosed.",
    ]

def test_report_creation_rolls_back_on_database_failure(
    client,
    monkeypatch,
    db_session,
):
    """
    If the database transaction fails while creating a report,
    neither the Report nor its ReportAIAnalysis may remain
    persisted.

    This protects transaction atomicity.
    """

    from app.models.report import Report
    from app.models.report_ai_analysis import ReportAIAnalysis
    from app.services.ai_risk_assessment import AIRiskAssessment

    # ---------------------------------------------------------
    # Mock AI
    # ---------------------------------------------------------

    def fake_ai_assessment(
        reason: str,
        description: str,
    ):
        return AIRiskAssessment(
            level="high",
            score=75,
            reasons=[
                "Public child exposure.",
                "Location information may be disclosed.",
            ],
        )

    monkeypatch.setattr(
        "app.api.reports.assess_risk_with_ai",
        fake_ai_assessment,
    )

    # ---------------------------------------------------------
    # Force the request database session to fail on commit
    # ---------------------------------------------------------

    from app.api import reports as reports_api

    original_get_db = reports_api.get_db

    def failing_get_db():
        db = db_session

        original_commit = db.commit

        def failing_commit():
            raise RuntimeError(
                "Simulated database commit failure."
            )

        db.commit = failing_commit

        try:
            yield db
        finally:
            # Restore commit so we can inspect the database
            # normally after the request.
            db.commit = original_commit

    # FastAPI dependency override must target the dependency
    # object registered by the route.
    from app.main import app

    previous_override = app.dependency_overrides.get(
    original_get_db
    )

    app.dependency_overrides[
        original_get_db
    ] = failing_get_db

    try:
        response = client.post(
            "/reports/",
            json={
                "platform": "Instagram",
                "url": (
                    "https://example.com/"
                    "atomicity-test"
                ),
                "reason": (
                    "potential_child_exposure"
                ),
                "description": (
                    "A public post shows a child "
                    "and may reveal regular location "
                    "information."
                ),
            },
        )

        assert response.status_code == 500

        assert response.json() == {
            "detail": "Unable to save report."
        }

    finally:
        # Restore the test database dependency override
        # instead of deleting it.
        if previous_override is not None:
            app.dependency_overrides[
                original_get_db
            ] = previous_override
        else:
            app.dependency_overrides.pop(
                original_get_db,
                None,
            )
    # ---------------------------------------------------------
    # Verify rollback
    # ---------------------------------------------------------

    reports = (
        db_session.query(Report)
        .all()
    )

    ai_analyses = (
        db_session.query(
            ReportAIAnalysis
        )
        .all()
    )

    assert reports == []
    assert ai_analyses == []

def test_review_without_token_returns_401(
    client,
    monkeypatch,
):
    """
    Reviewing a report without authentication
    must be rejected.
    """

    from app.services.ai_risk_assessment import AIRiskAssessment

    def fake_ai_assessment(
        reason: str,
        description: str,
    ):
        return AIRiskAssessment(
            level="medium",
            score=20,
            reasons=[
                "Test assessment.",
            ],
        )

    monkeypatch.setattr(
        "app.api.reports.assess_risk_with_ai",
        fake_ai_assessment,
    )

    response = client.post(
        "/reports/",
        json={
            "platform": "Instagram",
            "url": "https://example.com/auth-test-001",
            "reason": "potential_child_exposure",
            "description": "Authentication test report.",
        },
    )

    assert response.status_code == 200

    report_id = int(
        response.json()["report_id"].replace(
            "CV-",
            "",
        )
    )

    response = client.patch(
        f"/reports/{report_id}/review",
        json={
            "new_status": "under_review",
            "decision": "manual_review_started",
            "notes": "This request has no token.",
        },
    )

    assert response.status_code == 401

def test_authenticated_reviewer_identity_is_saved_from_token(
    client,
    monkeypatch,
    auth_headers,
):
    """
    The reviewer identity must come from the authenticated
    JWT, not from client-provided review data.
    """

    from app.services.ai_risk_assessment import AIRiskAssessment

    def fake_ai_assessment(
        reason: str,
        description: str,
    ):
        return AIRiskAssessment(
            level="medium",
            score=20,
            reasons=[
                "Test assessment.",
            ],
        )

    monkeypatch.setattr(
        "app.api.reports.assess_risk_with_ai",
        fake_ai_assessment,
    )

    response = client.post(
        "/reports/",
        json={
            "platform": "Instagram",
            "url": "https://example.com/auth-test-002",
            "reason": "potential_child_exposure",
            "description": "Authenticated reviewer identity test.",
        },
    )

    assert response.status_code == 200

    report_id = int(
        response.json()["report_id"].replace(
            "CV-",
            "",
        )
    )

    response = client.patch(
        f"/reports/{report_id}/review",
        headers=auth_headers,
        json={
            "new_status": "under_review",
            "decision": "manual_review_started",
            "notes": "Authenticated review test.",
        },
    )

    assert response.status_code == 200

    response = client.get(
        f"/reports/{report_id}/reviews"
    )

    assert response.status_code == 200

    reviews = response.json()

    assert len(reviews) == 1

    assert (
        reviews[0]["reviewer"]
        == "test_reviewer"
    )

def test_regular_reviewer_cannot_list_reviewers(
    client,
    auth_headers,
):
    response = client.get(
        "/auth/reviewers",
        headers=auth_headers,
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail": "Insufficient permissions."
    }


def test_admin_can_list_reviewers(
    client,
    reviewer_user,
    admin_auth_headers,
):
    response = client.get(
        "/auth/reviewers",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200

    reviewers = response.json()

    usernames = {
        reviewer["username"]
        for reviewer in reviewers
    }

    assert "test_admin" in usernames
    assert "test_reviewer" in usernames

    for reviewer in reviewers:
        assert "password_hash" not in reviewer


def test_admin_can_create_reviewer(
    client,
    admin_auth_headers,
):
    response = client.post(
        "/auth/reviewers",
        headers=admin_auth_headers,
        json={
            "username": "new_reviewer",
            "password": "NewReviewerPassword123!",
            "role": "reviewer",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "new_reviewer"
    assert data["role"] == "reviewer"
    assert data["is_active"] is True

    assert "password" not in data
    assert "password_hash" not in data


def test_regular_reviewer_cannot_create_reviewer(
    client,
    auth_headers,
):
    response = client.post(
        "/auth/reviewers",
        headers=auth_headers,
        json={
            "username": "forbidden_reviewer",
            "password": "ForbiddenPassword123!",
            "role": "reviewer",
        },
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail": "Insufficient permissions."
    }


def test_duplicate_reviewer_username_returns_409(
    client,
    reviewer_user,
    admin_auth_headers,
):
    response = client.post(
        "/auth/reviewers",
        headers=admin_auth_headers,
        json={
            "username": "test_reviewer",
            "password": "AnotherPassword123!",
            "role": "reviewer",
        },
    )

    assert response.status_code == 409

    assert response.json() == {
        "detail": "Reviewer username already exists."
    }


def test_invalid_reviewer_role_returns_422(
    client,
    admin_auth_headers,
):
    response = client.post(
        "/auth/reviewers",
        headers=admin_auth_headers,
        json={
            "username": "invalid_role_user",
            "password": "InvalidRolePassword123!",
            "role": "superuser",
        },
    )

    assert response.status_code == 422

    assert response.json() == {
        "detail": "Invalid reviewer role."
    }

def test_admin_can_deactivate_reviewer(
    client,
    reviewer_user,
    admin_auth_headers,
):
    response = client.patch(
        f"/auth/reviewers/{reviewer_user.id}/status",
        headers=admin_auth_headers,
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "test_reviewer"
    assert data["is_active"] is False


def test_regular_reviewer_cannot_change_account_status(
    client,
    reviewer_user,
    auth_headers,
):
    response = client.patch(
        f"/auth/reviewers/{reviewer_user.id}/status",
        headers=auth_headers,
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail": "Insufficient permissions."
    }


def test_deactivated_reviewer_cannot_use_auth_me(
    client,
    reviewer_user,
    auth_headers,
    admin_auth_headers,
):
    response = client.patch(
        f"/auth/reviewers/{reviewer_user.id}/status",
        headers=admin_auth_headers,
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 200

    response = client.get(
        "/auth/me",
        headers=auth_headers,
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail": "Reviewer account is inactive."
    }


def test_admin_can_reactivate_reviewer(
    client,
    reviewer_user,
    auth_headers,
    admin_auth_headers,
):
    # Deactivate.
    response = client.patch(
        f"/auth/reviewers/{reviewer_user.id}/status",
        headers=admin_auth_headers,
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 200

    # Reactivate.
    response = client.patch(
        f"/auth/reviewers/{reviewer_user.id}/status",
        headers=admin_auth_headers,
        json={
            "is_active": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is True

    # Original token becomes usable again because
    # account status is checked against the database.
    response = client.get(
        "/auth/me",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["username"] == "test_reviewer"


def test_admin_cannot_deactivate_own_account(
    client,
    admin_user,
    admin_auth_headers,
):
    response = client.patch(
        f"/auth/reviewers/{admin_user.id}/status",
        headers=admin_auth_headers,
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 409

    assert response.json() == {
        "detail": (
            "Administrator cannot change "
            "their own active status."
        )
    }

def test_reviewer_creation_creates_audit_log(
    client,
    admin_auth_headers,
    db_session,
):
    from app.models.reviewer import Reviewer
    from app.models.reviewer_audit_log import ReviewerAuditLog

    response = client.post(
        "/auth/reviewers",
        headers=admin_auth_headers,
        json={
            "username": "audit_created_user",
            "password": "AuditCreatedPassword123!",
            "role": "reviewer",
        },
    )

    assert response.status_code == 201

    reviewer = (
        db_session.query(Reviewer)
        .filter(
            Reviewer.username == "audit_created_user"
        )
        .first()
    )

    assert reviewer is not None

    audit_logs = (
        db_session.query(ReviewerAuditLog)
        .filter(
            ReviewerAuditLog.target_reviewer_id
            == reviewer.id
        )
        .all()
    )

    assert len(audit_logs) == 1

    audit_log = audit_logs[0]

    assert audit_log.action == "reviewer_created"
    assert audit_log.target_reviewer_id == reviewer.id
    assert audit_log.actor_reviewer_id != reviewer.id


def test_reviewer_deactivation_creates_audit_log(
    client,
    reviewer_user,
    admin_user,
    admin_auth_headers,
    db_session,
):
    from app.models.reviewer_audit_log import ReviewerAuditLog

    response = client.patch(
        f"/auth/reviewers/{reviewer_user.id}/status",
        headers=admin_auth_headers,
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 200

    audit_logs = (
        db_session.query(ReviewerAuditLog)
        .filter(
            ReviewerAuditLog.target_reviewer_id
            == reviewer_user.id
        )
        .all()
    )

    assert len(audit_logs) == 1

    audit_log = audit_logs[0]

    assert audit_log.action == "reviewer_deactivated"
    assert audit_log.actor_reviewer_id == admin_user.id
    assert audit_log.target_reviewer_id == reviewer_user.id


def test_reviewer_reactivation_creates_audit_log(
    client,
    reviewer_user,
    admin_user,
    admin_auth_headers,
    db_session,
):
    from app.models.reviewer_audit_log import ReviewerAuditLog

    # First deactivate.
    response = client.patch(
        f"/auth/reviewers/{reviewer_user.id}/status",
        headers=admin_auth_headers,
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 200

    # Then reactivate.
    response = client.patch(
        f"/auth/reviewers/{reviewer_user.id}/status",
        headers=admin_auth_headers,
        json={
            "is_active": True,
        },
    )

    assert response.status_code == 200

    audit_logs = (
        db_session.query(ReviewerAuditLog)
        .filter(
            ReviewerAuditLog.target_reviewer_id
            == reviewer_user.id
        )
        .order_by(
            ReviewerAuditLog.created_at.asc()
        )
        .all()
    )

    assert len(audit_logs) == 2

    assert audit_logs[0].action == "reviewer_deactivated"
    assert audit_logs[1].action == "reviewer_reactivated"

    assert (
        audit_logs[1].actor_reviewer_id
        == admin_user.id
    )

    assert (
        audit_logs[1].target_reviewer_id
        == reviewer_user.id
    )

def test_admin_can_list_reviewer_audit_logs(
    client,
    reviewer_user,
    admin_user,
    admin_auth_headers,
):
    # Generate an administrative audit event.
    response = client.patch(
        f"/auth/reviewers/{reviewer_user.id}/status",
        headers=admin_auth_headers,
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 200

    response = client.get(
        "/auth/audit-logs",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200

    audit_data = response.json()
    audit_logs = audit_data["items"]   

    audit_log = audit_logs[0]

    assert (
        audit_log["actor_reviewer_id"]
        == admin_user.id
    )

    assert (
        audit_log["target_reviewer_id"]
        == reviewer_user.id
    )

    assert (
        audit_log["action"]
        == "reviewer_deactivated"
    )

    assert "details" in audit_log
    assert "created_at" in audit_log


def test_regular_reviewer_cannot_list_audit_logs(
    client,
    auth_headers,
):
    response = client.get(
        "/auth/audit-logs",
        headers=auth_headers,
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail": "Insufficient permissions."
    }

def test_audit_logs_can_be_filtered_by_action(
    client,
    reviewer_user,
    admin_auth_headers,
):
    # Generate deactivation.
    response = client.patch(
        f"/auth/reviewers/{reviewer_user.id}/status",
        headers=admin_auth_headers,
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 200

    # Generate reactivation.
    response = client.patch(
        f"/auth/reviewers/{reviewer_user.id}/status",
        headers=admin_auth_headers,
        json={
            "is_active": True,
        },
    )

    assert response.status_code == 200

    response = client.get(
        "/auth/audit-logs",
        headers=admin_auth_headers,
        params={
            "action": "reviewer_reactivated",
        },
    )

    assert response.status_code == 200

    audit_data = response.json()
    audit_logs = audit_data["items"]
    assert (
        audit_logs[0]["action"]
        == "reviewer_reactivated"
    )


def test_audit_logs_can_be_filtered_by_actor(
    client,
    reviewer_user,
    admin_user,
    admin_auth_headers,
):
    response = client.patch(
        f"/auth/reviewers/{reviewer_user.id}/status",
        headers=admin_auth_headers,
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 200

    response = client.get(
        "/auth/audit-logs",
        headers=admin_auth_headers,
        params={
            "actor_reviewer_id": admin_user.id,
        },
    )

    assert response.status_code == 200

    audit_data = response.json()
    audit_logs = audit_data["items"]

    assert len(audit_logs) == 1

    assert (
        audit_logs[0]["actor_reviewer_id"]
        == admin_user.id
    )


def test_audit_logs_can_be_filtered_by_target(
    client,
    reviewer_user,
    admin_auth_headers,
):
    response = client.patch(
        f"/auth/reviewers/{reviewer_user.id}/status",
        headers=admin_auth_headers,
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 200

    response = client.get(
        "/auth/audit-logs",
        headers=admin_auth_headers,
        params={
            "target_reviewer_id": reviewer_user.id,
        },
    )

    assert response.status_code == 200

    audit_data = response.json()
    audit_logs = audit_data["items"]

    assert (
        audit_logs[0]["target_reviewer_id"]
        == reviewer_user.id
    )


def test_audit_log_filters_can_be_combined(
    client,
    reviewer_user,
    admin_user,
    admin_auth_headers,
):
    # Generate deactivation.
    response = client.patch(
        f"/auth/reviewers/{reviewer_user.id}/status",
        headers=admin_auth_headers,
        json={
            "is_active": False,
        },
    )

    assert response.status_code == 200

    # Generate reactivation.
    response = client.patch(
        f"/auth/reviewers/{reviewer_user.id}/status",
        headers=admin_auth_headers,
        json={
            "is_active": True,
        },
    )

    assert response.status_code == 200

    response = client.get(
        "/auth/audit-logs",
        headers=admin_auth_headers,
        params={
            "action": "reviewer_reactivated",
            "actor_reviewer_id": admin_user.id,
            "target_reviewer_id": reviewer_user.id,
        },
    )

    assert response.status_code == 200

    audit_data = response.json()
    audit_logs = audit_data["items"]

    audit_log = audit_logs[0]

    assert (
        audit_log["action"]
        == "reviewer_reactivated"
    )

    assert (
        audit_log["actor_reviewer_id"]
        == admin_user.id
    )

    assert (
        audit_log["target_reviewer_id"]
        == reviewer_user.id
    )

def test_audit_logs_limit_pagination(
    client,
    reviewer_user,
    admin_auth_headers,
):
    # Generate two audit events.
    response = client.patch(
        f"/auth/reviewers/{reviewer_user.id}/status",
        headers=admin_auth_headers,
        json={"is_active": False},
    )
    assert response.status_code == 200

    response = client.patch(
        f"/auth/reviewers/{reviewer_user.id}/status",
        headers=admin_auth_headers,
        json={"is_active": True},
    )
    assert response.status_code == 200

    response = client.get(
        "/auth/audit-logs",
        headers=admin_auth_headers,
        params={"limit": 1},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert data["limit"] == 1
    assert data["offset"] == 0
    assert len(data["items"]) == 1


def test_audit_logs_offset_pagination(
    client,
    reviewer_user,
    admin_auth_headers,
):
    # Generate two audit events.
    response = client.patch(
        f"/auth/reviewers/{reviewer_user.id}/status",
        headers=admin_auth_headers,
        json={"is_active": False},
    )
    assert response.status_code == 200

    response = client.patch(
        f"/auth/reviewers/{reviewer_user.id}/status",
        headers=admin_auth_headers,
        json={"is_active": True},
    )
    assert response.status_code == 200

    # Without offset, newest event is reactivation.
    response = client.get(
        "/auth/audit-logs",
        headers=admin_auth_headers,
        params={
            "limit": 1,
            "offset": 0,
        },
    )

    assert response.status_code == 200

    first_page = response.json()

    assert len(first_page["items"]) == 1
    assert (
        first_page["items"][0]["action"]
        == "reviewer_reactivated"
    )

    # Offset 1 should return the older deactivation event.
    response = client.get(
        "/auth/audit-logs",
        headers=admin_auth_headers,
        params={
            "limit": 1,
            "offset": 1,
        },
    )

    assert response.status_code == 200

    second_page = response.json()

    assert second_page["total"] == 2
    assert second_page["limit"] == 1
    assert second_page["offset"] == 1
    assert len(second_page["items"]) == 1

    assert (
        second_page["items"][0]["action"]
        == "reviewer_deactivated"
    )


def test_audit_logs_reject_limit_above_100(
    client,
    admin_auth_headers,
):
    response = client.get(
        "/auth/audit-logs",
        headers=admin_auth_headers,
        params={
            "limit": 101,
        },
    )

    assert response.status_code == 422

    assert response.json() == {
        "detail": "limit must be between 1 and 100."
    }

def test_regular_reviewer_cannot_access_admin_metrics(
    client,
    auth_headers,
):
    response = client.get(
        "/reports/admin/metrics",
        headers=auth_headers,
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail": "Insufficient permissions."
    }


def test_admin_can_access_admin_metrics(
    client,
    admin_auth_headers,
):
    response = client.get(
        "/reports/admin/metrics",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_reports" in data
    assert "risk_distribution" in data
    assert "urgent_pending" in data


def test_senior_reviewer_can_access_admin_metrics(
    client,
    db_session,
):
    from app.models.reviewer import Reviewer
    from app.services.auth import hash_password

    senior = Reviewer(
        username="test_senior",
        password_hash=hash_password(
            "SeniorPassword123!"
        ),
        role="senior_reviewer",
        is_active=True,
    )

    db_session.add(senior)
    db_session.commit()
    db_session.refresh(senior)

    response = client.post(
        "/auth/login",
        data={
            "username": "test_senior",
            "password": "SeniorPassword123!",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    response = client.get(
        "/reports/admin/metrics",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200


def test_admin_metrics_count_reports_correctly(
    client,
    monkeypatch,
    admin_auth_headers,
):
    from app.services.ai_risk_assessment import AIRiskAssessment

    def fake_ai_assessment(
        reason: str,
        description: str,
    ):
        return AIRiskAssessment(
            level="medium",
            score=20,
            reasons=[
                "Test assessment.",
            ],
        )

    monkeypatch.setattr(
        "app.api.reports.assess_risk_with_ai",
        fake_ai_assessment,
    )

    # Create two medium-risk reports.
    for index in range(2):
        response = client.post(
            "/reports/",
            json={
                "platform": "Instagram",
                "url": (
                    f"https://example.com/"
                    f"metrics-{index}"
                ),
                "reason": "potential_child_exposure",
                "description": (
                    "Metrics test report."
                ),
            },
        )

        assert response.status_code == 200

    response = client.get(
        "/reports/admin/metrics",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_reports"] == 2
    assert data["pending"] == 2

    assert (
        data["risk_distribution"]["medium"]
        == 2
    )


def test_admin_metrics_count_urgent_pending_correctly(
    client,
    monkeypatch,
    admin_auth_headers,
):
    from app.services.ai_risk_assessment import AIRiskAssessment

    def fake_ai_assessment(
        reason: str,
        description: str,
    ):
        return AIRiskAssessment(
            level="high",
            score=75,
            reasons=[
                "Significant AI risk signal.",
            ],
        )

    monkeypatch.setattr(
        "app.api.reports.assess_risk_with_ai",
        fake_ai_assessment,
    )

    response = client.post(
        "/reports/",
        json={
            "platform": "Instagram",
            "url": "https://example.com/urgent-metrics",
            "reason": "potential_child_exposure",
            "description": (
                "A public post shows a child "
                "and may reveal regular location information."
            ),
        },
    )

    assert response.status_code == 200

    response = client.get(
        "/reports/admin/metrics",
        headers=admin_auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_reports"] == 1
    assert data["pending"] == 1
    assert data["urgent_pending"] == 1