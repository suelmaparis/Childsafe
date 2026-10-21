"""add_school_signals_to_reports

Revision ID: 574a1b11236a
Revises: d5a2bb32b084
Create Date: 2026-10-21 14:46:57.137319

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '574a1b11236a'
down_revision: Union[str, Sequence[str], None] = 'd5a2bb32b084'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "reports",
        sa.Column(
            "school_signals",
            sa.Text(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        "reports",
        "school_signals",
    )
