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


class TransactionKind(str, enum.Enum):
    """Cash flow direction of a money movement."""

    EXPENSE = "EXPENSE"
    INCOME = "INCOME"


class IncomeKind(str, enum.Enum):
    """Type of a recurring monthly income source."""

    SALARY = "SALARY"      # salário
    BENEFIT = "BENEFIT"    # benefícios: VR, VT, etc.
    OTHER = "OTHER"        # outras rendas fixas


class BudgetGroup(str, enum.Enum):
    """50/30/20 rule buckets used to balance a monthly budget."""

    NEEDS = "NEEDS"      # essentials: rent, food, bills (target ~50%)
    WANTS = "WANTS"      # lifestyle: leisure, dining out (target ~30%)
    SAVINGS = "SAVINGS"  # savings + debt payoff (target ~20%)


class RoutineStatus(str, enum.Enum):
    DONE = "DONE"
    LATE = "LATE"
    SKIPPED = "SKIPPED"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
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


class EmailVerificationToken(Base):
    """One-time token emailed on registration to prove control of the address.

    Mirrors PasswordResetToken: short-lived, single-use. Consuming a valid token
    flips the owning user's is_verified flag to True.
    """

    __tablename__ = "email_verification_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
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


# ── Finance / expense control ───────────────────────────────────────────────


class ExpenseCategory(Base):
    """A spending category (an "envelope"). Carries its own monthly budget and
    a 50/30/20 group so the overview can roll spending up into Needs/Wants/Savings.
    Seeded with sensible defaults per user on first access; user can add custom ones."""

    __tablename__ = "expense_categories"
    __table_args__ = (UniqueConstraint("user_id", "category_key", name="uq_expense_category_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    category_key: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    emoji: Mapped[str] = mapped_column(String(8), default="💸")
    color: Mapped[str] = mapped_column(String(9), default="#a3a3a3")
    group: Mapped[BudgetGroup] = mapped_column(Enum(BudgetGroup), default=BudgetGroup.NEEDS)
    monthly_budget: Mapped[float] = mapped_column(Float, default=0.0)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    position: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Transaction(Base):
    """A single money movement (expense or income) on a given day."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("expense_categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    kind: Mapped[TransactionKind] = mapped_column(
        Enum(TransactionKind), default=TransactionKind.EXPENSE
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    category: Mapped["ExpenseCategory | None"] = relationship()


class RecurringBill(Base):
    """A fixed monthly obligation ("conta a pagar"): rent, subscriptions, loans.
    Has a due day-of-month; whether it is paid for a given month lives in BillPayment."""

    __tablename__ = "recurring_bills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("expense_categories.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    due_day: Mapped[int] = mapped_column(Integer, nullable=False)  # 1..31
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    category: Mapped["ExpenseCategory | None"] = relationship()


class BillPayment(Base):
    """Marks a RecurringBill as paid for a specific (year, month)."""

    __tablename__ = "bill_payments"
    __table_args__ = (
        UniqueConstraint("bill_id", "year", "month", name="uq_bill_payment_period"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bill_id: Mapped[int] = mapped_column(
        ForeignKey("recurring_bills.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Installment(Base):
    """A financed purchase paid in a fixed number of equal monthly charges
    ("parcelamento"): e.g. 10x of R$200 starting Mar/2026.

    Unlike a RecurringBill (open-ended), an installment plan has a finite span.
    The schedule is fully derived from (start_year, start_month, total_installments)
    — we don't store one row per charge; the service projects it onto any month
    and computes which installment number falls there and how many remain."""

    __tablename__ = "installments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("expense_categories.id", ondelete="SET NULL"), nullable=True
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    installment_amount: Mapped[float] = mapped_column(Float, nullable=False)  # value per month
    total_installments: Mapped[int] = mapped_column(Integer, nullable=False)  # how many months
    start_year: Mapped[int] = mapped_column(Integer, nullable=False)
    start_month: Mapped[int] = mapped_column(Integer, nullable=False)  # 1..12
    due_day: Mapped[int] = mapped_column(Integer, default=1)  # day-of-month each charge lands
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    category: Mapped["ExpenseCategory | None"] = relationship()


class RecurringIncome(Base):
    """A fixed monthly income source ("renda fixa"): salary or a benefit like
    VR/VT. Unlike an INCOME Transaction (a one-off cash movement on a date), this
    is recurring and counts toward every month's total income without re-entry."""

    __tablename__ = "recurring_incomes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    kind: Mapped[IncomeKind] = mapped_column(Enum(IncomeKind), default=IncomeKind.SALARY)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SavingsGoal(Base):
    """A savings target the user works toward ("meta de economia"): a name, a
    target amount, and the amount accumulated so far. Progress is tracked by
    editing current_amount (e.g. via the contribute endpoint)."""

    __tablename__ = "savings_goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    target_amount: Mapped[float] = mapped_column(Float, nullable=False)
    current_amount: Mapped[float] = mapped_column(Float, default=0.0)
    emoji: Mapped[str] = mapped_column(String(8), default="🎯")
    color: Mapped[str] = mapped_column(String(9), default="#4ade80")
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
