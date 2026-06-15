"""finance: recurring income sources (salário + benefícios VR/VT)

Revision ID: 0010
Revises: 0009
Create Date: 2026-06-15
"""

from alembic import op
import sqlalchemy as sa

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Let create_table emit the single CREATE TYPE for the enum (default
    # create_type=True). Calling Enum.create() as well would double-create it.
    op.create_table(
        "recurring_incomes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column(
            "kind",
            sa.Enum("SALARY", "BENEFIT", "OTHER", name="incomekind"),
            nullable=False,
            server_default="SALARY",
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_recurring_incomes_user_id", "recurring_incomes", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_recurring_incomes_user_id", table_name="recurring_incomes")
    op.drop_table("recurring_incomes")
    sa.Enum(name="incomekind").drop(op.get_bind(), checkfirst=True)
