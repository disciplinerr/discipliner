from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import TrailPhase, TrailProgress, User
from app.schemas import PhaseOut, PhaseProgressOut, TrailProgressOut


def _phase_out(phase: TrailPhase) -> PhaseOut:
    return PhaseOut(
        id=phase.id,
        number=phase.number,
        name=phase.name,
        weeks=phase.weeks,
        topics=[t for t in phase.topics.split("\n") if t.strip()],
        exercises=[e for e in phase.exercises.split("\n") if e.strip()],
    )


def get_all_phases(db: Session) -> list[PhaseOut]:
    phases = db.scalars(select(TrailPhase).order_by(TrailPhase.number)).all()
    return [_phase_out(p) for p in phases]


def get_progress(db: Session, user: User) -> TrailProgressOut:
    phases = db.scalars(select(TrailPhase).order_by(TrailPhase.number)).all()
    progress = {
        p.phase_id: p
        for p in db.scalars(select(TrailProgress).where(TrailProgress.user_id == user.id))
    }
    return TrailProgressOut(
        current_phase=user.current_phase,
        phases=[
            PhaseProgressOut(
                phase=_phase_out(phase),
                started_at=progress[phase.id].started_at if phase.id in progress else None,
                completed_at=progress[phase.id].completed_at if phase.id in progress else None,
                summary=progress[phase.id].summary if phase.id in progress else "",
                is_current=phase.number == user.current_phase,
            )
            for phase in phases
        ],
    )


class PhaseOrderError(Exception):
    pass


def complete_phase(db: Session, user: User, phase_id: int, summary: str) -> None:
    phase = db.get(TrailPhase, phase_id)
    if phase is None:
        raise LookupError("Phase not found")
    # Non-negotiable rule 3: phases must be completed in order.
    if phase.number != user.current_phase:
        raise PhaseOrderError(
            f"Out of order: you are on phase {user.current_phase}, "
            f"cannot complete phase {phase.number}."
        )

    now = datetime.now(timezone.utc)
    record = db.scalar(
        select(TrailProgress).where(
            TrailProgress.user_id == user.id, TrailProgress.phase_id == phase.id
        )
    )
    if record is None:
        record = TrailProgress(user_id=user.id, phase_id=phase.id, started_at=now)
        db.add(record)
    if record.completed_at is not None:
        raise PhaseOrderError("Phase already completed.")
    record.completed_at = now
    record.summary = summary
    user.current_phase = user.current_phase + 1
    db.commit()
