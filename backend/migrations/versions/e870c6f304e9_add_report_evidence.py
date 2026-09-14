"""add report evidence

Revision ID: e870c6f304e9
Revises: 6369861602ff
Create Date: 2026-09-13 21:52:50.165304

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e870c6f304e9'
down_revision: Union[str, Sequence[str], None] = '6369861602ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "report_evidence",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "report_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "evidence_type",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "source_url",
            sa.String(length=2048),
            nullable=True,
        ),
        sa.Column(
            "platform",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "external_reference",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "content_hash",
            sa.String(length=128),
            nullable=True,
        ),
        sa.Column(
            "notes",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "captured_by_reviewer_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "captured_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["captured_by_reviewer_id"],
            ["reviewers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["report_id"],
            ["reports.id"],
        ),
        sa.PrimaryKeyConstraint(
            "id"
        ),
    )

    op.create_index(
        op.f("ix_report_evidence_id"),
        "report_evidence",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_report_evidence_report_id"),
        "report_evidence",
        ["report_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_report_evidence_report_id"),
        table_name="report_evidence",
    )

    op.drop_index(
        op.f("ix_report_evidence_id"),
        table_name="report_evidence",
    )

    op.drop_table(
        "report_evidence"
    )