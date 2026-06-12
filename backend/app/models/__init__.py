import enum
from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Difficulty(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class SubmissionResult(str, enum.Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"
    PENDING = "PENDING"


class RoutineStatus(str, enum.Enum):
    DONE = "DONE"
    LATE = "LATE"
    SKIPPED = "SKIPPED"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    current_phase: Mapped[int] = mapped_column(Integer, default=1)

    challenges: Mapped[list["DailyChallenge"]] = relationship(back_populates="user")
    routine_logs: Mapped[list["RoutineLog"]] = relationship(back_populates="user")


class DailyChallenge(Base):
    __tablename__ = "daily_challenges"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_challenge_user_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    math_problem: Mapped[str] = mapped_column(Text, nullable=False)
    programming_task: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[Difficulty] = mapped_column(Enum(Difficulty), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    expected_output_example: Mapped[str] = mapped_column(Text, default="")
    constraints: Mapped[str] = mapped_column(Text, default="")

    user: Mapped["User"] = relationship(back_populates="challenges")
    submissions: Mapped[list["ChallengeSubmission"]] = relationship(back_populates="challenge")


class ChallengeSubmission(Base):
    __tablename__ = "challenge_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    challenge_id: Mapped[int] = mapped_column(
        ForeignKey("daily_challenges.id"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    math_derivation: Mapped[str | None] = mapped_column(Text, nullable=True)
    code_submission: Mapped[str] = mapped_column(Text, nullable=False)
    result: Mapped[SubmissionResult] = mapped_column(
        Enum(SubmissionResult), default=SubmissionResult.PENDING
    )
    reason: Mapped[str] = mapped_column(Text, default="")
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    challenge: Mapped["DailyChallenge"] = relationship(back_populates="submissions")


class RoutineLog(Base):
    __tablename__ = "routine_logs"
    __table_args__ = (
        UniqueConstraint("user_id", "date", "item_key", name="uq_routine_user_date_item"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    item_key: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[RoutineStatus] = mapped_column(Enum(RoutineStatus), nullable=False)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="routine_logs")


class TrailPhase(Base):
    __tablename__ = "trail_phases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    weeks: Mapped[str] = mapped_column(String(64), nullable=False)
    topics: Mapped[str] = mapped_column(Text, nullable=False)  # newline-separated
    exercises: Mapped[str] = mapped_column(Text, nullable=False)  # newline-separated


class TrailProgress(Base):
    __tablename__ = "trail_progress"
    __table_args__ = (UniqueConstraint("user_id", "phase_id", name="uq_progress_user_phase"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    phase_id: Mapped[int] = mapped_column(ForeignKey("trail_phases.id"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    summary: Mapped[str] = mapped_column(Text, default="")

    phase: Mapped["TrailPhase"] = relationship()


class TrailExercise(Base):
    __tablename__ = "trail_exercises"
    __table_args__ = (
        UniqueConstraint("user_id", "phase_id", "exercise_key", name="uq_exercise_user_phase_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phase_id: Mapped[int] = mapped_column(ForeignKey("trail_phases.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    exercise_key: Mapped[str] = mapped_column(String(255), nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ReviewCard(Base):
    """Spaced-repetition card (SM-2-lite) for active recall of trail topics.

    Cards are auto-created from the topics of every phase the user has
    reached. Grading reschedules the card: 0=forgot, 1=hard, 2=good, 3=easy.
    """

    __tablename__ = "review_cards"
    __table_args__ = (
        UniqueConstraint("user_id", "phase_id", "topic", name="uq_review_user_phase_topic"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    phase_id: Mapped[int] = mapped_column(ForeignKey("trail_phases.id"), nullable=False)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    ease: Mapped[float] = mapped_column(Float, default=2.5)
    interval_days: Mapped[int] = mapped_column(Integer, default=0)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    phase: Mapped["TrailPhase"] = relationship()


class UserRoutineItem(Base):
    """Per-user routine item. Seeded from system defaults on first access; user can add custom ones."""

    __tablename__ = "user_routine_items"
    __table_args__ = (UniqueConstraint("user_id", "item_key", name="uq_user_routine_item"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    item_key: Mapped[str] = mapped_column(String(64), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    position: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class FallbackChallenge(Base):
    """Pre-seeded static pool served when the Claude API is unavailable."""

    __tablename__ = "fallback_challenges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    math_problem: Mapped[str] = mapped_column(Text, nullable=False)
    programming_task: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[Difficulty] = mapped_column(Enum(Difficulty), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    expected_output_example: Mapped[str] = mapped_column(Text, default="")
    constraints: Mapped[str] = mapped_column(Text, default="")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class EnglishItem(Base):
    """Vocabulary bank for technical English training."""

    __tablename__ = "english_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    term: Mapped[str] = mapped_column(String(120), nullable=False)
    term_pt: Mapped[str | None] = mapped_column(String(120), nullable=True)
    definition_en: Mapped[str] = mapped_column(Text, nullable=False)
    definition_pt: Mapped[str] = mapped_column(Text, nullable=False)
    example_sentence: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(60), nullable=False)
    difficulty: Mapped[Difficulty] = mapped_column(Enum(Difficulty), nullable=False)
    source: Mapped[str] = mapped_column(String(30), default="seed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class EnglishProgress(Base):
    """SM-2-lite state per user+item for spaced repetition of vocabulary."""

    __tablename__ = "english_progress"
    __table_args__ = (UniqueConstraint("user_id", "item_id", name="uq_english_progress_user_item"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("english_items.id"), nullable=False)
    ease: Mapped[float] = mapped_column(Float, default=2.5)
    interval_days: Mapped[int] = mapped_column(Integer, default=0)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    last_reviewed: Mapped[date | None] = mapped_column(Date, nullable=True)

    item: Mapped["EnglishItem"] = relationship()


class EnglishAttempt(Base):
    """Log of individual exercise answers for stats and session tracking."""

    __tablename__ = "english_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("english_items.id"), nullable=False)
    exercise_type: Mapped[str] = mapped_column(String(30), nullable=False)
    correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    attempted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
