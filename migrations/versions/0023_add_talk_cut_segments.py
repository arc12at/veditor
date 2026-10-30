"""Add cut_segments JSONB column to talks table.

Revision ID: 0023
Revises: 0022
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0023"
down_revision = "0022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "talks",
        sa.Column(
            "cut_segments",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("talks", "cut_segments")
