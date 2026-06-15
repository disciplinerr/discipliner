"""email verification: users.is_verified + email_verification_tokens

Revision ID: 0009
Revises: 0008
Create Date: 2026-06-14
"""

from alembic import op
import sqlalchemy as sa

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Existing accounts predate verification — grandfather them in as verified
    # (server_default="true") so they aren't locked out. New rows are set to
    # False explicitly by the register endpoint.
    op.add_column(
        "users",
        sa.Column(
            "is_verified",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),
    )
    # New sign-ups must verify; drop the grandfather default at the DB level.
    op.alter_column("users", "is_verified", server_default="false")

    op.create_table(
        "email_verification_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token", sa.String(128), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_email_verification_tokens_token", "email_verification_tokens", ["token"]
    )
    op.create_index(
        "ix_email_verification_tokens_user_id", "email_verification_tokens", ["user_id"]
    )


def downgrade() -> None:
    op.drop_index(
        "ix_email_verification_tokens_token", table_name="email_verification_tokens"
    )
    op.drop_index(
        "ix_email_verification_tokens_user_id", table_name="email_verification_tokens"
    )
    op.drop_table("email_verification_tokens")
    op.drop_column("users", "is_verified")
