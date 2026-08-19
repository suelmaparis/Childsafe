from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ReviewerAuditLog(Base):
    __tablename__ = "reviewer_audit_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    actor_reviewer_id: Mapped[int] = mapped_column(
        ForeignKey("reviewers.id"),
        index=True,
    )

    target_reviewer_id: Mapped[int] = mapped_column(
        ForeignKey("reviewers.id"),
        index=True,
    )

    action: Mapped[str] = mapped_column(
        String(50),
    )

    details: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
