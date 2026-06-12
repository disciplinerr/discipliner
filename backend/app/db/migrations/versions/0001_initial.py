"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

# create_type=False: types are created explicitly once in upgrade() because
# the difficulty enum is shared by two tables.
difficulty_enum = postgresql.ENUM(
    "beginner", "intermediate", "advanced", name="difficulty", create_type=False
)
result_enum = postgresql.ENUM(
    "PASS", "FAIL", "PARTIAL", "PENDING", name="submissionresult", create_type=False
)
routine_status_enum = postgresql.ENUM(
    "DONE", "LATE", "SKIPPED", name="routinestatus", create_type=False
)


def upgrade() -> None:
    bind = op.get_bind()
    difficulty_enum.create(bind, checkfirst=True)
    result_enum.create(bind, checkfirst=True)
    routine_status_enum.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("current_phase", sa.Integer(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "trail_phases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("number", sa.Integer(), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("weeks", sa.String(64), nullable=False),
        sa.Column("topics", sa.Text(), nullable=False),
        sa.Column("exercises", sa.Text(), nullable=False),
    )

    op.create_table(
        "daily_challenges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("math_problem", sa.Text(), nullable=False),
        sa.Column("programming_task", sa.Text(), nullable=False),
        sa.Column("difficulty", difficulty_enum, nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("expected_output_example", sa.Text(), nullable=False),
        sa.Column("constraints", sa.Text(), nullable=False),
        sa.UniqueConstraint("user_id", "date", name="uq_challenge_user_date"),
    )
    op.create_index("ix_daily_challenges_user_id", "daily_challenges", ["user_id"])

    op.create_table(
        "challenge_submissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "challenge_id", sa.Integer(), sa.ForeignKey("daily_challenges.id"), nullable=False
        ),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("math_derivation", sa.Text(), nullable=False),
        sa.Column("code_submission", sa.Text(), nullable=False),
        sa.Column("result", result_enum, nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_challenge_submissions_challenge_id", "challenge_submissions", ["challenge_id"]
    )
    op.create_index("ix_challenge_submissions_user_id", "challenge_submissions", ["user_id"])

    op.create_table(
        "routine_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("item_key", sa.String(64), nullable=False),
        sa.Column("status", routine_status_enum, nullable=False),
        sa.Column("logged_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "date", "item_key", name="uq_routine_user_date_item"),
    )
    op.create_index("ix_routine_logs_user_id", "routine_logs", ["user_id"])

    op.create_table(
        "trail_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("phase_id", sa.Integer(), sa.ForeignKey("trail_phases.id"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.UniqueConstraint("user_id", "phase_id", name="uq_progress_user_phase"),
    )
    op.create_index("ix_trail_progress_user_id", "trail_progress", ["user_id"])

    op.create_table(
        "trail_exercises",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("phase_id", sa.Integer(), sa.ForeignKey("trail_phases.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("exercise_key", sa.String(255), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint(
            "user_id", "phase_id", "exercise_key", name="uq_exercise_user_phase_key"
        ),
    )
    op.create_index("ix_trail_exercises_user_id", "trail_exercises", ["user_id"])

    op.create_table(
        "fallback_challenges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("math_problem", sa.Text(), nullable=False),
        sa.Column("programming_task", sa.Text(), nullable=False),
        sa.Column("difficulty", difficulty_enum, nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("expected_output_example", sa.Text(), nullable=False),
        sa.Column("constraints", sa.Text(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("fallback_challenges")
    op.drop_table("trail_exercises")
    op.drop_table("trail_progress")
    op.drop_table("routine_logs")
    op.drop_table("challenge_submissions")
    op.drop_table("daily_challenges")
    op.drop_table("trail_phases")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    difficulty_enum.drop(op.get_bind(), checkfirst=True)
    result_enum.drop(op.get_bind(), checkfirst=True)
    routine_status_enum.drop(op.get_bind(), checkfirst=True)
