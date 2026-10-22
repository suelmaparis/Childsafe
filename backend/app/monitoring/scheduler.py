
import logging
import os
import threading
import time
from datetime import datetime, timezone, timedelta
from app.monitoring.runner import run_collector
from app.monitoring.heartbeat import update_worker_heartbeat
from sqlalchemy import text

from app.core.database import engine
from app.core.settings import (
    MONITORING_ENABLED,
    MONITORING_INTERVAL_MINUTES,
)

logger = logging.getLogger(__name__)

MONITORING_LOCK_ID = 374221


def try_acquire_monitoring_lock(connection):
    if connection.dialect.name != "postgresql":
        return False

    result = connection.execute(
        text("SELECT pg_try_advisory_lock(:lock_id)"),
        {"lock_id": MONITORING_LOCK_ID},
    )
    return bool(result.scalar())


def release_monitoring_lock(connection):
    connection.execute(
        text("SELECT pg_advisory_unlock(:lock_id)"),
        {"lock_id": MONITORING_LOCK_ID},
    )


def monitoring_ran_recently(connection) -> bool:
    interval_seconds = max(
        60,
        MONITORING_INTERVAL_MINUTES * 60,
    )

    cutoff = datetime.now(timezone.utc) - timedelta(
        seconds=interval_seconds
    )

    result = connection.execute(
        text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM monitoring_runs
                WHERE source_channel = :channel
                    AND status IN ('running', 'completed')
                    AND started_at >= :cutoff
            )
            """
        ),
        {
            "channel": "meta_instagram_collector",
            "cutoff": cutoff,
        },
    )

    return bool(result.scalar())


def run_scheduled_monitoring():
    from app.monitoring.registry import get_enabled_collectors
    from app.monitoring.runner import run_collector

    if engine.dialect.name != "postgresql":
        logger.info("PostgreSQL required for scheduled monitoring.")
        return False

    with engine.connect().execution_options(
        isolation_level="AUTOCOMMIT"
    ) as connection:
        if not try_acquire_monitoring_lock(connection):
            logger.info("Another monitoring cycle is running.")
            return False

        try:
            if monitoring_ran_recently(connection):

                logger.info("Monitoring ran recently. Skipping.")
                return False
            update_worker_heartbeat("running")
            collectors = get_enabled_collectors()

            all_succeeded = True

            for collector in collectors:
                try:
                    run_collector(collector)
                except Exception:
                    all_succeeded = False
                    logger.exception(
                        "Collector failed: %s",
                        collector.channel,
                    )

            return all_succeeded

        finally:
            release_monitoring_lock(connection)


def monitoring_scheduler_loop(stop_event: threading.Event):
    if not (
        MONITORING_ENABLED
        and os.getenv(
            "CHILDSAFE_WEB_SCHEDULER_ENABLED",
            "false",
        ).lower() == "true"
    ):
        logger.info("Web monitoring scheduler is disabled.")
        return

    interval_seconds = max(
        60,
        MONITORING_INTERVAL_MINUTES * 60,
    )

    logger.info(
        "Monitoring scheduler started. Interval: %s minutes.",
        MONITORING_INTERVAL_MINUTES,
    )

    next_run = time.monotonic()

    while not stop_event.wait(60):
        try:
            update_worker_heartbeat("running")

            if time.monotonic() >= next_run:
                run_scheduled_monitoring()
                next_run = time.monotonic() + interval_seconds

        except Exception:
            logger.exception(
                "Unexpected error in scheduled monitoring."
            )
    logger.info("Monitoring scheduler stopped.")
