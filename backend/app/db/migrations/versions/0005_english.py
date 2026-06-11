"""english vocabulary tables

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-11
"""

from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "english_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("term", sa.String(120), nullable=False),
        sa.Column("term_pt", sa.String(120), nullable=True),
        sa.Column("definition_en", sa.Text(), nullable=False),
        sa.Column("definition_pt", sa.Text(), nullable=False),
        sa.Column("example_sentence", sa.Text(), nullable=True),
        sa.Column("category", sa.String(60), nullable=False),
        sa.Column(
            "difficulty",
            sa.Enum("beginner", "intermediate", "advanced", name="difficulty"),
            nullable=False,
        ),
        sa.Column("source", sa.String(30), nullable=False, server_default="seed"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "english_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("english_items.id"), nullable=False),
        sa.Column("ease", sa.Float(), nullable=False, server_default="2.5"),
        sa.Column("interval_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("repetitions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("last_reviewed", sa.Date(), nullable=True),
        sa.UniqueConstraint("user_id", "item_id", name="uq_english_progress_user_item"),
    )
    op.create_index("ix_english_progress_user_id", "english_progress", ["user_id"])

    op.create_table(
        "english_attempts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("english_items.id"), nullable=False),
        sa.Column("exercise_type", sa.String(30), nullable=False),
        sa.Column("correct", sa.Boolean(), nullable=False),
        sa.Column("attempted_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_english_attempts_user_id", "english_attempts", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_english_attempts_user_id", table_name="english_attempts")
    op.drop_table("english_attempts")
    op.drop_index("ix_english_progress_user_id", table_name="english_progress")
    op.drop_table("english_progress")
    op.drop_table("english_items")
