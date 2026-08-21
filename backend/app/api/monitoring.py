from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.api.auth import require_role
from app.core.database import SessionLocal
from app.models.monitoring_run import MonitoringRun
from app.models.reviewer import Reviewer


router = APIRouter(
    prefix="/monitoring",
    tags=["Monitoring"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("/runs")
def list_monitoring_runs(
    limit: int = 20,
    current_reviewer: Reviewer = Depends(
        require_role(
            "admin",
            "senior_reviewer",
        )
    ),
    db: Session = Depends(get_db),
):
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=422,
            detail="limit must be between 1 and 100.",
        )

    runs = (
        db.query(MonitoringRun)
        .order_by(
            MonitoringRun.started_at.desc()
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "run_id": run.id,
            "platform": run.platform,
            "source_channel": (
                run.source_channel
            ),
            "status": run.status,

            "candidates_found": (
                run.candidates_found
            ),

            "candidates_relevant": (
                run.candidates_relevant
            ),

            "candidates_ignored": (
                run.candidates_ignored
            ),

            "reports_created": (
                run.reports_created
            ),

            "duplicates_skipped": (
                run.duplicates_skipped
            ),

            "errors_count": (
                run.errors_count
            ),

            "error_message": (
                run.error_message
            ),

            "started_at": (
                run.started_at
            ),

            "finished_at": (
                run.finished_at
            ),
        }
        for run in runs
    ]