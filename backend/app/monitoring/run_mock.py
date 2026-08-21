from app.core.database import SessionLocal

from app.monitoring.collectors.mock import (
    collect_candidates,
)

from app.monitoring.engine import (
    process_candidates,
)


def main():
    candidates = collect_candidates()

    print(
        f"ChildSafe monitoring found "
        f"{len(candidates)} candidate(s)."
    )

    db = SessionLocal()

    try:
        results = process_candidates(
            candidates=candidates,
            db=db,
        )

        for result in results:
            print()

            if result.get("status") == "duplicate":
                print(
                    "Duplicate skipped:",
                    result["report_id"],
                )

                print(
                    result["message"]
                )

                continue

            report = result["report"]

            print(
                "Report created:",
                result["report_id"],
            )

            print(
                "Source:",
                report["source_type"],
            )

            print(
                "Channel:",
                report["source_channel"],
            )

            print(
                "Platform:",
                report["platform"],
            )

            print(
                "Risk:",
                report["risk_level"],
                report["risk_score"],
            )

            ai = report.get(
                "ai_assessment",
                {}
            )

            if ai.get("level"):
                print(
                    "AI risk:",
                    ai["level"],
                    ai["score"],
                )
            else:
                print(
                    "AI risk: unavailable"
                )

    finally:
        db.close()


if __name__ == "__main__":
    main()