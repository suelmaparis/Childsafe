from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ReportExportLog(Base):
    __tablename__ = "report_export_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    report_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reports.id"),
        nullable=False,
        index=True,
    )

    reviewer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reviewers.id"),
        nullable=False,
        index=True,
    )

    export_format: Mapped[str] = mapped_column(
        String(10),
        default="pdf",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
