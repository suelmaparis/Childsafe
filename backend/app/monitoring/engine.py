import logging

from app.core import settings
from app.services.monitored_media_analysis import (
    analyze_monitored_image,
)

logger = logging.getLogger(__name__)
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
        # Automatic image analysis using AWS Rekognition
    if settings.MEDIA_ANALYSIS_ENABLED:
        metadata = candidate.metadata or {}

        media_url = metadata.get("media_url")
        media_type = metadata.get("media_type")

        if media_url and media_type == "IMAGE":
            try:
                assessment = analyze_monitored_image(
                    media_url
                )

                # Preserve the visual assessment for review.
                metadata["visual_assessment"] = {
                    "score": assessment.score,
                    "level": assessment.level,
                    "reasons": assessment.reasons,
                    "details": assessment.details,
                }

                candidate.metadata = metadata

                # Flag high-risk visual findings for review.
                if assessment.level in {"high", "critical"}:
                    detection["relevant"] = True
                    detection["reason"] = (
                        "potential_child_exposure"
                    )
                    detection["signals"] = [
                        *detection.get("signals", []),
                        "visual_risk_requires_review",
                    ]

            except Exception:
                logger.exception(
                    "Automatic image analysis failed."
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

        school_signals=(
            candidate.metadata.get("school_signals")
            if candidate.metadata
            else None
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