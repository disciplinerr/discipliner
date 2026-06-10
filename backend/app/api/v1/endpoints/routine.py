from datetime import date, datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import RoutineLog, RoutineStatus, User
from app.schemas import RoutineCheckRequest, RoutineDayOut, RoutineItemOut, RoutineWeekOut
from app.services.routine_service import ROUTINE_ITEMS

router = APIRouter(prefix="/routine", tags=["routine"])

WAKE_UP_DEADLINE = time(7, 0)


def _day_items(db: Session, user_id: int, day: date) -> list[RoutineItemOut]:
    logs = {
        log.item_key: log
        for log in db.scalars(
            select(RoutineLog).where(RoutineLog.user_id == user_id, RoutineLog.date == day)
        )
    }
    return [
        RoutineItemOut(
            item_key=key,
            label=label,
            status=logs[key].status.value if key in logs else None,
            logged_at=logs[key].logged_at if key in logs else None,
        )
        for key, label in ROUTINE_ITEMS.items()
    ]


@router.get("/today", response_model=RoutineDayOut)
def today_routine(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    today = date.today()
    return RoutineDayOut(date=today, items=_day_items(db, current_user.id, today))


@router.patch("/today/{item_id}", response_model=RoutineItemOut)
def check_item(
    item_id: str,
    payload: RoutineCheckRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if item_id not in ROUTINE_ITEMS:
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
        # Logs are permanent — no unchecking, no rewriting history.
        raise HTTPException(status_code=409, detail="Item already logged for today")

    now = datetime.now(timezone.utc)
    status = RoutineStatus(payload.status)
    # Server-side timestamp validation: checking in "wake up before 7" after
    # 7:00 AM local server time is recorded as LATE, not DONE.
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
    db.commit()
    db.refresh(log)
    return RoutineItemOut(
        item_key=item_id,
        label=ROUTINE_ITEMS[item_id],
        status=log.status.value,
        logged_at=log.logged_at,
    )


@router.get("/week", response_model=RoutineWeekOut)
def week_routine(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    today = date.today()
    days = [
        RoutineDayOut(date=d, items=_day_items(db, current_user.id, d))
        for d in (today - timedelta(days=offset) for offset in range(6, -1, -1))
    ]
    return RoutineWeekOut(days=days)
