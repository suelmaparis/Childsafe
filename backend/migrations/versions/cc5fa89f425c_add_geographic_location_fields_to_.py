"""add geographic location fields to reports

Revision ID: cc5fa89f425c
Revises: 574a1b11236a
Create Date: 2026-10-23 11:34:30.335824

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc5fa89f425c'
down_revision: Union[str, Sequence[str], None] = '574a1b11236a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Acrescenta os campos geográficos às denúncias."""

    op.add_column(
        "reports",
        sa.Column("geo_latitude", sa.Float(), nullable=True),
    )

    op.add_column(
        "reports",
        sa.Column("geo_longitude", sa.Float(), nullable=True),
    )

    op.add_column(
        "reports",
        sa.Column("geo_location_text", sa.Text(), nullable=True),
    )

    op.add_column(
        "reports",
        sa.Column("geo_source", sa.String(150), nullable=True),
    )

    op.add_column(
        "reports",
        sa.Column("geo_source_url", sa.Text(), nullable=True),
    )

    op.add_column(
        "reports",
        sa.Column("geo_coordinate_type", sa.String(50), nullable=True),
    )

    op.add_column(
        "reports",
        sa.Column("geo_verification_status", sa.String(30), nullable=True),
    )


def downgrade() -> None:
    """Remove os campos geográficos."""

    op.drop_column("reports", "geo_verification_status")
    op.drop_column("reports", "geo_coordinate_type")
    op.drop_column("reports", "geo_source_url")
    op.drop_column("reports", "geo_source")
    op.drop_column("reports", "geo_location_text")
    op.drop_column("reports", "geo_longitude")
    op.drop_column("reports", "geo_latitude")