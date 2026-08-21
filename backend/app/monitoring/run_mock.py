from datetime import datetime, timezone

from app.core.database import SessionLocal

from app.models.monitoring_run import (
    MonitoringRun,
)

from app.monitoring.collectors.mock import (
    MockInstagramCollector,
)

from app.monitoring.engine import (
    process_candidates,
)


def main():
    collector = MockInstagramCollector()

    db = SessionLocal()

    monitoring_run = MonitoringRun(
        platform=collector.platform,
        source_channel=collector.channel,
        status="running",
    )

    db.add(monitoring_run)
    db.commit()
    db.refresh(monitoring_run)

    try:
        candidates = collector.collect()

        monitoring_run.candidates_found = len(
            candidates
        )

        print(
            f"ChildSafe monitoring found "
            f"{len(candidates)} candidate(s)."
        )

        results = process_candidates(
            candidates=candidates,
            db=db,
        )

        reports_created = 0
        duplicates_skipped = 0
        candidates_relevant = 0
        candidates_ignored = 0

        for result in results:
            print()

            # --------------------------------------------------
            # Candidate ignored by detector
            # --------------------------------------------------

            if result.get("status") == "ignored":
                candidates_ignored += 1

                print(
                    "Candidate ignored."
                )

                detection = result.get(
                    "detection",
                    {}
                )

                print(
                    "Confidence:",
                    detection.get(
                        "confidence",
                        0,
                    ),
                )

                print(
                    "Signals:",
                    detection.get(
                        "signals",
                        [],
                    ),
                )

                continue

            # --------------------------------------------------
            # Relevant candidate, but duplicate
            # --------------------------------------------------

            if result.get("status") == "duplicate":
                candidates_relevant += 1
                duplicates_skipped += 1

                print(
                    "Duplicate skipped:",
                    result["report_id"],
                )

                print(
                    result["message"]
                )

                continue

            # --------------------------------------------------
            # Relevant candidate created a new report
            # --------------------------------------------------

            candidates_relevant += 1
            reports_created += 1

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

        # ------------------------------------------------------
        # Save monitoring-run metrics
        # ------------------------------------------------------

        monitoring_run.candidates_relevant = (
            candidates_relevant
        )

        monitoring_run.candidates_ignored = (
            candidates_ignored
        )

        monitoring_run.reports_created = (
            reports_created
        )

        monitoring_run.duplicates_skipped = (
            duplicates_skipped
        )

        monitoring_run.status = "completed"

        monitoring_run.finished_at = (
            datetime.now(timezone.utc)
        )

        db.commit()

        # ------------------------------------------------------
        # Terminal summary
        # ------------------------------------------------------

        print()

        print(
            "Monitoring run completed:",
            monitoring_run.id,
        )

        print(
            "Candidates:",
            monitoring_run.candidates_found,
        )

        print(
            "Relevant:",
            monitoring_run.candidates_relevant,
        )

        print(
            "Ignored:",
            monitoring_run.candidates_ignored,
        )

        print(
            "Reports created:",
            monitoring_run.reports_created,
        )

        print(
            "Duplicates:",
            monitoring_run.duplicates_skipped,
        )

        print(
            "Errors:",
            monitoring_run.errors_count,
        )

    except Exception as exc:
        db.rollback()

        monitoring_run.status = "failed"
        monitoring_run.errors_count = 1
        monitoring_run.error_message = str(exc)

        monitoring_run.finished_at = (
            datetime.now(timezone.utc)
        )

        db.add(monitoring_run)
        db.commit()

        print(
            "Monitoring run failed:",
            exc,
        )

        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()