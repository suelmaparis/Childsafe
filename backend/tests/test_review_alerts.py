from datetime import (
    datetime,
    timedelta,
    timezone,
)

from app.models.report import Report
from app.models.report_action import ReportAction


def test_high_risk_pending_report_without_reviewer_creates_alert(
    db_session,
):
    report = Report(
        platform="Instagram",
        url="https://example.com/alert-1",
        reason="potential_child_exposure",
        description="High-risk pending report.",
        risk_level="high",
        risk_score=80,
        review_status="pending",
        created_at=(
            datetime.now(timezone.utc)
            - timedelta(hours=2)
        ),
    )

    db_session.add(report)
    db_session.commit()
    db_session.refresh(report)

    from app.services.review_alerts import (
        get_review_alerts,
    )

    alerts = get_review_alerts(
        db_session
    )

    report_id = (
        f"CV-{report.id:06d}"
    )

    matching = [
        alert
        for alert in alerts
        if alert["report_id"]
        == report_id
    ]

    alert_types = {
        alert["type"]
        for alert in matching
    }

    assert (
        "urgent_pending"
        in alert_types
    )

    assert (
        "urgent_unassigned"
        in alert_types
    )


def test_escalated_report_without_action_creates_alert(
    db_session,
):
    report = Report(
        platform="Facebook",
        url="https://example.com/alert-2",
        reason="potential_child_exposure",
        description="Escalated report.",
        risk_level="high",
        risk_score=85,
        review_status="escalated",
        created_at=(
            datetime.now(timezone.utc)
            - timedelta(hours=3)
        ),
    )

    db_session.add(report)
    db_session.commit()
    db_session.refresh(report)

    from app.services.review_alerts import (
        get_review_alerts,
    )

    alerts = get_review_alerts(
        db_session
    )

    report_id = (
        f"CV-{report.id:06d}"
    )

    assert any(
        alert["type"]
        == "escalated_without_action"
        and alert["report_id"]
        == report_id
        for alert in alerts
    )


def test_escalated_report_with_action_has_no_missing_action_alert(
    db_session,
    admin_user,
):
    report = Report(
        platform="TikTok",
        url="https://example.com/alert-3",
        reason="potential_child_exposure",
        description="Escalated report with action.",
        risk_level="high",
        risk_score=90,
        review_status="escalated",
        created_at=(
            datetime.now(timezone.utc)
            - timedelta(hours=4)
        ),
    )

    db_session.add(report)
    db_session.commit()
    db_session.refresh(report)

    action = ReportAction(
        report_id=report.id,
        action_type="internal_escalation",
        status="pending",
        notes="Action exists.",
        created_by_reviewer_id=(
            admin_user.id
        ),
    )

    db_session.add(action)
    db_session.commit()

    from app.services.review_alerts import (
        get_review_alerts,
    )

    alerts = get_review_alerts(
        db_session
    )

    report_id = (
        f"CV-{report.id:06d}"
    )

    assert not any(
        alert["type"]
        == "escalated_without_action"
        and alert["report_id"]
        == report_id
        for alert in alerts
    )


def test_normal_report_does_not_create_alert(
    db_session,
):
    report = Report(
        platform="YouTube",
        url="https://example.com/alert-4",
        reason="potential_child_exposure",
        description="Normal low-risk report.",
        risk_level="low",
        risk_score=10,
        review_status="pending",
        created_at=datetime.now(
            timezone.utc
        ),
    )

    db_session.add(report)
    db_session.commit()
    db_session.refresh(report)

    from app.services.review_alerts import (
        get_review_alerts,
    )

    alerts = get_review_alerts(
        db_session
    )

    report_id = (
        f"CV-{report.id:06d}"
    )

    assert not any(
        alert["report_id"]
        == report_id
        for alert in alerts
    )


def test_review_alerts_endpoint(
    client,
    auth_headers,
):
    response = client.get(
        "/reports/review-alerts",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "count" in data
    assert "alerts" in data
    assert isinstance(
        data["alerts"],
        list,
    )

    assert (
        data["count"]
        == len(data["alerts"])
    )


def test_review_alerts_requires_authentication(
    client,
):
    response = client.get(
        "/reports/review-alerts"
    )

    assert response.status_code == 401

def test_pending_action_overdue_creates_alert(
    db_session,
    admin_user,
):
    report = Report(
        platform="Instagram",
        url="https://example.com/action-alert-1",
        reason="potential_child_exposure",
        description="Report with overdue pending action.",
        risk_level="medium",
        risk_score=40,
        review_status="confirmed",
        created_at=datetime.now(
            timezone.utc
        ),
    )

    db_session.add(report)
    db_session.commit()
    db_session.refresh(report)

    action = ReportAction(
        report_id=report.id,
        action_type="internal_escalation",
        status="pending",
        notes="Waiting too long.",
        created_by_reviewer_id=(
            admin_user.id
        ),
        created_at=(
            datetime.now(timezone.utc)
            - timedelta(hours=25)
        ),
        updated_at=(
            datetime.now(timezone.utc)
            - timedelta(hours=25)
        ),
    )

    db_session.add(action)
    db_session.commit()
    db_session.refresh(action)

    from app.services.review_alerts import (
        get_review_alerts,
    )

    alerts = get_review_alerts(
        db_session
    )

    report_id = (
        f"CV-{report.id:06d}"
    )

    assert any(
        alert["type"]
        == "action_pending_overdue"
        and alert["report_id"]
        == report_id
        and alert["action_id"]
        == action.id
        for alert in alerts
    )


def test_in_progress_action_overdue_creates_alert(
    db_session,
    admin_user,
):
    report = Report(
        platform="Facebook",
        url="https://example.com/action-alert-2",
        reason="potential_child_exposure",
        description="Report with overdue action.",
        risk_level="high",
        risk_score=75,
        review_status="confirmed",
        created_at=datetime.now(
            timezone.utc
        ),
    )

    db_session.add(report)
    db_session.commit()
    db_session.refresh(report)

    action = ReportAction(
        report_id=report.id,
        action_type="platform_report",
        status="in_progress",
        notes="Still waiting for response.",
        created_by_reviewer_id=(
            admin_user.id
        ),
        created_at=(
            datetime.now(timezone.utc)
            - timedelta(hours=73)
        ),
        updated_at=(
            datetime.now(timezone.utc)
            - timedelta(hours=73)
        ),
    )

    db_session.add(action)
    db_session.commit()
    db_session.refresh(action)

    from app.services.review_alerts import (
        get_review_alerts,
    )

    alerts = get_review_alerts(
        db_session
    )

    report_id = (
        f"CV-{report.id:06d}"
    )

    assert any(
        alert["type"]
        == "action_in_progress_overdue"
        and alert["report_id"]
        == report_id
        and alert["action_id"]
        == action.id
        for alert in alerts
    )