from app.core.settings import (
    MOCK_INSTAGRAM_ENABLED,
    META_INSTAGRAM_ENABLED,
    META_FACEBOOK_ENABLED,
    META_ACCESS_TOKEN,
    META_APP_ID,
    META_APP_SECRET,
)
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from app.core.settings import (
    MONITORING_ENABLED,
    MONITORING_INTERVAL_MINUTES,
)

from sqlalchemy.orm import Session

from app.api.auth import require_role
from app.core.database import SessionLocal
from app.models.monitoring_run import MonitoringRun
from app.models.reviewer import Reviewer
from datetime import datetime, timezone

from app.core.database import SessionLocal

from app.models.monitoring_worker_status import (
    MonitoringWorkerStatus,
)

router = APIRouter(
    prefix="/monitoring",
    tags=["Monitoring"],
)
def get_worker_status():
    db = SessionLocal()

    try:
        worker = (
            db.query(MonitoringWorkerStatus)
            .filter(
                MonitoringWorkerStatus.id == 1
            )
            .first()
        )

        if worker is None:
            return {
                "status": "unknown",
                "last_heartbeat": None,
                "started_at": None,
            }

        status = worker.status

        if (
            worker.last_heartbeat
            and status == "running"
        ):
            now = datetime.now(timezone.utc)

            heartbeat = (
                worker.last_heartbeat
            )

            if heartbeat.tzinfo is None:
                heartbeat = heartbeat.replace(
                    tzinfo=timezone.utc
                )

            age_seconds = (
                now - heartbeat
            ).total_seconds()

            stale_after = (
                MONITORING_INTERVAL_MINUTES
                * 60
                * 2
            )

            if age_seconds > stale_after:
                status = "stale"

        return {
            "status": status,
            "last_heartbeat": (
                worker.last_heartbeat
            ),
            "started_at": (
                worker.started_at
            ),
        }

    finally:
        db.close()
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

def meta_is_configured() -> bool:
    return all(
        [
            META_ACCESS_TOKEN,
            META_APP_ID,
            META_APP_SECRET,
        ]
    )

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
@router.get("/status")
def monitoring_status(
    current_reviewer: Reviewer = Depends(
        require_role(
            "admin",
            "senior_reviewer",
        )
    ),
):
    meta_configured = (
        meta_is_configured()
    )
    worker = get_worker_status()
    
    return {
        "monitoring_enabled": MONITORING_ENABLED,
        "interval_minutes": (
            MONITORING_INTERVAL_MINUTES
        ),
         "worker": worker,
        "monitoring_enabled": True,

        "collectors": [
            {
                "name": (
                    "mock_instagram_collector"
                ),
                "platform": "Instagram",
                "status": (
                    "active"
                    if MOCK_INSTAGRAM_ENABLED
                    else "disabled"
                ),
                "mode": "mock",
               
            },

            {
                "name": (
                    "meta_instagram_collector"
                ),
                "platform": "Instagram",
                "status": (
                    "active"
                    if (
                        META_INSTAGRAM_ENABLED
                        and meta_configured
                    )
                    else (
                        "not_configured"
                        if not meta_configured
                        else "disabled"
                    )
                ),
                "mode": "api",
            },

            {
                "name": (
                    "meta_facebook_collector"
                ),
                "platform": "Facebook",
                "status": (
                    "active"
                    if (
                        META_FACEBOOK_ENABLED
                        and meta_configured
                    )
                    else (
                        "not_configured"
                        if not meta_configured
                        else "disabled"
                    )
                ),
                "mode": "api",
            },
        ],
    }