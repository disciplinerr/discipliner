from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import EnglishAttempt, RoutineLog, RoutineStatus, User
from app.services.routine_service import get_active_items

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _routine_streak(db: Session, user_id: int, active_count: int) -> int:
    """Consecutive calendar days ending today where at least 1 item was logged done/late."""
    if active_count == 0:
        return 0
    streak = 0
    today = date.today()
    for offset in range(0, 365):
        d = today - timedelta(days=offset)
        done = db.scalar(
            select(func.count(RoutineLog.id)).where(
                RoutineLog.user_id == user_id,
                RoutineLog.date == d,
                RoutineLog.status.in_([RoutineStatus.DONE, RoutineStatus.LATE]),
            )
        )
        if done and done > 0:
            streak += 1
        else:
            break
    return streak


def _routine_7d(db: Session, user_id: int, active_count: int) -> list[dict]:
    today = date.today()
    result = []
    for offset in range(6, -1, -1):
        d = today - timedelta(days=offset)
        done = db.scalar(
            select(func.count(RoutineLog.id)).where(
                RoutineLog.user_id == user_id,
                RoutineLog.date == d,
                RoutineLog.status.in_([RoutineStatus.DONE, RoutineStatus.LATE]),
            )
        ) or 0
        pct = round(done / active_count * 100) if active_count > 0 else 0
        result.append({"date": d.isoformat(), "done": done, "total": active_count, "pct": min(pct, 100)})
    return result


def _english_accuracy_7d(db: Session, user_id: int) -> int:
    today = date.today()
    since = today - timedelta(days=6)
    total = db.scalar(
        select(func.count(EnglishAttempt.id)).where(
            EnglishAttempt.user_id == user_id,
            EnglishAttempt.attempted_at >= since,
        )
    ) or 0
    if total == 0:
        return 0
    correct = db.scalar(
        select(func.count(EnglishAttempt.id)).where(
            EnglishAttempt.user_id == user_id,
            EnglishAttempt.attempted_at >= since,
            EnglishAttempt.correct.is_(True),
        )
    ) or 0
    return round(correct / total * 100)


@router.get("/stats")
def dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    active_items = get_active_items(db, current_user.id)
    active_count = len(active_items)
    streak = _routine_streak(db, current_user.id, active_count)
    week = _routine_7d(db, current_user.id, active_count)
    english_accuracy = _english_accuracy_7d(db, current_user.id)
    return {
        "routine_streak": streak,
        "routine_7d": week,
        "english_accuracy_7d": english_accuracy,
    }
