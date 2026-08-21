import json

from sqlalchemy import func
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)
from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    field_validator,
)
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from datetime import datetime, timedelta, timezone
from app.core.database import SessionLocal
from app.models.report import Report
from app.models.report_ai_analysis import ReportAIAnalysis
from app.models.report_review import ReportReview
from app.api.auth import require_role
from app.services.ai_risk_assessment import (
    AI_MODEL,
    assess_risk_with_ai,
)
from app.services.review_queue_priority import (
    determine_queue_priority,
)
from app.services.review_state_machine import (
    validate_review_transition,
)
from app.services.review_triage import (
    determine_review_priority,
)
from app.services.risk_assessment import assess_risk
from app.services.risk_comparison import (
    compare_risk_assessments,
)
from app.api.auth import get_current_reviewer
from app.models.reviewer import Reviewer

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)

limiter = Limiter(
    key_func=get_remote_address
)
# ============================================================
# REQUEST MODELS
# ============================================================


class ReportCreate(BaseModel):
    platform: str
    url: str
    reason: str
    description: str

    source_type: str = "unknown"
    source_channel: str | None = None
    source_reference: str | None = None

class PublicReportCreate(BaseModel):
    platform: str

    url: HttpUrl

    reason: str

    description: str = Field(
        min_length=10,
        max_length=2000,
    )

    @field_validator("platform")
    @classmethod
    def validate_platform(
        cls,
        value: str,
    ) -> str:
        allowed_platforms = {
            "Instagram",
            "Facebook",
            "TikTok",
            "YouTube",
            "X",
            "Other",
        }

        value = value.strip()

        if value not in allowed_platforms:
            raise ValueError(
                "Unsupported platform."
            )

        return value

    @field_validator("reason")
    @classmethod
    def validate_reason(
        cls,
        value: str,
    ) -> str:
        allowed_reasons = {
            "potential_child_exposure",
            "location_exposure",
            "privacy_concern",
            "suspected_exploitation",
            "sexualized_content",
            "other",
        }

        value = value.strip()

        if value not in allowed_reasons:
            raise ValueError(
                "Unsupported report reason."
            )

        return value

    @field_validator("description")
    @classmethod
    def clean_description(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Description cannot be empty."
            )

        return value
class ReportReviewCreate(BaseModel):
    new_status: str
    decision: str
    notes: str
# ============================================================
# DATABASE DEPENDENCY
# ============================================================


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# HELPERS
# ============================================================


def normalize_score(
    score: int,
) -> int:
    """
    Normalize a score to the current 0-100 scale.

    Historical records may contain scores greater than 100
    because an older version of the deterministic rule engine
    allowed cumulative scores above 100.

    The stored historical value is not modified.
    """

    return max(
        0,
        min(int(score), 100),
    )


def parse_ai_reasons(
    value: str,
) -> list[str]:
    """
    Safely deserialize AI reasons stored as JSON text.

    Invalid historical JSON must not break an entire endpoint.
    """

    try:
        parsed = json.loads(value)

    except (
        json.JSONDecodeError,
        TypeError,
    ):
        return [str(value)]

    if isinstance(parsed, list):
        return [
            str(item)
            for item in parsed
        ]

    return [str(parsed)]


def get_latest_ai_analysis(
    db: Session,
    report_id: int,
) -> ReportAIAnalysis | None:
    """
    Return the newest AI analysis for a report.
    """

    return (
        db.query(ReportAIAnalysis)
        .filter(
            ReportAIAnalysis.report_id
            == report_id
        )
        .order_by(
            ReportAIAnalysis.created_at.desc()
        )
        .first()
    )


# ============================================================
# CREATE REPORT
# ============================================================

def create_report_record(
    report: ReportCreate,
    db: Session,
):
    """
    Create a child-safety report.

    The deterministic assessment is the primary layer.

    AI is a secondary assessment layer and does not make
    enforcement or final review decisions.

    AI failure must not prevent a report from being received.
    """

    # --------------------------------------------------------
    # 1. Deterministic assessment
    # --------------------------------------------------------

    assessment = assess_risk(
        report.reason,
        report.description,
    )

    # --------------------------------------------------------
    # 2. Secondary AI assessment
    # --------------------------------------------------------

    ai_assessment = None

    try:
        ai_assessment = assess_risk_with_ai(
            report.reason,
            report.description,
        )

    except Exception as exc:
        # AI is an optional secondary layer.
        # A failure here must not prevent report creation.
        print(
            f"AI risk assessment unavailable: {exc}"
        )

    # --------------------------------------------------------
    # 3. Initial deterministic triage
    # --------------------------------------------------------

    triage = determine_review_priority(
        assessment.level
    )

    # --------------------------------------------------------
    # 4. Compare deterministic and AI assessments
    # --------------------------------------------------------

    risk_comparison = None

    if ai_assessment is not None:
        risk_comparison = compare_risk_assessments(
            rule_level=assessment.level,
            rule_score=assessment.score,
            ai_level=ai_assessment.level,
            ai_score=ai_assessment.score,
        )

    # --------------------------------------------------------
    # 5. Create report
    # --------------------------------------------------------

    new_report = Report(
        platform=report.platform,
        url=report.url,
        reason=report.reason,
        description=report.description,

        source_type=report.source_type,
        source_channel=report.source_channel,
        source_reference=report.source_reference,

        risk_level=assessment.level,
        risk_score=assessment.score,
        review_status="pending",
    )

    db.add(new_report)

    ai_analysis = None

    try:
        # Obtain report ID without committing yet.
        db.flush()

        # ----------------------------------------------------
        # 6. Save AI analysis when available
        # ----------------------------------------------------

        if ai_assessment is not None:
            ai_analysis = ReportAIAnalysis(
                report_id=new_report.id,
                model=AI_MODEL,
                level=ai_assessment.level,
                score=ai_assessment.score,
                reasons=json.dumps(
                    ai_assessment.reasons
                ),
            )

            db.add(ai_analysis)

        # ----------------------------------------------------
        # 7. Commit report + AI analysis atomically
        # ----------------------------------------------------

        db.commit()

        db.refresh(new_report)

        if ai_analysis is not None:
            db.refresh(ai_analysis)

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to save report.",
        ) from exc

    # --------------------------------------------------------
    # 8. Build response
    # --------------------------------------------------------

    response = {
        "report_id": (
            f"CV-{new_report.id:06d}"
        ),
        "status": new_report.status,
        "message": (
            "Report received successfully."
        ),
        "report": {
            "report_id": (
                f"CV-{new_report.id:06d}"
            ),
            "platform": new_report.platform,
            "url": new_report.url,
            "reason": new_report.reason,
            "description": (
                new_report.description
            ),

            "source_type": new_report.source_type,
            "source_channel": new_report.source_channel,
            "source_reference": new_report.source_reference,

            "status": new_report.status,

            # Deterministic assessment
            "risk_level": (
                new_report.risk_level
            ),
            "risk_score": (
                new_report.risk_score
            ),
            "risk_reasons": (
                assessment.reasons
            ),

            # Initial deterministic triage
            "review_status": (
                new_report.review_status
            ),
            "review_priority": (
                triage.priority
            ),
            "recommended_queue": (
                triage.recommended_queue
            ),

            "created_at": (
                new_report.created_at
            ),
        },
    }

    # --------------------------------------------------------
    # 9. Risk comparison response
    # --------------------------------------------------------

    if risk_comparison is not None:
        response["report"]["risk_comparison"] = {
            "relationship": (
                risk_comparison.relationship
            ),
            "level_difference": (
                risk_comparison.level_difference
            ),
            "score_difference": (
                risk_comparison.score_difference
            ),
            "needs_attention": (
                risk_comparison.needs_attention
            ),
        }

    else:
        response["report"]["risk_comparison"] = {
            "status": "unavailable",
        }

    # --------------------------------------------------------
    # 10. AI assessment response
    # --------------------------------------------------------

    if (
        ai_assessment is not None
        and ai_analysis is not None
    ):
        response["report"]["ai_assessment"] = {
            "level": ai_analysis.level,
            "score": ai_analysis.score,
            "reasons": (
                ai_assessment.reasons
            ),
            "model": ai_analysis.model,
            "created_at": (
                ai_analysis.created_at
            ),
        }

    else:
        response["report"]["ai_assessment"] = {
            "status": "unavailable",
        }

    return response

@router.post("/")
def create_report(
    report: ReportCreate,
    db: Session = Depends(get_db),
):
    return create_report_record(
        report=report,
        db=db,
    )
@router.post("/public")
@limiter.limit("5/minute")
def create_public_report(
    request: Request,
    report: PublicReportCreate,
    db: Session = Depends(get_db),
):
    internal_report = ReportCreate(
        platform=report.platform,
        url=str(report.url),
        reason=report.reason,
        description=report.description,
        source_type="public_report",
        source_channel="public_web_form",
        source_reference=None,
    )

    result = create_report_record(
        report=internal_report,
        db=db,
    )

    return {
        "report_id": result["report_id"],
        "status": result["status"],
        "message": (
            "Report submitted successfully."
        ),
    }
# ============================================================
# LIST REPORTS
# ============================================================


@router.get("/")
def list_reports(
    db: Session = Depends(get_db),
):
    reports = (
        db.query(Report)
        .order_by(
            Report.created_at.desc()
        )
        .all()
    )

    return [
        {
            "report_id": (
                f"CV-{report.id:06d}"
            ),
            "platform": report.platform,
            "url": report.url,
            "reason": report.reason,
            "description": (
                report.description
            ),
            "status": report.status,
            "risk_level": (
                report.risk_level
            ),
            "risk_score": (
                report.risk_score
            ),
            "review_status": (
                report.review_status
            ),
            "created_at": (
                report.created_at
            ),
        }
        for report in reports
    ]


# ============================================================
# REVIEW QUEUE
# ============================================================


@router.get("/review-queue")
def review_queue(
    current_reviewer: Reviewer = Depends(
        require_role(
            "reviewer",
            "senior_reviewer",
            "admin",
        )
    ),
    db: Session = Depends(get_db),
):
    reports = (
        db.query(Report)
        .filter(
            Report.review_status == "pending"
        )
        .order_by(
            Report.risk_score.desc(),
            Report.created_at.asc(),
        )
        .all()
    )

    queue_items = []

    for report in reports:

        ai_analysis = get_latest_ai_analysis(
            db=db,
            report_id=report.id,
        )

        # Historical rule scores may exceed 100.
        # Preserve the database value in the response,
        # but normalize it for current comparison logic.
        comparison_rule_score = normalize_score(
            report.risk_score
        )

        if ai_analysis is not None:
            ai_level = ai_analysis.level
            comparison_ai_score = normalize_score(
                ai_analysis.score
            )

        else:
            ai_level = None
            comparison_ai_score = None

        try:
            queue_priority = (
                determine_queue_priority(
                    risk_level=report.risk_level,
                    risk_score=(
                        comparison_rule_score
                    ),
                    ai_level=ai_level,
                    ai_score=(
                        comparison_ai_score
                    ),
                )
            )

        except ValueError as exc:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Invalid risk data found "
                    f"for report {report.id}: "
                    f"{exc}"
                ),
            ) from exc

        item = {
            "report_id": (
                f"CV-{report.id:06d}"
            ),
            "platform": report.platform,
            "url": report.url,
            "reason": report.reason,
            "description": (
                report.description
            ),
            "status": report.status,

            # Preserve original stored values.
            "risk_level": (
                report.risk_level
            ),
            "risk_score": (
                report.risk_score
            ),

            "review_status": (
                report.review_status
            ),

            "queue_priority": (
                queue_priority.priority
            ),
            "queue_priority_score": (
                queue_priority.priority_score
            ),
            "queue_priority_reason": (
                queue_priority.reason
            ),

            "created_at": (
                report.created_at
            ),
        }

        if ai_analysis is not None:
            item["ai_assessment"] = {
                "level": ai_analysis.level,
                "score": ai_analysis.score,
                "reasons": parse_ai_reasons(
                    ai_analysis.reasons
                ),
                "model": ai_analysis.model,
                "created_at": (
                    ai_analysis.created_at
                ),
            }

        else:
            item["ai_assessment"] = {
                "status": "unavailable",
            }

        queue_items.append(item)

    # Highest-priority reports first.
    queue_items.sort(
        key=lambda item: (
            -item[
                "queue_priority_score"
            ],
            -normalize_score(
                item["risk_score"]
            ),
            item["created_at"],
        )
    )

    return queue_items


# ============================================================
# REVIEW REPORT
# ============================================================


@router.patch("/{report_id}/review")
def review_report(
    report_id: int,
    review: ReportReviewCreate,
    db: Session = Depends(get_db),
    current_reviewer: Reviewer = Depends(
        get_current_reviewer
    ),
):
    allowed_statuses = {
        "under_review",
        "reviewed",
        "confirmed",
        "dismissed",
        "escalated",
    }

    # --------------------------------------------------------
    # Validate target status
    # --------------------------------------------------------

    if review.new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail={
                "error": (
                    "Invalid review status."
                ),
                "allowed_statuses": sorted(
                    allowed_statuses
                ),
            },
        )

    # --------------------------------------------------------
    # Find report
    # --------------------------------------------------------

    report = db.get(
        Report,
        report_id,
    )

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found.",
        )

    previous_status = (
        report.review_status
    )

    # --------------------------------------------------------
    # Validate workflow transition
    # --------------------------------------------------------

    transition = (
        validate_review_transition(
            previous_status=previous_status,
            new_status=review.new_status,
        )
    )

    if not transition.allowed:
        raise HTTPException(
            status_code=409,
            detail={
                "error": transition.reason,
                "review_status": (
                    previous_status
                ),
            },
        )

    # --------------------------------------------------------
    # Create human review history
    # --------------------------------------------------------

    review_record = ReportReview(
        report_id=report.id,
        previous_status=previous_status,
        new_status=review.new_status,
        decision=review.decision,
        notes=review.notes,
        reviewer=current_reviewer.username,
)
    report.review_status = (
        review.new_status
    )

    db.add(review_record)

    try:
        db.commit()

        db.refresh(report)
        db.refresh(review_record)

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to save review.",
        ) from exc

    return {
        "report_id": (
            f"CV-{report.id:06d}"
        ),

        "review": {
            "previous_status": (
                review_record.previous_status
            ),
            "new_status": (
                review_record.new_status
            ),
            "decision": (
                review_record.decision
            ),
            "notes": (
                review_record.notes
            ),
            "reviewer": (
                review_record.reviewer
            ),
            "created_at": (
                review_record.created_at
            ),
        },

        "report": {
            "platform": report.platform,
            "url": report.url,
            "reason": report.reason,
            "risk_level": (
                report.risk_level
            ),
            "risk_score": (
                report.risk_score
            ),
            "review_status": (
                report.review_status
            ),
        },
    }


# ============================================================
# REVIEW HISTORY
# ============================================================


@router.get("/{report_id}/reviews")
def get_report_reviews(
    report_id: int,
    current_reviewer: Reviewer = Depends(
        require_role(
            "reviewer",
            "senior_reviewer",
            "admin",
        )
    ),
    db: Session = Depends(get_db),
):
    report = db.get(
        Report,
        report_id,
    )

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found.",
        )

    reviews = (
        db.query(ReportReview)
        .filter(
            ReportReview.report_id
            == report_id
        )
        .order_by(
            ReportReview.created_at.asc()
        )
        .all()
    )

    return [
        {
            "review_id": review.id,
            "previous_status": (
                review.previous_status
            ),
            "new_status": (
                review.new_status
            ),
            "decision": review.decision,
            "notes": review.notes,
            "reviewer": review.reviewer,
            "created_at": (
                review.created_at
            ),
        }
        for review in reviews
    ]


# ============================================================
# AUDIT
# ============================================================


@router.get("/{report_id}/audit")
def get_report_audit(
    report_id: int,
    current_reviewer: Reviewer = Depends(
        require_role(
            "reviewer",
            "senior_reviewer",
            "admin",
        )
    ),
    db: Session = Depends(get_db),
):
    """
    Read-only audit view for a report.

    Includes:
    - original report
    - deterministic assessment
    - latest AI assessment
    - AI analysis history
    - risk comparison
    - computed queue priority
    - human review history
    """

    # --------------------------------------------------------
    # Find report
    # --------------------------------------------------------

    report = db.get(
        Report,
        report_id,
    )

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found.",
        )

    # --------------------------------------------------------
    # AI history
    # --------------------------------------------------------

    ai_analyses = (
        db.query(ReportAIAnalysis)
        .filter(
            ReportAIAnalysis.report_id
            == report_id
        )
        .order_by(
            ReportAIAnalysis.created_at.asc()
        )
        .all()
    )

    ai_history = [
        {
            "analysis_id": analysis.id,
            "model": analysis.model,
            "level": analysis.level,
            "score": analysis.score,
            "reasons": parse_ai_reasons(
                analysis.reasons
            ),
            "created_at": (
                analysis.created_at
            ),
        }
        for analysis in ai_analyses
    ]

    latest_ai = (
        ai_analyses[-1]
        if ai_analyses
        else None
    )

    # Historical stored scores are preserved,
    # while current comparison logic uses 0-100.
    comparison_rule_score = normalize_score(
        report.risk_score
    )

    # --------------------------------------------------------
    # AI assessment + comparison
    # --------------------------------------------------------

    if latest_ai is not None:
        comparison_ai_score = (
            normalize_score(
                latest_ai.score
            )
        )

        ai_assessment = {
            "level": latest_ai.level,
            "score": latest_ai.score,
            "reasons": parse_ai_reasons(
                latest_ai.reasons
            ),
            "model": latest_ai.model,
            "created_at": (
                latest_ai.created_at
            ),
        }

        try:
            comparison = (
                compare_risk_assessments(
                    rule_level=(
                        report.risk_level
                    ),
                    rule_score=(
                        comparison_rule_score
                    ),
                    ai_level=(
                        latest_ai.level
                    ),
                    ai_score=(
                        comparison_ai_score
                    ),
                )
            )

            queue_priority = (
                determine_queue_priority(
                    risk_level=(
                        report.risk_level
                    ),
                    risk_score=(
                        comparison_rule_score
                    ),
                    ai_level=(
                        latest_ai.level
                    ),
                    ai_score=(
                        comparison_ai_score
                    ),
                )
            )

        except ValueError as exc:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Invalid stored risk data: "
                    f"{exc}"
                ),
            ) from exc

        comparison_data = {
            "relationship": (
                comparison.relationship
            ),
            "level_difference": (
                comparison.level_difference
            ),
            "score_difference": (
                comparison.score_difference
            ),
            "needs_attention": (
                comparison.needs_attention
            ),
        }

    else:
        ai_assessment = {
            "status": "unavailable",
        }

        comparison_data = {
            "status": "unavailable",
        }

        try:
            queue_priority = (
                determine_queue_priority(
                    risk_level=(
                        report.risk_level
                    ),
                    risk_score=(
                        comparison_rule_score
                    ),
                )
            )

        except ValueError as exc:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Invalid stored risk data: "
                    f"{exc}"
                ),
            ) from exc

    # --------------------------------------------------------
    # Human review history
    # --------------------------------------------------------

    reviews = (
        db.query(ReportReview)
        .filter(
            ReportReview.report_id
            == report_id
        )
        .order_by(
            ReportReview.created_at.asc()
        )
        .all()
    )

    review_history = [
        {
            "review_id": review.id,
            "previous_status": (
                review.previous_status
            ),
            "new_status": (
                review.new_status
            ),
            "decision": (
                review.decision
            ),
            "notes": review.notes,
            "reviewer": (
                review.reviewer
            ),
            "created_at": (
                review.created_at
            ),
        }
        for review in reviews
    ]

    return {
        "report_id": (
            f"CV-{report.id:06d}"
        ),

        "report": {
            "id": report.id,
            "platform": report.platform,
            "url": report.url,
            "reason": report.reason,
            "description": (
                report.description
            ),

            "source_type": report.source_type,
            "source_channel": report.source_channel,
            "source_reference": report.source_reference,

            "status": report.status,
            "created_at": (
                report.created_at
            ),
        },

        "deterministic_assessment": {
            # Historical stored value is preserved.
            "level": report.risk_level,
            "score": report.risk_score,
        },

        "ai_assessment": (
            ai_assessment
        ),

        "ai_analysis_history": (
            ai_history
        ),

        "risk_comparison": (
            comparison_data
        ),

        "review": {
            "current_status": (
                report.review_status
            ),
            "review_count": len(
                review_history
            ),
            "history": (
                review_history
            ),
        },

        "queue_priority": {
            # A finalized report is no longer actually
            # present in the pending review queue.
            "active": (
                report.review_status
                == "pending"
            ),
            "priority": (
                queue_priority.priority
            ),
            "priority_score": (
                queue_priority.priority_score
            ),
            "reason": (
                queue_priority.reason
            ),
        },
    }
# ============================================================
# ADMIN METRICS
# ============================================================


@router.get("/admin/metrics")
def get_admin_metrics(
    days: int | None = None,
    current_reviewer: Reviewer = Depends(
        require_role(
            "admin",
            "senior_reviewer",
        )
    ),
    db: Session = Depends(get_db),
):
    """
    Return operational metrics for the ChildSafe review system.

    Accessible only to administrators and senior reviewers.

    Report totals and distributions are calculated with SQL
    aggregation instead of loading every report into memory.

    Optional period filter:
    - days: include only reports created within the last 1-365 days.
    """

    # ---------------------------------------------------------
    # Optional period filter
    # ---------------------------------------------------------

    if days is not None:
        if days < 1 or days > 365:
            raise HTTPException(
                status_code=422,
                detail="days must be between 1 and 365.",
            )

        period_start = (
            datetime.now(timezone.utc)
            - timedelta(days=days)
        )
    else:
        period_start = None

    # ---------------------------------------------------------
    # Total reports
    # ---------------------------------------------------------

    total_query = db.query(
        func.count(Report.id)
    )

    if period_start is not None:
        total_query = total_query.filter(
            Report.created_at >= period_start
        )

    total_reports = (
        total_query.scalar()
        or 0
    )

    # ---------------------------------------------------------
    # Review-status distribution
    # ---------------------------------------------------------

    review_status_query = db.query(
        Report.review_status,
        func.count(Report.id),
    )

    if period_start is not None:
        review_status_query = (
            review_status_query.filter(
                Report.created_at >= period_start
            )
        )

    review_status_rows = (
        review_status_query
        .group_by(Report.review_status)
        .all()
    )

    review_status_counts = {
        "pending": 0,
        "under_review": 0,
        "reviewed": 0,
        "confirmed": 0,
        "dismissed": 0,
        "escalated": 0,
    }

    for status, count in review_status_rows:
        if status in review_status_counts:
            review_status_counts[status] = count

    # ---------------------------------------------------------
    # Risk-level distribution
    # ---------------------------------------------------------

    risk_query = db.query(
        Report.risk_level,
        func.count(Report.id),
    )

    if period_start is not None:
        risk_query = risk_query.filter(
            Report.created_at >= period_start
        )

    risk_rows = (
        risk_query
        .group_by(Report.risk_level)
        .all()
    )

    risk_distribution = {
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
    }

    for risk_level, count in risk_rows:
        if risk_level in risk_distribution:
            risk_distribution[risk_level] = count

    # ---------------------------------------------------------
    # Latest AI assessment per report
    # ---------------------------------------------------------
    #
    # Use one subquery to identify the newest AI analysis ID
    # for each report, avoiding an N+1 query pattern.
    # ---------------------------------------------------------

    latest_ai_subquery = (
        db.query(
            ReportAIAnalysis.report_id.label(
                "report_id"
            ),
            func.max(
                ReportAIAnalysis.id
            ).label(
                "latest_analysis_id"
            ),
        )
        .group_by(
            ReportAIAnalysis.report_id
        )
        .subquery()
    )

    # ---------------------------------------------------------
    # Urgent pending reports
    # ---------------------------------------------------------

    pending_query = (
        db.query(
            Report,
            ReportAIAnalysis,
        )
        .outerjoin(
            latest_ai_subquery,
            latest_ai_subquery.c.report_id
            == Report.id,
        )
        .outerjoin(
            ReportAIAnalysis,
            ReportAIAnalysis.id
            == latest_ai_subquery.c.latest_analysis_id,
        )
        .filter(
            Report.review_status == "pending"
        )
    )

    if period_start is not None:
        pending_query = pending_query.filter(
            Report.created_at >= period_start
        )

    pending_rows = pending_query.all()

    urgent_pending = 0

    for report, ai_analysis in pending_rows:
        ai_level = (
            ai_analysis.level
            if ai_analysis is not None
            else None
        )

        ai_score = (
            normalize_score(
                ai_analysis.score
            )
            if ai_analysis is not None
            else None
        )

        queue_priority = determine_queue_priority(
            risk_level=report.risk_level,
            risk_score=normalize_score(
                report.risk_score
            ),
            ai_level=ai_level,
            ai_score=ai_score,
        )

        if queue_priority.priority == "urgent":
            urgent_pending += 1
         # ---------------------------------------------------------
    # Outcome rates
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # Outcome rates
    # ---------------------------------------------------------

    confirmed_reports = (
        review_status_counts["confirmed"]
    )

    escalated_reports = (
        review_status_counts["escalated"]
    )

    if total_reports > 0:
        confirmation_rate = round(
            (
                confirmed_reports
                / total_reports
            )
            * 100,
            2,
        )

        escalation_rate = round(
            (
                escalated_reports
                / total_reports
            )
            * 100,
            2,
        )

    else:
        confirmation_rate = 0.0
        escalation_rate = 0.0

    # ---------------------------------------------------------
    # Response
    # ---------------------------------------------------------

    return {
        "total_reports": total_reports,
        "pending": (
            review_status_counts["pending"]
        ),
        "under_review": (
            review_status_counts[
                "under_review"
            ]
        ),
        "reviewed": (
            review_status_counts["reviewed"]
        ),
        "confirmed": (
            review_status_counts["confirmed"]
        ),
        "dismissed": (
            review_status_counts["dismissed"]
        ),
        "escalated": (
            review_status_counts["escalated"]
        ),
        "risk_distribution": (
            risk_distribution
        ),
        "urgent_pending": urgent_pending,
        "confirmation_rate": (
            confirmation_rate
        ),
        "escalation_rate": (
            escalation_rate
        ),
    }
# ============================================================
# ADMIN METRICS TREND
# ============================================================


@router.get("/admin/metrics/trend")
def get_admin_metrics_trend(
    days: int = 30,
    current_reviewer: Reviewer = Depends(
        require_role(
            "admin",
            "senior_reviewer",
        )
    ),
    db: Session = Depends(get_db),
):
    """
    Return a daily report trend for the ChildSafe dashboard.

    Accessible only to administrators and senior reviewers.

    The result includes every calendar day in the requested
    period, including days with zero reports.
    """

    if days < 1 or days > 365:
        raise HTTPException(
            status_code=422,
            detail=(
                "days must be between 1 and 365."
            ),
        )

    now = datetime.now(timezone.utc)
    today = now.date()

    start_date = (
        today
        - timedelta(days=days - 1)
    )

    period_start = datetime.combine(
        start_date,
        datetime.min.time(),
        tzinfo=timezone.utc,
    )

    # ---------------------------------------------------------
    # Reports created during the period
    # ---------------------------------------------------------

    reports = (
        db.query(Report)
        .filter(
            Report.created_at >= period_start
        )
        .all()
    )

    # ---------------------------------------------------------
    # Initialize every day with zero values
    # ---------------------------------------------------------

    daily_metrics = {}

    for day_offset in range(days):
        current_date = (
            start_date
            + timedelta(days=day_offset)
        )

        daily_metrics[current_date] = {
            "date": current_date.isoformat(),
            "created": 0,
            "confirmed": 0,
            "escalated": 0,
        }

    # ---------------------------------------------------------
    # Aggregate reports by creation date
    # ---------------------------------------------------------

    for report in reports:
        report_date = report.created_at.date()

        if report_date not in daily_metrics:
            continue

        daily_metrics[
            report_date
        ]["created"] += 1

        if report.review_status == "confirmed":
            daily_metrics[
                report_date
            ]["confirmed"] += 1

        if report.review_status == "escalated":
            daily_metrics[
                report_date
            ]["escalated"] += 1

    return list(
        daily_metrics.values()
    )
# ============================================================
# ADMIN REVIEW TREND
# ============================================================


@router.get("/admin/review-trend")
def get_admin_review_trend(
    days: int = 30,
    current_reviewer: Reviewer = Depends(
        require_role(
            "admin",
            "senior_reviewer",
        )
    ),
    db: Session = Depends(get_db),
):
    """
    Return daily human-review decision activity.

    Unlike /admin/metrics/trend, which groups reports by
    report creation date, this endpoint groups review events
    by the date on which the human decision was recorded.

    Accessible only to administrators and senior reviewers.
    """

    if days < 1 or days > 365:
        raise HTTPException(
            status_code=422,
            detail="days must be between 1 and 365.",
        )

    now = datetime.now(timezone.utc)
    today = now.date()

    start_date = (
        today
        - timedelta(days=days - 1)
    )

    period_start = datetime.combine(
        start_date,
        datetime.min.time(),
        tzinfo=timezone.utc,
    )

    # ---------------------------------------------------------
    # Review events in requested period
    # ---------------------------------------------------------

    review_events = (
        db.query(ReportReview)
        .filter(
            ReportReview.created_at >= period_start
        )
        .all()
    )

    # ---------------------------------------------------------
    # Initialize every calendar day
    # ---------------------------------------------------------

    daily_metrics = {}

    for day_offset in range(days):
        current_date = (
            start_date
            + timedelta(days=day_offset)
        )

        daily_metrics[current_date] = {
            "date": current_date.isoformat(),
            "review_events": 0,
            "confirmed": 0,
            "dismissed": 0,
            "escalated": 0,
        }

    # ---------------------------------------------------------
    # Aggregate human-review events
    # ---------------------------------------------------------

    for review in review_events:
        review_date = (
            review.created_at.date()
        )

        if review_date not in daily_metrics:
            continue

        daily_metrics[
            review_date
        ]["review_events"] += 1

        if review.new_status == "confirmed":
            daily_metrics[
                review_date
            ]["confirmed"] += 1

        elif review.new_status == "dismissed":
            daily_metrics[
                review_date
            ]["dismissed"] += 1

        elif review.new_status == "escalated":
            daily_metrics[
                review_date
            ]["escalated"] += 1

    return list(
        daily_metrics.values()
    )
# ============================================================
# GET SINGLE REPORT
# ============================================================


@router.get("/{report_id}")
def get_report(
    report_id: int,
    current_reviewer: Reviewer = Depends(
        require_role(
            "reviewer",
            "senior_reviewer",
            "admin",
        )
    ),
    db: Session = Depends(get_db),
):
    report = db.get(
        Report,
        report_id,
    )

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found.",
        )

    return {
        "report_id": (
            f"CV-{report.id:06d}"
        ),
        "platform": report.platform,
        "url": report.url,
        "reason": report.reason,
        "description": (
            report.description
        ),
        "status": report.status,
        "risk_level": (
            report.risk_level
        ),
        "risk_score": (
            report.risk_score
        ),
        "review_status": (
            report.review_status
        ),
        "created_at": (
            report.created_at
        ),
    }