from app.monitoring.registry import (
    get_enabled_collectors,
)

from app.monitoring.runner import (
    run_collector,
)


def main():
    collectors = get_enabled_collectors()

    if not collectors:
        print(
            "No monitoring collectors enabled."
        )
        return

    print(
        f"ChildSafe found "
        f"{len(collectors)} enabled collector(s)."
    )

    for collector in collectors:
        print(
            f"- {collector.platform}: "
            f"{collector.channel}"
        )

    for collector in collectors:
        run_collector(
            collector
        )


if __name__ == "__main__":
    main()