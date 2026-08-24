from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.api.auth import require_role

from app.core.database import SessionLocal

from app.core.settings import (
    MOCK_INSTAGRAM_ENABLED,
    META_INSTAGRAM_ENABLED,
    META_FACEBOOK_ENABLED,
    META_ACCESS_TOKEN,
    META_APP_ID,
    META_APP_SECRET,
    MONITORING_ENABLED,
    MONITORING_INTERVAL_MINUTES,
)

from app.models.monitoring_run import (
    MonitoringRun,
)

from app.models.monitoring_worker_status import (
    MonitoringWorkerStatus,
)

from app.models.reviewer import (
    Reviewer,
)


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


def meta_is_configured() -> bool:
    return all(
        [
            META_ACCESS_TOKEN,
            META_APP_ID,
            META_APP_SECRET,
        ]
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
            now = datetime.now(
                timezone.utc
            )

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
            detail=(
                "limit must be between "
                "1 and 100."
            ),
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



def get_last_run_for_collector(
    db: Session,
    source_channel: str,
):
    return (
        db.query(MonitoringRun)
        .filter(
            MonitoringRun.source_channel
            == source_channel
        )
        .order_by(
            MonitoringRun.id.desc()
        )
        .first()
    )
@router.get("/status")
def monitoring_status(
    current_reviewer: Reviewer = Depends(
        require_role(
            "admin",
            "senior_reviewer",
        )
    ),
    db: Session = Depends(get_db),
):
    meta_configured = meta_is_configured()
    worker = get_worker_status()

    mock_last_run = get_last_run_for_collector(
        db,
        "mock_instagram_collector",
    )

    meta_instagram_last_run = (
        get_last_run_for_collector(
            db,
            "meta_instagram_collector",
        )
    )

    meta_facebook_last_run = (
        get_last_run_for_collector(
            db,
            "meta_facebook_collector",
        )
    )

    mock_status = (
        "disabled"
        if not MOCK_INSTAGRAM_ENABLED
        else (
            "error"
            if (
                mock_last_run
                and mock_last_run.status == "failed"
            )
            else "active"
        )
    )

    return {
        "monitoring_enabled": MONITORING_ENABLED,
        "interval_minutes": (
            MONITORING_INTERVAL_MINUTES
        ),
        "worker": worker,

        "collectors": [
            {
                "name": "mock_instagram_collector",
                "platform": "Instagram",
                "status": mock_status,
                "mode": "mock",

                "last_run_id": (
                    mock_last_run.id
                    if mock_last_run
                    else None
                ),

                "last_error": (
                    mock_last_run.error_message
                    if (
                        mock_last_run
                        and mock_last_run.status == "failed"
                    )
                    else None
                ),
            },

            {
                "name": "meta_instagram_collector",
                "platform": "Instagram",

                "status": (
                    "not_configured"
                    if not meta_configured
                    else (
                        "disabled"
                        if not META_INSTAGRAM_ENABLED
                        else (
                            "error"
                            if (
                                meta_instagram_last_run
                                and
                                meta_instagram_last_run.status
                                == "failed"
                            )
                            else "active"
                        )
                    )
                ),

                "mode": "api",

                "last_run_id": (
                    meta_instagram_last_run.id
                    if meta_instagram_last_run
                    else None
                ),

                "last_error": (
                    meta_instagram_last_run.error_message
                    if (
                        meta_instagram_last_run
                        and
                        meta_instagram_last_run.status
                        == "failed"
                    )
                    else None
                ),
            },

            {
                "name": "meta_facebook_collector",
                "platform": "Facebook",

                "status": (
                    "not_configured"
                    if not meta_configured
                    else (
                        "disabled"
                        if not META_FACEBOOK_ENABLED
                        else (
                            "error"
                            if (
                                meta_facebook_last_run
                                and
                                meta_facebook_last_run.status
                                == "failed"
                            )
                            else "active"
                        )
                    )
                ),

                "mode": "api",

                "last_run_id": (
                    meta_facebook_last_run.id
                    if meta_facebook_last_run
                    else None
                ),

                "last_error": (
                    meta_facebook_last_run.error_message
                    if (
                        meta_facebook_last_run
                        and
                        meta_facebook_last_run.status
                        == "failed"
                    )
                    else None
                ),
            },
        ],
    }