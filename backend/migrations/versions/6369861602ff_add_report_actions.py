"""add report actions

Revision ID: 6369861602ff
Revises: 4b30b048951d
Create Date: 2026-09-08 15:11:53.833901

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6369861602ff'
down_revision: Union[str, Sequence[str], None] = '4b30b048951d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "report_actions",
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
            "action_type",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "notes",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "external_reference",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "created_by_reviewer_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["created_by_reviewer_id"],
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
        op.f("ix_report_actions_id"),
        "report_actions",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_report_actions_report_id"),
        "report_actions",
        ["report_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_report_actions_report_id"),
        table_name="report_actions",
    )

    op.drop_index(
        op.f("ix_report_actions_id"),
        table_name="report_actions",
    )

    op.drop_table(
        "report_actions"
    )