"""add incident location and safety fields

Revision ID: 92ac3a9ae323
Revises: 9ca230ee50e6
Create Date: 2026-10-16 10:36:25.025605

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92ac3a9ae323'
down_revision: Union[str, Sequence[str], None] = '9ca230ee50e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add optional incident and safety fields."""
    op.add_column(
        "reports",
        sa.Column("incident_location", sa.String(500), nullable=True),
    )
    op.add_column(
        "reports",
        sa.Column("reporter_location", sa.String(500), nullable=True),
    )
    op.add_column(
        "reports",
        sa.Column("incident_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "reports",
        sa.Column("is_immediate_danger", sa.Boolean(), nullable=True),
    )


def downgrade() -> None:
    """Remove incident and safety fields."""
    op.drop_column("reports", "is_immediate_danger")
    op.drop_column("reports", "incident_at")
    op.drop_column("reports", "reporter_location")
    op.drop_column("reports", "incident_location")
