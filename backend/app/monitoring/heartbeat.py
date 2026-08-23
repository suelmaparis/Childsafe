from datetime import datetime, timezone

from app.core.database import SessionLocal
from app.models.monitoring_worker_status import (
    MonitoringWorkerStatus,
)


def update_worker_heartbeat(
    status: str = "running",
):
    db = SessionLocal()

    try:
        now = datetime.now(timezone.utc)

        worker = (
            db.query(MonitoringWorkerStatus)
            .filter(
                MonitoringWorkerStatus.id == 1
            )
            .first()
        )

        if worker is None:
            worker = MonitoringWorkerStatus(
                id=1,
                status=status,
                started_at=(
                    now
                    if status == "running"
                    else None
                ),
                last_heartbeat=now,
                updated_at=now,
            )

            db.add(worker)

        else:
            worker.status = status
            worker.last_heartbeat = now
            worker.updated_at = now

            if (
                status == "running"
                and worker.started_at is None
            ):
                worker.started_at = now

        db.commit()

    finally:
        db.close()