"""english vocabulary tables

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-11
"""

from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use raw SQL so SQLAlchemy does not attempt to recreate the existing
    # 'difficulty' enum type (already created in migration 0001).
    op.execute("""
        CREATE TABLE english_items (
            id          SERIAL PRIMARY KEY,
            term        VARCHAR(120) NOT NULL,
            term_pt     VARCHAR(120),
            definition_en TEXT NOT NULL,
            definition_pt TEXT NOT NULL,
            example_sentence TEXT,
            category    VARCHAR(60) NOT NULL,
            difficulty  difficulty NOT NULL,
            source      VARCHAR(30) NOT NULL DEFAULT 'seed',
            created_at  TIMESTAMPTZ NOT NULL
        )
    """)

    op.execute("""
        CREATE TABLE english_progress (
            id            SERIAL PRIMARY KEY,
            user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            item_id       INTEGER NOT NULL REFERENCES english_items(id) ON DELETE CASCADE,
            ease          FLOAT NOT NULL DEFAULT 2.5,
            interval_days INTEGER NOT NULL DEFAULT 0,
            repetitions   INTEGER NOT NULL DEFAULT 0,
            due_date      DATE NOT NULL,
            last_reviewed DATE,
            CONSTRAINT uq_english_progress_user_item UNIQUE (user_id, item_id)
        )
    """)
    op.execute("CREATE INDEX ix_english_progress_user_id ON english_progress (user_id)")

    op.execute("""
        CREATE TABLE english_attempts (
            id            SERIAL PRIMARY KEY,
            user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            item_id       INTEGER NOT NULL REFERENCES english_items(id) ON DELETE CASCADE,
            exercise_type VARCHAR(30) NOT NULL,
            correct       BOOLEAN NOT NULL,
            attempted_at  TIMESTAMPTZ NOT NULL
        )
    """)
    op.execute("CREATE INDEX ix_english_attempts_user_id ON english_attempts (user_id)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_english_attempts_user_id")
    op.execute("DROP TABLE IF EXISTS english_attempts")
    op.execute("DROP INDEX IF EXISTS ix_english_progress_user_id")
    op.execute("DROP TABLE IF EXISTS english_progress")
    op.execute("DROP TABLE IF EXISTS english_items")
