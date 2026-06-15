"""finance: store app icon keys instead of OS emojis on categories/goals

Revision ID: 0011
Revises: 0010
Create Date: 2026-06-15
"""

from alembic import op
import sqlalchemy as sa

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None

# emoji -> app icon key (mirrors EMOJI_TO_KEY in frontend lib/icons.tsx)
_EMOJI_MAP = {
    "🎓": "education",
    "🏠": "housing",
    "🛒": "groceries",
    "🚌": "transport",
    "💡": "utilities",
    "🩺": "health",
    "🍽️": "dining",
    "🎮": "leisure",
    "🛍️": "shopping",
    "📺": "subscriptions",
    "💰": "savings",
    "💳": "debt",
    "🎯": "target",
    "💸": "money",
}


def _convert(table: str, fallback: str) -> None:
    bind = op.get_bind()
    # Widen the column so icon keys fit.
    op.alter_column(table, "emoji", type_=sa.String(32))
    # Map known emojis to keys.
    for emoji, key in _EMOJI_MAP.items():
        bind.execute(
            sa.text(f"UPDATE {table} SET emoji = :key WHERE emoji = :emoji"),
            {"key": key, "emoji": emoji},
        )
    # Anything left that isn't already a known key becomes the fallback.
    known_keys = sorted(set(_EMOJI_MAP.values()) | {fallback, "tag"})
    bind.execute(
        sa.text(
            f"UPDATE {table} SET emoji = :fb "
            f"WHERE emoji NOT IN :keys"
        ).bindparams(sa.bindparam("keys", expanding=True)),
        {"fb": fallback, "keys": known_keys},
    )


def upgrade() -> None:
    _convert("expense_categories", "tag")
    _convert("savings_goals", "target")


def downgrade() -> None:
    # One-way data migration; just narrow the columns back.
    op.alter_column("expense_categories", "emoji", type_=sa.String(8))
    op.alter_column("savings_goals", "emoji", type_=sa.String(8))
