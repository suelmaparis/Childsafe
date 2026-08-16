"""Add report risk and review status

Revision ID: 8a3ea96d536b
Revises:
Create Date: 2026-08-16 14:13:03.698876

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8a3ea96d536b"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "reports",
        sa.Column(
            "risk_level",
            sa.String(length=20),
            nullable=False,
            server_default="medium",
        ),
    )

    op.add_column(
        "reports",
        sa.Column(
            "review_status",
            sa.String(length=30),
            nullable=False,
            server_default="pending",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("reports", "review_status")
    op.drop_column("reports", "risk_level")