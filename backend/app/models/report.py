from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    platform: Mapped[str] = mapped_column(
        String(50),
    )

    url: Mapped[str] = mapped_column(
        String(2048),
    )

    reason: Mapped[str] = mapped_column(
        String(100),
    )

    description: Mapped[str] = mapped_column(
        Text,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="received",
    )

    risk_level: Mapped[str] = mapped_column(
        String(20),
        default="medium",
    )

    risk_score: Mapped[int] = mapped_column(
        default=0,
    )

    review_status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )