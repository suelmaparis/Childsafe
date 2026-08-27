from sqlalchemy.orm import Session

from app.api.reports import (
    ReportCreate,
    create_report_record,
)

from app.models.report import Report

from app.monitoring.candidate import (
    MonitoringCandidate,
)

from app.monitoring.detector import (
    detect_candidate,
)


def process_candidate(
    candidate: MonitoringCandidate,
    db: Session,
):
    """
    Convert automatically discovered content
    into a ChildSafe report.

    Duplicate content is skipped when a report with
    the same platform and URL already exists.
    """

    detection = detect_candidate(
        candidate
    )

    if not detection.get(
        "relevant",
        False,
    ):
        return {
            "status": "ignored",
            "message": (
                "Monitoring candidate was not relevant "
                "enough to create a report."
            ),
            "detection": {
                "confidence": detection.get(
                    "confidence",
                    0.0,
                ),
                "signal_score": detection.get(
                    "signal_score",
                    0,
                ),
                "signals": detection.get(
                    "signals",
                    [],
                ),
                "source": detection.get(
                    "source",
                    "monitoring_detector_v2",
                ),
            },
        }

    existing_report = None

    if candidate.source_reference:
        existing_report = (
            db.query(Report)
            .filter(
                Report.source_channel
                == candidate.source_channel,

                Report.source_reference
                == candidate.source_reference,
            )
            .first()
        )

    if existing_report is None:
        existing_report = (
            db.query(Report)
            .filter(
                Report.platform
                == candidate.platform,

                Report.url
                == candidate.url,
            )
            .first()
        )

    if existing_report is not None:
        return {
            "status": "duplicate",

            "report_id": (
                f"CV-{existing_report.id:06d}"
            ),

            "message": (
                "Monitoring candidate already exists."
            ),

            "detection": {
                "confidence": detection.get(
                    "confidence",
                    0.0,
                ),
                "signal_score": detection.get(
                    "signal_score",
                    0,
                ),
                "signals": detection.get(
                    "signals",
                    [],
                ),
                "source": detection.get(
                    "source",
                    "monitoring_detector_v2",
                ),
            },
        }

    report = ReportCreate(
        platform=candidate.platform,
        url=candidate.url,

        reason=(
            detection.get(
                "reason"
            )
            or candidate.reason
        ),

        description=candidate.description,

        source_type="automated_monitoring",

        source_channel=(
            candidate.source_channel
        ),

        source_reference=(
            candidate.source_reference
        ),

        detection_confidence=(
            detection.get(
                "confidence",
                0.0,
            )
        ),
        detection_signal_score=(
            detection.get(
                "signal_score",
                0,
            )
        ),

        detection_signals=(
            detection.get(
                "signals",
                [],
            )
        ),

        detection_source=(
            detection.get(
                "source",
                "monitoring_detector_v2",
            )
        ),
    )

    return create_report_record(
        report=report,
        db=db,
    )


def process_candidates(
    candidates: list[MonitoringCandidate],
    db: Session,
) -> list[dict]:
    results = []

    for candidate in candidates:
        result = process_candidate(
            candidate=candidate,
            db=db,
        )

        results.append(
            result
        )

    return results