import json

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.report import Report
from app.models.report_review import ReportReview
from app.models.report_ai_analysis import ReportAIAnalysis
from app.services.risk_assessment import assess_risk
from app.services.review_triage import determine_review_priority
from app.services.ai_risk_assessment import assess_risk_with_ai
from app.services.risk_comparison import compare_risk_assessments
from app.models.report_ai_analysis import ReportAIAnalysis
from app.services.review_queue_priority import determine_queue_priority
from app.services.review_state_machine import validate_review_transition


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_report(
    report: ReportCreate,
    db: Session = Depends(get_db),
):
    """
    Create a child-safety report.

    The deterministic risk assessment is the primary layer.
    AI is a secondary analysis layer and does not make
    enforcement or final review decisions.
    """

    # ---------------------------------------------------------
    # 1. Primary deterministic risk assessment
    # ---------------------------------------------------------

    assessment = assess_risk(
        report.reason,
        report.description,
    )

    # ---------------------------------------------------------
    # 2. Secondary AI risk assessment
    # ---------------------------------------------------------

    ai_assessment = None

    try:
        ai_assessment = assess_risk_with_ai(
            report.reason,
            report.description,
        )

    except Exception as exc:
        # AI must never prevent a report from being received.
        print(f"AI risk assessment unavailable: {exc}")

    # ---------------------------------------------------------
    # 3. Review triage
    # ---------------------------------------------------------

    triage = determine_review_priority(
        assessment.level
    )
    
    risk_comparison = None

    if ai_assessment is not None:
        risk_comparison = compare_risk_assessments(
            rule_level=assessment.level,
            rule_score=assessment.score,
            ai_level=ai_assessment.level,
            ai_score=ai_assessment.score,
        )
    # ---------------------------------------------------------
    # 4. Create report
    # ---------------------------------------------------------

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

    try:
        # Flush gives us the report ID without committing yet.
        db.flush()

        # -----------------------------------------------------
        # 5. Save AI analysis when available
        # -----------------------------------------------------

        ai_analysis = None

        if ai_assessment is not None:
            ai_analysis = ReportAIAnalysis(
                report_id=new_report.id,
                model="gpt-5-mini",
                level=ai_assessment.level,
                score=ai_assessment.score,
                reasons=json.dumps(ai_assessment.reasons),
            )

            db.add(ai_analysis)

        # -----------------------------------------------------
        # 6. Commit report + AI analysis together
        # -----------------------------------------------------

        db.commit()

        db.refresh(new_report)

        if ai_analysis is not None:
            db.refresh(ai_analysis)

    except Exception:
        db.rollback()
        raise

    # ---------------------------------------------------------
    # 7. Build response
    # ---------------------------------------------------------

    response = {
        "report_id": f"CV-{new_report.id:06d}",
        "status": new_report.status,
        "message": "Report received successfully.",
        "report": {
            "report_id": f"CV-{new_report.id:06d}",
            "platform": new_report.platform,
            "url": new_report.url,
            "reason": new_report.reason,
            "description": new_report.description,
            "status": new_report.status,
             
            # Primary deterministic assessment
            "risk_level": new_report.risk_level,
            "risk_score": new_report.risk_score,
            "risk_reasons": assessment.reasons,

            # Review triage
            "review_status": new_report.review_status,
            "review_priority": triage.priority,
            "recommended_queue": triage.recommended_queue,
             
            "created_at": new_report.created_at,

            "risk_comparison": (
                {
                    "relationship": risk_comparison.relationship,
                    "level_difference": risk_comparison.level_difference,
                    "score_difference": risk_comparison.score_difference,
                    "needs_attention": risk_comparison.needs_attention,
                }
                if risk_comparison is not None
                else {
                    "status": "unavailable",
                }
            ),
        },
    }

    # ---------------------------------------------------------
    # 8. Add AI assessment to response
    # ---------------------------------------------------------

    if ai_assessment is not None and ai_analysis is not None:
        response["report"]["ai_assessment"] = {
            "level": ai_analysis.level,
            "score": ai_analysis.score,
            "reasons": ai_assessment.reasons,
            "model": ai_analysis.model,
            "created_at": ai_analysis.created_at,
        }

    else:
        response["report"]["ai_assessment"] = {
            "status": "unavailable",
        }

    return response


@router.get("/")
def list_reports(
    db: Session = Depends(get_db),
):
    reports = (
        db.query(Report)
        .order_by(Report.created_at.desc())
        .all()
    )

    return [
        {
            "report_id": f"CV-{report.id:06d}",
            "platform": report.platform,
            "url": report.url,
            "reason": report.reason,
            "description": report.description,
            "status": report.status,
            "risk_level": report.risk_level,
            "risk_score": report.risk_score,
            "review_status": report.review_status,
            "created_at": report.created_at,
        }
        for report in reports
    ]


@router.get("/review-queue")
def review_queue(db: Session = Depends(get_db)):
    reports = (
        db.query(Report)
        .filter(Report.review_status == "pending")
        .order_by(
            Report.risk_score.desc(),
            Report.created_at.asc(),
        )
        .all()
    )

    queue_items = []

    for report in reports:
        ai_analysis = (
            db.query(ReportAIAnalysis)
            .filter(ReportAIAnalysis.report_id == report.id)
            .order_by(ReportAIAnalysis.created_at.desc())
            .first()
        )

        if ai_analysis is not None:
            ai_level = ai_analysis.level
            ai_score = ai_analysis.score
        else:
            ai_level = None
            ai_score = None

        queue_priority = determine_queue_priority(
            risk_level=report.risk_level,
            risk_score=report.risk_score,
            ai_level=ai_level,
            ai_score=ai_score,
        )

        queue_items.append(
            {
                "report_id": f"CV-{report.id:06d}",
                "platform": report.platform,
                "url": report.url,
                "reason": report.reason,
                "description": report.description,
                "status": report.status,
                "risk_level": report.risk_level,
                "risk_score": report.risk_score,
                "review_status": report.review_status,
                "queue_priority": queue_priority.priority,
                "queue_priority_score": queue_priority.priority_score,
                "queue_priority_reason": queue_priority.reason,
                "ai_assessment": (
                    {
                        "level": ai_analysis.level,
                        "score": ai_analysis.score,
                        "reasons": json.loads(ai_analysis.reasons),
                        "model": ai_analysis.model,
                        "created_at": ai_analysis.created_at,
                    }
                    if ai_analysis is not None
                    else {
                        "status": "unavailable",
                    }
                ),
                "created_at": report.created_at,
            }
        )

    queue_items.sort(
        key=lambda item: (
            -item["queue_priority_score"],
            -item["risk_score"],
            item["created_at"],
        )
    )

    return queue_items

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

    final_statuses = {
        "confirmed",
        "dismissed",
        "escalated",
    }

    # ---------------------------------------------------------
    # Validate requested status
    # ---------------------------------------------------------

    if review.new_status not in allowed_statuses:
        return {
            "error": "Invalid review status.",
            "allowed_statuses": sorted(
                allowed_statuses
            ),
        }

    # ---------------------------------------------------------
    # Find report
    # ---------------------------------------------------------

    report = db.get(
        Report,
        report_id,
    )

    if report is None:
        return {
            "error": "Report not found."
        }

    previous_status = report.review_status

    # ---------------------------------------------------------
    # Protect final decisions
    # ---------------------------------------------------------

    transition = validate_review_transition(
        previous_status=previous_status,
        new_status=review.new_status,
    )

    if not transition.allowed:
        return {
            "error": transition.reason,
            "review_status": previous_status,
        }
    # ---------------------------------------------------------
    # Create review history record
    # ---------------------------------------------------------

    review_record = ReportReview(
        report_id=report.id,
        previous_status=previous_status,
        new_status=review.new_status,
        decision=review.decision,
        notes=review.notes,
        reviewer=review.reviewer,
    )

    report.review_status = review.new_status

    db.add(review_record)

    try:
        db.commit()

        db.refresh(report)
        db.refresh(review_record)

    except Exception:
        db.rollback()

        return {
            "error": "Unable to save review."
        }

    return {
        "report_id": f"CV-{report.id:06d}",
        "review": {
            "previous_status": review_record.previous_status,
            "new_status": review_record.new_status,
            "decision": review_record.decision,
            "notes": review_record.notes,
            "reviewer": review_record.reviewer,
            "created_at": review_record.created_at,
        },
        "report": {
            "platform": report.platform,
            "url": report.url,
            "reason": report.reason,
            "risk_level": report.risk_level,
            "risk_score": report.risk_score,
            "review_status": report.review_status,
        },
    }


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
        return {
            "error": "Report not found."
        }

    reviews = (
        db.query(ReportReview)
        .filter(
            ReportReview.report_id == report_id
        )
        .order_by(
            ReportReview.created_at.asc()
        )
        .all()
    )

    return [
        {
            "review_id": review.id,
            "previous_status": review.previous_status,
            "new_status": review.new_status,
            "decision": review.decision,
            "notes": review.notes,
            "reviewer": review.reviewer,
            "created_at": review.created_at,
        }
        for review in reviews
    ]


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
        return {
            "error": "Report not found."
        }

    return {
        "report_id": f"CV-{report.id:06d}",
        "platform": report.platform,
        "url": report.url,
        "reason": report.reason,
        "description": report.description,
        "status": report.status,
        "risk_level": report.risk_level,
        "risk_score": report.risk_score,
        "review_status": report.review_status,
        "created_at": report.created_at,
    }
