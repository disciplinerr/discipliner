"""make math_derivation nullable in challenge_submissions

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-11
"""

from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "challenge_submissions",
        "math_derivation",
        existing_type=sa.Text(),
        nullable=True,
    )


def downgrade() -> None:
    op.execute("UPDATE challenge_submissions SET math_derivation = '' WHERE math_derivation IS NULL")
    op.alter_column(
        "challenge_submissions",
        "math_derivation",
        existing_type=sa.Text(),
        nullable=False,
    )
