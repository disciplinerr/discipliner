"""finance: expense categories, transactions, recurring bills, payments

Revision ID: 0007
Revises: 0006
Create Date: 2026-06-14
"""

from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


budget_group = sa.Enum("NEEDS", "WANTS", "SAVINGS", name="budgetgroup")
transaction_kind = sa.Enum("EXPENSE", "INCOME", name="transactionkind")


def upgrade() -> None:
    op.create_table(
        "expense_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("category_key", sa.String(64), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("emoji", sa.String(8), nullable=False, server_default="💸"),
        sa.Column("color", sa.String(9), nullable=False, server_default="#a3a3a3"),
        sa.Column("group", budget_group, nullable=False, server_default="NEEDS"),
        sa.Column("monthly_budget", sa.Float(), nullable=False, server_default="0"),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "category_key", name="uq_expense_category_key"),
    )
    op.create_index(
        "ix_expense_categories_user_id", "expense_categories", ["user_id"]
    )

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "category_id",
            sa.Integer(),
            sa.ForeignKey("expense_categories.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("kind", transaction_kind, nullable=False, server_default="EXPENSE"),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_transactions_user_id", "transactions", ["user_id"])
    op.create_index("ix_transactions_category_id", "transactions", ["category_id"])
    op.create_index("ix_transactions_date", "transactions", ["date"])

    op.create_table(
        "recurring_bills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "category_id",
            sa.Integer(),
            sa.ForeignKey("expense_categories.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("due_day", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_recurring_bills_user_id", "recurring_bills", ["user_id"])

    op.create_table(
        "bill_payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "bill_id",
            sa.Integer(),
            sa.ForeignKey("recurring_bills.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("bill_id", "year", "month", name="uq_bill_payment_period"),
    )
    op.create_index("ix_bill_payments_bill_id", "bill_payments", ["bill_id"])
    op.create_index("ix_bill_payments_user_id", "bill_payments", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_bill_payments_user_id", table_name="bill_payments")
    op.drop_index("ix_bill_payments_bill_id", table_name="bill_payments")
    op.drop_table("bill_payments")

    op.drop_index("ix_recurring_bills_user_id", table_name="recurring_bills")
    op.drop_table("recurring_bills")

    op.drop_index("ix_transactions_date", table_name="transactions")
    op.drop_index("ix_transactions_category_id", table_name="transactions")
    op.drop_index("ix_transactions_user_id", table_name="transactions")
    op.drop_table("transactions")

    op.drop_index("ix_expense_categories_user_id", table_name="expense_categories")
    op.drop_table("expense_categories")

    transaction_kind.drop(op.get_bind(), checkfirst=True)
    budget_group.drop(op.get_bind(), checkfirst=True)
