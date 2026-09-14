from datetime import datetime

from pydantic import (
    BaseModel,
    Field,
)


class ReportEvidenceCreate(BaseModel):
    evidence_type: str = Field(
        min_length=1,
        max_length=50,
    )

    source_url: str | None = Field(
        default=None,
        max_length=2048,
    )

    platform: str | None = Field(
        default=None,
        max_length=50,
    )

    external_reference: str | None = Field(
        default=None,
        max_length=255,
    )

    content_hash: str | None = Field(
        default=None,
        max_length=128,
    )

    notes: str | None = Field(
        default=None,
        max_length=5000,
    )


class ReportEvidenceResponse(BaseModel):
    id: int
    report_id: int

    evidence_type: str

    source_url: str | None
    platform: str | None
    external_reference: str | None
    content_hash: str | None
    notes: str | None

    captured_by_reviewer_id: int

    captured_at: datetime
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }