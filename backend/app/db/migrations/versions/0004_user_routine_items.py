"""add user_routine_items table

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-11
"""

from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_routine_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("item_key", sa.String(64), nullable=False),
        sa.Column("label", sa.String(255), nullable=False),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "item_key", name="uq_user_routine_item"),
    )
    op.create_index("ix_user_routine_items_user_id", "user_routine_items", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_user_routine_items_user_id", table_name="user_routine_items")
    op.drop_table("user_routine_items")
