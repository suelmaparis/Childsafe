from sqlalchemy import text

from app.core.database import engine
from app.monitoring.candidate import MonitoringCandidate
from app.monitoring.detector import detect_candidate
from app.monitoring.signal_extractor import (
    extract_school_signals,
    extract_signals,
)

QUERY = text(
    "SELECT id, platform, url, description "
    "FROM reports "
    "WHERE source_type = 'automated_monitoring' "
    "ORDER BY id"
)


def main():
    with engine.connect() as connection:
        rows = connection.execute(QUERY).fetchall()

    kept = []
    dropped = []

    for report_id, platform, url, description in rows:
        content = description or ""
        signals = extract_signals(content)

        candidate = MonitoringCandidate(
            platform=platform or "",
            url=url or "x",
            description=content,
            source_reference=str(report_id),
            contains_child=signals["contains_child"],
            location_detected=signals["location_detected"],
            volunteer_context=signals["volunteer_context"],
            tourism_context=signals["tourism_context"],
            metadata={"school_signals": extract_school_signals(content)},
        )

        detection = detect_candidate(candidate)

        row = (
            report_id,
            detection["signal_score"],
            detection["signals"],
            content[:120].replace("\n", " "),
        )

        if detection["relevant"]:
            kept.append(row)
        else:
            dropped.append(row)

    print(f"Total: {len(rows)} | Mantidos: {len(kept)} | Descartados: {len(dropped)}")

    for title, group in (("MANTIDOS", kept), ("DESCARTADOS", dropped)):
        print("=" * 40, title)
        for item in group:
            print(item)


if __name__ == "__main__":
    main()
