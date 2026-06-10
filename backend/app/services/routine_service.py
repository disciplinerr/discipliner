from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import RoutineLog, RoutineStatus

ROUTINE_ITEMS: dict[str, str] = {
    "wake_up_before_7": "Wake up before 7:00 AM",
    "no_unnecessary_spending": "No unnecessary spending today",
    "study_session": "Study session completed (minimum 1 hour)",
    "daily_challenge": "Daily challenge attempted",
    "trail_review": "Review one concept from the learning trail",
}


def log_item_if_absent(
    db: Session,
    user_id: int,
    item_key: str,
    status: RoutineStatus = RoutineStatus.DONE,
) -> None:
    """Auto-log a routine item from another action (e.g. grading a review card
    logs `trail_review`). No-op if already logged. Does not commit."""
    existing = db.scalar(
        select(RoutineLog).where(
            RoutineLog.user_id == user_id,
            RoutineLog.date == date.today(),
            RoutineLog.item_key == item_key,
        )
    )
    if existing is None:
        db.add(
            RoutineLog(
                user_id=user_id,
                date=date.today(),
                item_key=item_key,
                status=status,
                logged_at=datetime.now(timezone.utc),
            )
        )
