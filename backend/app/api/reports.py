import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.report import Report
from app.models.report_ai_analysis import ReportAIAnalysis
from app.models.report_review import ReportReview
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


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


# ============================================================
# REQUEST MODELS
# ============================================================


class ReportCreate(BaseModel):
    platform: str
    url: str
    reason: str
    description: str


class ReportReviewCreate(BaseModel):
    new_status: str
    decision: str
    notes: str
    reviewer: str


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


@router.post("/")
def create_report(
    report: ReportCreate,
    db: Session = Depends(get_db),
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
        reviewer=review.reviewer,
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
# GET SINGLE REPORT
# ============================================================


@router.get("/{report_id}")
def get_report(
    report_id: int,
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