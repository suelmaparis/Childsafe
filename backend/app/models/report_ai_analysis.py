from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ReportAIAnalysis(Base):
    __tablename__ = "report_ai_analyses"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    report_id: Mapped[int] = mapped_column(
        ForeignKey("reports.id"),
        index=True,
    )

    model: Mapped[str] = mapped_column(
        String(100),
    )

    level: Mapped[str] = mapped_column(
        String(20),
    )

    score: Mapped[int] = mapped_column(
        Integer,
    )

    reasons: Mapped[str] = mapped_column(
        Text,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )