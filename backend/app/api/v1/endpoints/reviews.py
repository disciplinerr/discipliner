from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import ReviewCard, User
from app.schemas import ReviewCardOut, ReviewGradeRequest, ReviewStatsOut
from app.services.review_service import (
    get_due_cards,
    get_stats,
    grade_card,
    seed_cards_for_user,
)
from app.services.routine_service import log_item_if_absent

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/due", response_model=list[ReviewCardOut])
def due(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    seed_cards_for_user(db, current_user)
    return get_due_cards(db, current_user)


@router.get("/stats", response_model=ReviewStatsOut)
def stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    seed_cards_for_user(db, current_user)
    return get_stats(db, current_user)


@router.post("/{card_id}/grade", response_model=ReviewCardOut)
def grade(
    card_id: int,
    payload: ReviewGradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    card = db.get(ReviewCard, card_id)
    if card is None or card.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Card not found")

    grade_card(card, payload.grade)
    # Reviewing a concept fulfills the "trail_review" routine item for today.
    log_item_if_absent(db, current_user.id, "trail_review")
    db.commit()
    db.refresh(card)
    return card
