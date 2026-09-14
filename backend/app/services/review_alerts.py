from datetime import (
    datetime,
    timedelta,
    timezone,
)

from sqlalchemy.orm import Session

from app.models.report import Report
from app.models.report_action import ReportAction


URGENT_PENDING_LIMIT = timedelta(
    hours=1
)

UNDER_REVIEW_LIMIT = timedelta(
    hours=24
)

ACTION_PENDING_LIMIT = timedelta(
    hours=24
)

ACTION_IN_PROGRESS_LIMIT = timedelta(
    hours=72
)


def _utc_now() -> datetime:
    return datetime.now(
        timezone.utc
    )


def get_review_alerts(
    db: Session,
) -> list[dict]:
    now = _utc_now()

    alerts = []

    reports = (
        db.query(Report)
        .order_by(
            Report.created_at.asc()
        )
        .all()
    )

    for report in reports:
        created_at = (
            report.created_at
        )

        if created_at is None:
            continue

        if created_at.tzinfo is None:
            created_at = (
                created_at.replace(
                    tzinfo=timezone.utc
                )
            )

        age = (
            now - created_at
        )

        report_id = (
            f"CV-{report.id:06d}"
        )

        if (
            report.review_status
            == "pending"
            and report.risk_level
            in {
                "high",
                "critical",
            }
            and age
            >= URGENT_PENDING_LIMIT
        ):
            alerts.append(
                {
                    "type":
                        "urgent_pending",
                    "severity":
                        "critical",
                    "report_id":
                        report_id,
                    "message": (
                        "High-risk report "
                        "is still pending review."
                    ),
                }
            )

        if (
            report.review_status
            == "pending"
            and report.risk_level
            in {
                "high",
                "critical",
            }
            and not report.assigned_reviewer_id
        ):
            alerts.append(
                {
                    "type":
                        "urgent_unassigned",
                    "severity":
                        "high",
                    "report_id":
                        report_id,
                    "message": (
                        "High-risk report "
                        "has no assigned reviewer."
                    ),
                }
            )

        if (
            report.review_status
            == "under_review"
            and age
            >= UNDER_REVIEW_LIMIT
        ):
            alerts.append(
                {
                    "type":
                        "review_overdue",
                    "severity":
                        "medium",
                    "report_id":
                        report_id,
                    "message": (
                        "Report has remained "
                        "under review too long."
                    ),
                }
            )

        if (
            report.review_status
            == "escalated"
        ):
            action_count = (
                db.query(ReportAction)
                .filter(
                    ReportAction.report_id
                    == report.id
                )
                .count()
            )

            if action_count == 0:
                alerts.append(
                    {
                        "type":
                            "escalated_without_action",
                        "severity":
                            "high",
                        "report_id":
                            report_id,
                        "message": (
                            "Escalated report "
                            "has no case action."
                        ),
                    }
                )


    actions = (
        db.query(ReportAction)
        .order_by(
            ReportAction.created_at.asc()
        )
        .all()
    )

    for action in actions:
        created_at = (
            action.created_at
        )

        if created_at is None:
            continue

        if created_at.tzinfo is None:
            created_at = (
                created_at.replace(
                    tzinfo=timezone.utc
                )
            )

        age = (
            now - created_at
        )

        report_id = (
            f"CV-{action.report_id:06d}"
        )

        if (
            action.status == "pending"
            and age
            >= ACTION_PENDING_LIMIT
        ):
            alerts.append(
                {
                    "type":
                        "action_pending_overdue",
                    "severity":
                        "medium",
                    "report_id":
                        report_id,
                    "action_id":
                        action.id,
                    "message": (
                        "Case action has remained "
                        "pending for more than "
                        "24 hours."
                    ),
                }
            )

        if (
            action.status
            == "in_progress"
            and age
            >= ACTION_IN_PROGRESS_LIMIT
        ):
            alerts.append(
                {
                    "type":
                        "action_in_progress_overdue",
                    "severity":
                        "high",
                    "report_id":
                        report_id,
                    "action_id":
                        action.id,
                    "message": (
                        "Case action has remained "
                        "in progress for more than "
                        "72 hours."
                    ),
                }
            )

    return alerts