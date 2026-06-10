"""Aggregates Base and all models for Alembic autogenerate."""

from app.db.base_class import Base  # noqa: F401
from app.models import (  # noqa: F401
    ChallengeSubmission,
    DailyChallenge,
    FallbackChallenge,
    ReviewCard,
    RoutineLog,
    TrailExercise,
    TrailPhase,
    TrailProgress,
    User,
)
