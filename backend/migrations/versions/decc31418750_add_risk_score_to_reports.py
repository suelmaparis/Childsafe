"""Add risk score to reports

Revision ID: decc31418750
Revises: 8a3ea96d536b
Create Date: 2026-08-16 14:42:41.068943

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "decc31418750"
down_revision: Union[str, Sequence[str], None] = "8a3ea96d536b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "reports",
        sa.Column(
            "risk_score",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("reports", "risk_score")