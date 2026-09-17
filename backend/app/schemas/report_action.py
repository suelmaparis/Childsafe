from datetime import datetime

from pydantic import BaseModel, Field


class ReportActionCreate(BaseModel):
    action_type: str = Field(
        min_length=1,
        max_length=50,
    )

    notes: str | None = Field(
        default=None,
        max_length=5000,
    )

    external_reference: str | None = Field(
        default=None,
        max_length=255,
    )
    platform: str | None = Field(
    default=None,
    max_length=50,
    )

    destination: str | None = Field(
        default=None,
        max_length=255,
    )

    external_result: str | None = Field(
        default=None,
        max_length=5000,
    )


class ReportActionUpdate(BaseModel):
    status: str = Field(
        min_length=1,
        max_length=30,
    )

    notes: str | None = Field(
        default=None,
        max_length=5000,
    )

    external_reference: str | None = Field(
        default=None,
        max_length=255,
    )
    platform: str | None = Field(
    default=None,
    max_length=50,
    )

    destination: str | None = Field(
        default=None,
        max_length=255,
    )

    external_result: str | None = Field(
        default=None,
        max_length=5000,
    )


class ReportActionResponse(BaseModel):
    id: int
    report_id: int

    action_type: str
    status: str

    notes: str | None
    external_reference: str | None

    created_by_reviewer_id: int

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }
    platform: str | None
    destination: str | None
    external_result: str | None

    submitted_at: datetime | None
    responded_at: datetime | None
