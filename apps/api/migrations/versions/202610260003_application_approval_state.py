"""separate candidate approval from verified application submission.

Revision ID: 202610260003
Revises: 202610110002
Create Date: 2026-10-26 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "202610260003"
down_revision = "202610110002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("applications", sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("applications", "approved_at")
