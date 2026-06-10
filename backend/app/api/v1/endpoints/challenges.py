from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import ChallengeSubmission, DailyChallenge, SubmissionResult, User
from app.schemas import (
    ChallengeHistoryItem,
    ChallengeOut,
    SubmissionCreate,
    SubmissionOut,
)
from app.services.challenge_generator import (
    evaluate_submission,
    get_or_create_today_challenge,
)
from app.services.routine_service import log_item_if_absent

router = APIRouter(prefix="/challenges", tags=["challenges"])


@router.get("/today", response_model=ChallengeOut)
def today_challenge(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return get_or_create_today_challenge(db, current_user)


@router.post("/{challenge_id}/submit", response_model=SubmissionOut)
def submit(
    challenge_id: int,
    payload: SubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Non-negotiable rule 5: math derivation is required, minimum 50 characters.
    if len(payload.math_derivation.strip()) < 50:
        raise HTTPException(
            status_code=422,
            detail="math_derivation is required (minimum 50 characters). Write your derivation.",
        )

    challenge = db.get(DailyChallenge, challenge_id)
    if challenge is None or challenge.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Challenge not found")

    result, reason = evaluate_submission(challenge, payload.code_submission)
    submission = ChallengeSubmission(
        challenge_id=challenge.id,
        user_id=current_user.id,
        math_derivation=payload.math_derivation,
        code_submission=payload.code_submission,
        result=SubmissionResult(result),
        reason=reason,
    )
    db.add(submission)
    # Attempting the challenge fulfills the "daily_challenge" routine item.
    log_item_if_absent(db, current_user.id, "daily_challenge")
    db.commit()
    db.refresh(submission)
    return submission


@router.get("/history", response_model=list[ChallengeHistoryItem])
def history(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    challenges = db.scalars(
        select(DailyChallenge)
        .where(DailyChallenge.user_id == current_user.id)
        .order_by(DailyChallenge.date.desc())
    ).all()
    return [
        ChallengeHistoryItem(
            challenge=ChallengeOut.model_validate(c),
            submissions=[
                SubmissionOut.model_validate(s)
                for s in sorted(c.submissions, key=lambda s: s.submitted_at, reverse=True)
            ],
        )
        for c in challenges
    ]
