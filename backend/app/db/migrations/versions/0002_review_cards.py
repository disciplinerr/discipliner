"""review cards for spaced repetition

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-10

"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "review_cards",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("phase_id", sa.Integer(), sa.ForeignKey("trail_phases.id"), nullable=False),
        sa.Column("topic", sa.String(255), nullable=False),
        sa.Column("ease", sa.Float(), nullable=False),
        sa.Column("interval_days", sa.Integer(), nullable=False),
        sa.Column("repetitions", sa.Integer(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("user_id", "phase_id", "topic", name="uq_review_user_phase_topic"),
    )
    op.create_index("ix_review_cards_user_id", "review_cards", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_review_cards_user_id", table_name="review_cards")
    op.drop_table("review_cards")
