"""extend report actions for platform workflow

Revision ID: 9ca230ee50e6
Revises: e870c6f304e9
Create Date: 2026-09-14 13:36:13.741147

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9ca230ee50e6'
down_revision: Union[str, Sequence[str], None] = 'e870c6f304e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "report_actions",
        sa.Column(
            "platform",
            sa.String(length=50),
            nullable=True,
        ),
    )

    op.add_column(
        "report_actions",
        sa.Column(
            "destination",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "report_actions",
        sa.Column(
            "external_result",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "report_actions",
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "report_actions",
        sa.Column(
            "responded_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "report_actions",
        "responded_at",
    )

    op.drop_column(
        "report_actions",
        "submitted_at",
    )

    op.drop_column(
        "report_actions",
        "external_result",
    )

    op.drop_column(
        "report_actions",
        "destination",
    )

    op.drop_column(
        "report_actions",
        "platform",
    )