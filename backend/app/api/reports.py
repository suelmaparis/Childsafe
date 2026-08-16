from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.report import Report
from app.models.report_review import ReportReview
from app.services.risk_assessment import assess_risk
from app.services.review_triage import determine_review_priority


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
    # Run the initial rule-based risk assessment.
    assessment = assess_risk(
        report.reason,
        report.description,
    )
    triage = determine_review_priority(assessment.level)

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
    db.commit()
    db.refresh(new_report)

    return {
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
            "risk_level": new_report.risk_level,
            "risk_score": new_report.risk_score,
            "review_status": new_report.review_status,
            "review_priority": triage.priority,
            "recommended_queue": triage.recommended_queue,
            "risk_reasons": assessment.reasons,
            "created_at": new_report.created_at,
        },
    }


@router.get("/")
def list_reports(db: Session = Depends(get_db)):
    reports = db.query(Report).order_by(Report.created_at.desc()).all()

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

@router.patch("/{report_id}/review")
def review_report(
    report_id: int,
    review: ReportReviewCreate,
    db: Session = Depends(get_db),
):
    allowed_statuses = {
        "under_review",
        "reviewed",
        "escalated",
    }

    if review.new_status not in allowed_statuses:
        return {
            "error": "Invalid review status.",
            "allowed_statuses": sorted(allowed_statuses),
        }

    report = db.get(Report, report_id)

    if report is None:
        return {
            "error": "Report not found."
        }

    previous_status = report.review_status

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

@router.get("/{report_id}")
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
):
    report = db.get(Report, report_id)

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