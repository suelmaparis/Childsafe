"""prevent duplicate chat reports

Revision ID: 8262e0974771
Revises: 92ac3a9ae323
Create Date: 2026-10-16 13:35:13.306436

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8262e0974771'
down_revision: Union[str, Sequence[str], None] = '92ac3a9ae323'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Prevent duplicate submissions from the public AI chat."""
    op.create_index(
        "uq_reports_chat_submission",
        "reports",
        ["source_reference"],
        unique=True,
        sqlite_where=sa.text(
            "source_type = 'chat_report' "
            "AND source_channel = 'public_ai_chat' "
            "AND source_reference IS NOT NULL"
        ),
    )


def downgrade() -> None:
    """Remove chat submission uniqueness protection."""
    op.drop_index(
        "uq_reports_chat_submission",
        table_name="reports",
    )