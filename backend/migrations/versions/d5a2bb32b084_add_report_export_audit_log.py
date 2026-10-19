"""add report export audit log

Revision ID: d5a2bb32b084
Revises: 8262e0974771
Create Date: 2026-10-19 15:16:35.267450

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5a2bb32b084'
down_revision: Union[str, Sequence[str], None] = '8262e0974771'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
def upgrade() -> None:
    """Create the report PDF export audit table."""
    op.create_table(
        "report_export_logs",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "report_id",
            sa.Integer(),
            sa.ForeignKey("reports.id"),
            nullable=False,
        ),
        sa.Column(
            "reviewer_id",
            sa.Integer(),
            sa.ForeignKey("reviewers.id"),
            nullable=False,
        ),
        sa.Column(
            "export_format",
            sa.String(length=10),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Remove the report PDF export audit table."""
    op.drop_table("report_export_logs")