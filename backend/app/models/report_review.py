from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ReportReview(Base):
    __tablename__ = "report_reviews"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    report_id: Mapped[int] = mapped_column(
        ForeignKey("reports.id"),
        index=True,
    )

    previous_status: Mapped[str] = mapped_column(
        String(30),
    )

    new_status: Mapped[str] = mapped_column(
        String(30),
    )

    decision: Mapped[str] = mapped_column(
        String(50),
    )

    notes: Mapped[str] = mapped_column(
        Text,
    )

    reviewer: Mapped[str] = mapped_column(
        String(100),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
