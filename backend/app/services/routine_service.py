import uuid
from datetime import date, datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.models import RoutineLog, RoutineStatus, UserRoutineItem

SYSTEM_ROUTINE_ITEMS: dict[str, str] = {
    "wake_up_before_7": "Wake up before 7:00 AM",
    "no_unnecessary_spending": "No unnecessary spending today",
    "study_session": "Study session completed (minimum 1 hour)",
    "daily_challenge": "Daily challenge attempted",
    "trail_review": "Review one concept from the learning trail",
    "english_training": "Technical English session completed",
}


def ensure_items_seeded(db: Session, user_id: int) -> None:
    """Seed system routine items per-key — idempotent even when new items are added."""
    existing_keys = {
        row.item_key
        for row in db.scalars(
            select(UserRoutineItem).where(UserRoutineItem.user_id == user_id)
        )
    }
    max_pos = db.scalar(
        select(func.max(UserRoutineItem.position)).where(UserRoutineItem.user_id == user_id)
    ) or -1

    now = datetime.now(timezone.utc)
    rows = []
    for pos, (key, label) in enumerate(SYSTEM_ROUTINE_ITEMS.items()):
        if key not in existing_keys:
            rows.append({
                "user_id": user_id,
                "item_key": key,
                "label": label,
                "is_system": True,
                "is_active": True,
                "position": max(pos, max_pos + 1),
                "created_at": now,
            })
    if rows:
        # Parallel reads can race to seed the same keys; ON CONFLICT DO NOTHING
        # makes the insert atomic so the loser is ignored instead of raising
        # uq_user_routine_item.
        stmt = pg_insert(UserRoutineItem).values(rows).on_conflict_do_nothing(
            constraint="uq_user_routine_item"
        )
        db.execute(stmt)
        db.commit()


def get_active_items(db: Session, user_id: int) -> list[UserRoutineItem]:
    ensure_items_seeded(db, user_id)
    return list(db.scalars(
        select(UserRoutineItem)
        .where(UserRoutineItem.user_id == user_id, UserRoutineItem.is_active.is_(True))
        .order_by(UserRoutineItem.position)
    ).all())


def get_all_items(db: Session, user_id: int) -> list[UserRoutineItem]:
    """
    Returns items for the management modal.
    Inactive system items are excluded — they were intentionally deleted by the user.
    Inactive custom items are included so the user can re-activate them.
    """
    ensure_items_seeded(db, user_id)
    from sqlalchemy import or_
    return list(db.scalars(
        select(UserRoutineItem)
        .where(
            UserRoutineItem.user_id == user_id,
            or_(
                UserRoutineItem.is_system.is_(False),
                UserRoutineItem.is_active.is_(True),
            ),
        )
        .order_by(UserRoutineItem.position)
    ).all())


def create_custom_item(db: Session, user_id: int, label: str) -> UserRoutineItem:
    ensure_items_seeded(db, user_id)
    max_pos = db.scalar(
        select(func.max(UserRoutineItem.position)).where(UserRoutineItem.user_id == user_id)
    ) or 0
    key = f"custom_{uuid.uuid4().hex[:12]}"
    item = UserRoutineItem(
        user_id=user_id,
        item_key=key,
        label=label,
        is_system=False,
        is_active=True,
        position=max_pos + 1,
        created_at=datetime.now(timezone.utc),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def toggle_item(db: Session, user_id: int, item_key: str, is_active: bool) -> UserRoutineItem | None:
    item = db.scalar(
        select(UserRoutineItem).where(
            UserRoutineItem.user_id == user_id,
            UserRoutineItem.item_key == item_key,
        )
    )
    if item is None:
        return None
    item.is_active = is_active
    db.commit()
    db.refresh(item)
    return item


def delete_custom_item(db: Session, user_id: int, item_key: str) -> bool:
    item = db.scalar(
        select(UserRoutineItem).where(
            UserRoutineItem.user_id == user_id,
            UserRoutineItem.item_key == item_key,
            UserRoutineItem.is_system.is_(False),
        )
    )
    if item is None:
        return False
    db.delete(item)
    db.commit()
    return True


def delete_any_item(db: Session, user_id: int, item_key: str) -> bool:
    """
    Custom items: delete the row entirely.
    System items: deactivate (row must stay so ensure_items_seeded won't re-add it).
    """
    item = db.scalar(
        select(UserRoutineItem).where(
            UserRoutineItem.user_id == user_id,
            UserRoutineItem.item_key == item_key,
        )
    )
    if item is None:
        return False
    if item.is_system:
        item.is_active = False
    else:
        db.delete(item)
    db.commit()
    return True


def log_item_if_absent(
    db: Session,
    user_id: int,
    item_key: str,
    status: RoutineStatus = RoutineStatus.DONE,
) -> None:
    """Auto-log a routine item from another action. No-op if already logged. Does not commit."""
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
