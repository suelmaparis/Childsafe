from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MonitoringRun(Base):
    __tablename__ = "monitoring_runs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    platform: Mapped[str] = mapped_column(
        String(50),
    )

    source_channel: Mapped[str] = mapped_column(
        String(100),
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="running",
    )
    
    candidates_found: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    candidates_relevant: Mapped[int] = mapped_column(
    Integer,
    default=0,
)

    candidates_ignored: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    reports_created: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    duplicates_skipped: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    errors_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(
            timezone.utc
        ),
    )

    finished_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
candidates_relevant: Mapped[int] = mapped_column(
    Integer,
    default=0,
)

candidates_ignored: Mapped[int] = mapped_column(
    Integer,
    default=0,
)