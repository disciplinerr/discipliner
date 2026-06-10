"""Spaced repetition (SM-2-lite) over trail topics.

Implements the two techniques rated "high utility" by Dunlosky et al. (2013):
practice testing (active recall — the card asks the user to explain a topic
from memory) and distributed practice (expanding review intervals).

Grades: 0 = forgot, 1 = hard, 2 = good, 3 = easy.
"""

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ReviewCard, TrailPhase, User

MIN_EASE = 1.3
MAX_EASE = 3.0


def seed_cards_for_user(db: Session, user: User) -> None:
    """Create one card per topic for every phase the user has reached.

    Idempotent — existing cards are kept untouched. Called on every
    GET /reviews/due so new phases automatically feed the review deck.
    """
    phases = db.scalars(
        select(TrailPhase).where(TrailPhase.number <= user.current_phase)
    ).all()
    existing = {
        (c.phase_id, c.topic)
        for c in db.scalars(select(ReviewCard).where(ReviewCard.user_id == user.id))
    }
    today = date.today()
    created = False
    for phase in phases:
        for topic in (t.strip() for t in phase.topics.split("\n") if t.strip()):
            if (phase.id, topic) not in existing:
                db.add(
                    ReviewCard(
                        user_id=user.id,
                        phase_id=phase.id,
                        topic=topic,
                        due_date=today,
                    )
                )
                created = True
    if created:
        db.commit()


def get_due_cards(db: Session, user: User) -> list[ReviewCard]:
    return list(
        db.scalars(
            select(ReviewCard)
            .where(ReviewCard.user_id == user.id, ReviewCard.due_date <= date.today())
            .order_by(ReviewCard.due_date, ReviewCard.id)
        )
    )


def grade_card(card: ReviewCard, grade: int) -> None:
    """Apply an SM-2-lite scheduling update in place. Caller commits."""
    if grade not in (0, 1, 2, 3):
        raise ValueError("grade must be 0, 1, 2 or 3")

    if grade == 0:
        # Forgot: back to the start, see it again tomorrow.
        card.repetitions = 0
        card.interval_days = 1
        card.ease = max(MIN_EASE, card.ease - 0.2)
    else:
        card.repetitions += 1
        if grade == 1:
            card.ease = max(MIN_EASE, card.ease - 0.15)
        elif grade == 3:
            card.ease = min(MAX_EASE, card.ease + 0.15)

        if card.repetitions == 1:
            card.interval_days = 1
        elif card.repetitions == 2:
            card.interval_days = 3
        else:
            multiplier = card.ease * (0.8 if grade == 1 else 1.3 if grade == 3 else 1.0)
            card.interval_days = max(
                card.interval_days + 1, round(card.interval_days * multiplier)
            )

    card.due_date = date.today() + timedelta(days=card.interval_days)
    card.last_reviewed_at = datetime.now(timezone.utc)


def get_stats(db: Session, user: User) -> dict:
    cards = db.scalars(select(ReviewCard).where(ReviewCard.user_id == user.id)).all()
    today = date.today()
    return {
        "total": len(cards),
        "due": sum(1 for c in cards if c.due_date <= today),
        "reviewed_today": sum(
            1
            for c in cards
            if c.last_reviewed_at is not None and c.last_reviewed_at.date() == today
        ),
        "mature": sum(1 for c in cards if c.repetitions >= 3),
    }
