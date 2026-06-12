import calendar
from datetime import date, datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import RoutineLog, RoutineStatus, User, UserRoutineItem
from app.schemas import (
    RoutineCheckRequest,
    RoutineDayOut,
    RoutineDaySummary,
    RoutineItemOut,
    RoutineMonthOut,
    RoutineWeekOut,
    UserRoutineItemCreate,
    UserRoutineItemOut,
    UserRoutineItemToggle,
)
from app.services.routine_service import (
    create_custom_item,
    delete_any_item,
    delete_custom_item,
    get_active_items,
    get_all_items,
    toggle_item,
)

router = APIRouter(prefix="/routine", tags=["routine"])

WAKE_UP_DEADLINE = time(7, 0)


def _day_items(
    db: Session, user_id: int, day: date, items: list[UserRoutineItem]
) -> list[RoutineItemOut]:
    logs = {
        log.item_key: log
        for log in db.scalars(
            select(RoutineLog).where(RoutineLog.user_id == user_id, RoutineLog.date == day)
        )
    }
    return [
        RoutineItemOut(
            item_key=item.item_key,
            label=item.label,
            status=logs[item.item_key].status.value if item.item_key in logs else None,
            logged_at=logs[item.item_key].logged_at if item.item_key in logs else None,
        )
        for item in items
    ]


@router.get("/today", response_model=RoutineDayOut)
def today_routine(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    today = date.today()
    items = get_active_items(db, current_user.id)
    return RoutineDayOut(date=today, items=_day_items(db, current_user.id, today, items))


@router.patch("/today/{item_id}", response_model=RoutineItemOut)
def check_item(
    item_id: str,
    payload: RoutineCheckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validate item belongs to this user and is active
    item = db.scalar(
        select(UserRoutineItem).where(
            UserRoutineItem.user_id == current_user.id,
            UserRoutineItem.item_key == item_id,
            UserRoutineItem.is_active.is_(True),
        )
    )
    if item is None:
        # Fall back: accept system keys even before seeding runs
        from app.services.routine_service import SYSTEM_ROUTINE_ITEMS
        if item_id not in SYSTEM_ROUTINE_ITEMS:
            raise HTTPException(status_code=404, detail="Unknown routine item")

    today = date.today()
    existing = db.scalar(
        select(RoutineLog).where(
            RoutineLog.user_id == current_user.id,
            RoutineLog.date == today,
            RoutineLog.item_key == item_id,
        )
    )
    if existing:
        raise HTTPException(status_code=409, detail="Item already logged for today")

    now = datetime.now(timezone.utc)
    status = RoutineStatus(payload.status)
    if item_id == "wake_up_before_7" and status == RoutineStatus.DONE:
        if datetime.now().time() > WAKE_UP_DEADLINE:
            status = RoutineStatus.LATE

    log = RoutineLog(
        user_id=current_user.id,
        date=today,
        item_key=item_id,
        status=status,
        logged_at=now,
    )
    db.add(log)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Item already logged for today")
    db.refresh(log)

    label = item.label if item else item_id
    return RoutineItemOut(
        item_key=item_id,
        label=label,
        status=log.status.value,
        logged_at=log.logged_at,
    )


@router.get("/week", response_model=RoutineWeekOut)
def week_routine(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    today = date.today()
    items = get_active_items(db, current_user.id)
    days = [
        RoutineDayOut(date=d, items=_day_items(db, current_user.id, d, items))
        for d in (today - timedelta(days=offset) for offset in range(6, -1, -1))
    ]
    return RoutineWeekOut(days=days)


@router.get("/month", response_model=RoutineMonthOut)
def month_routine(
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = get_active_items(db, current_user.id)
    total_items = len(items)
    active_keys = {item.item_key for item in items}

    _, days_in_month = calendar.monthrange(year, month)
    first_day = date(year, month, 1)
    last_day = date(year, month, days_in_month)

    logs = db.scalars(
        select(RoutineLog).where(
            RoutineLog.user_id == current_user.id,
            RoutineLog.date >= first_day,
            RoutineLog.date <= last_day,
        )
    ).all()

    by_day: dict[date, list[RoutineLog]] = {}
    for log in logs:
        if log.item_key in active_keys:
            by_day.setdefault(log.date, []).append(log)

    today = date.today()
    summaries: list[RoutineDaySummary] = []
    for d in (first_day + timedelta(days=i) for i in range(days_in_month)):
        if d > today:
            summaries.append(RoutineDaySummary(date=d, done=0, total=0, skipped=0))
            continue
        day_logs = by_day.get(d, [])
        done = sum(1 for l in day_logs if l.status in (RoutineStatus.DONE, RoutineStatus.LATE))
        skipped = sum(1 for l in day_logs if l.status == RoutineStatus.SKIPPED)
        summaries.append(RoutineDaySummary(date=d, done=done, total=total_items, skipped=skipped))

    return RoutineMonthOut(year=year, month=month, days=summaries)


# ── Item management ────────────────────────────────────────────────────────────

@router.get("/items", response_model=list[UserRoutineItemOut])
def list_items(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return get_all_items(db, current_user.id)


@router.post("/items", response_model=UserRoutineItemOut, status_code=201)
def add_item(
    payload: UserRoutineItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_custom_item(db, current_user.id, payload.label)


@router.patch("/items/{item_key}", response_model=UserRoutineItemOut)
def update_item(
    item_key: str,
    payload: UserRoutineItemToggle,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = toggle_item(db, current_user.id, item_key, payload.is_active)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/items/{item_key}", status_code=204)
def remove_item(
    item_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not delete_any_item(db, current_user.id, item_key):
        raise HTTPException(status_code=404, detail="Item not found")
