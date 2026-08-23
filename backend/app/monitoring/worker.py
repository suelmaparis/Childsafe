import time

from app.core.settings import (
    MONITORING_ENABLED,
    MONITORING_INTERVAL_MINUTES,
)

from app.monitoring.registry import (
    get_enabled_collectors,
)

from app.monitoring.runner import (
    run_collector,
)

from app.monitoring.heartbeat import (
    update_worker_heartbeat,
)


def run_cycle():
    collectors = get_enabled_collectors()

    if not collectors:
        print(
            "No monitoring collectors enabled."
        )
        return

    print(
        f"Starting monitoring cycle with "
        f"{len(collectors)} collector(s)."
    )

    for collector in collectors:
        try:
            run_collector(
                collector
            )

        except Exception as exc:
            print(
                f"Collector failed: "
                f"{collector.channel}"
            )
            print(exc)


def main():
    if not MONITORING_ENABLED:
        print(
            "ChildSafe monitoring is disabled."
        )
        return

    interval_seconds = (
        MONITORING_INTERVAL_MINUTES * 60
    )

    print(
        "ChildSafe monitoring worker started."
    )

    print(
        f"Interval: "
        f"{MONITORING_INTERVAL_MINUTES} minute(s)."
    )

    update_worker_heartbeat(
        "running"
    )

    try:
        while True:
            update_worker_heartbeat(
                "running"
            )

            run_cycle()

            print()
            print(
                f"Next monitoring cycle in "
                f"{MONITORING_INTERVAL_MINUTES} minute(s)."
            )

            time.sleep(
                interval_seconds
            )

    except KeyboardInterrupt:
        update_worker_heartbeat(
            "stopped"
        )

        print()
        print(
            "ChildSafe monitoring worker stopped."
        )


if __name__ == "__main__":
    main()