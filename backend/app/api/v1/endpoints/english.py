import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.limiter import limiter
from app.db.session import get_db
from app.models import User
from app.schemas import (
    EnglishAnswerRequest,
    EnglishAnswerResult,
    EnglishExercise,
    EnglishSessionOut,
    EnglishStatsOut,
)
from app.services.english_service import get_session, get_stats, validate_and_answer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/english", tags=["english"])


@router.get("/session", response_model=EnglishSessionOut)
@limiter.limit("30/minute")
def session(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stats = get_stats(db, current_user)
    exercises = get_session(db, current_user)
    if not exercises:
        response.status_code = 204
        return EnglishSessionOut(items=[], done_today=stats["done_today"], due_today=0)
    return EnglishSessionOut(
        items=[EnglishExercise(**ex) for ex in exercises],
        done_today=stats["done_today"],
        due_today=stats["due_today"],
    )


@router.post("/answer", response_model=EnglishAnswerResult)
@limiter.limit("60/minute")
def answer(
    request: Request,
    payload: EnglishAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    correct, correct_answer, session_complete = validate_and_answer(
        db,
        current_user,
        payload.item_id,
        payload.exercise_type,
        payload.answer,
    )
    if correct_answer == "":
        raise HTTPException(status_code=404, detail="Item not found")
    return EnglishAnswerResult(
        correct=correct,
        correct_answer=correct_answer,
        session_complete=session_complete,
    )


@router.get("/stats", response_model=EnglishStatsOut)
def stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_stats(db, current_user)
