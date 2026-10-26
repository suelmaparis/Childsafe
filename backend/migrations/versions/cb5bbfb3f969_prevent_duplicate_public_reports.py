"""prevent duplicate public reports

Revision ID: cb5bbfb3f969
Revises: cc5fa89f425c
Create Date: 2026-10-26 15:03:17.198075

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb5bbfb3f969'
down_revision: Union[str, Sequence[str], None] = 'cc5fa89f425c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.create_index(
        "uq_reports_public_submission",
        "reports",
        ["source_reference"],
        unique=True,
        sqlite_where=sa.text(
            "source_type = 'public_report' "
            "AND source_channel = 'public_web_form' "
            "AND source_reference IS NOT NULL"
        ),
        postgresql_where=sa.text(
            "source_type = 'public_report' "
            "AND source_channel = 'public_web_form' "
            "AND source_reference IS NOT NULL"
        ),
    )


def downgrade():
    op.drop_index(
        "uq_reports_public_submission",
        table_name="reports",
    )