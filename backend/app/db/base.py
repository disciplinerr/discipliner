"""Aggregates Base and all models for Alembic autogenerate."""

from app.db.base_class import Base  # noqa: F401
from app.models import (  # noqa: F401
    BillPayment,
    ChallengeSubmission,
    DailyChallenge,
    ExpenseCategory,
    FallbackChallenge,
    Installment,
    RecurringBill,
    ReviewCard,
    RoutineLog,
    SavingsGoal,
    Transaction,
    TrailExercise,
    TrailPhase,
    TrailProgress,
    User,
)
