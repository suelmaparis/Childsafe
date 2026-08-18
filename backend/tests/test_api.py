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
        json={
            "new_status": "confirmed",
            "decision": "invalid_direct_confirmation",
            "notes": (
                "This transition should be rejected."
            ),
            "reviewer": "test_reviewer",
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
        json={
            "new_status": "under_review",
            "decision": "manual_review_started",
            "notes": "Human review started.",
            "reviewer": "test_reviewer",
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
        json={
            "new_status": "reviewed",
            "decision": "manual_review_completed",
            "notes": "Human review completed.",
            "reviewer": "test_reviewer",
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
        json={
            "new_status": "confirmed",
            "decision": "confirmed_child_safety_concern",
            "notes": (
                "Human reviewer confirmed the concern."
            ),
            "reviewer": "test_reviewer",
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
        json={
            "new_status": "dismissed",
            "decision": "invalid_final_change",
            "notes": (
                "Final decisions must not be changed."
            ),
            "reviewer": "test_reviewer",
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

    app.dependency_overrides[
        original_get_db
    ] = failing_get_db

    try:
        # -----------------------------------------------------
        # Attempt report creation
        # -----------------------------------------------------

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

        # The endpoint should report a persistence failure.
        assert response.status_code == 500

        assert response.json() == {
            "detail": "Unable to save report."
        }

    finally:
        # Remove our temporary override even if an assertion
        # fails.
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