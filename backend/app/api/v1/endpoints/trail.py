from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas import PhaseCompleteRequest, PhaseOut, TrailProgressOut
from app.services.trail_service import (
    PhaseOrderError,
    complete_phase,
    get_all_phases,
    get_progress,
)

router = APIRouter(prefix="/trail", tags=["trail"])


@router.get("/phases", response_model=list[PhaseOut])
def phases(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return get_all_phases(db)


@router.get("/progress", response_model=TrailProgressOut)
def progress(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return get_progress(db, current_user)


@router.post("/phase/{phase_id}/complete", status_code=status.HTTP_204_NO_CONTENT)
def complete(
    phase_id: int,
    payload: PhaseCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        complete_phase(db, current_user, phase_id, payload.summary)
    except LookupError:
        raise HTTPException(status_code=404, detail="Phase not found")
    except PhaseOrderError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
