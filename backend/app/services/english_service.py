"""Technical English training — spaced repetition over vocabulary.

SM-2-lite: binary grading (correct=2 / wrong=0).
Session cap: 15 exercises per day.
Routine auto-log: fires when 15 correct answers reached in a day.
"""

import logging
import random
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Difficulty, EnglishAttempt, EnglishItem, EnglishProgress, User
from app.services.routine_service import log_item_if_absent

logger = logging.getLogger(__name__)

SESSION_CAP = 15
CORRECT_CAP = 15
MIN_EASE = 1.3
MAX_EASE = 3.0


def _difficulty_for_phase(phase: int) -> list[Difficulty]:
    if phase <= 2:
        return [Difficulty.beginner]
    if phase <= 4:
        return [Difficulty.beginner, Difficulty.intermediate]
    return [Difficulty.beginner, Difficulty.intermediate, Difficulty.advanced]


def _available_types(item: EnglishItem) -> list[str]:
    types = ["multiple_choice_vocab"]
    if item.example_sentence:
        types.append("fill_in_the_blank")
    if item.term_pt:
        types.append("translate_pt_en")
        types.append("translate_en_pt")
    return types


def _build_exercise(
    item: EnglishItem,
    exercise_type: str,
    pool: list[EnglishItem],
) -> dict:
    if exercise_type == "multiple_choice_vocab":
        wrong_pool = [i.definition_en for i in pool if i.id != item.id]
        wrong = random.sample(wrong_pool, min(3, len(wrong_pool)))
        choices = [item.definition_en] + wrong
        random.shuffle(choices)
        return {"prompt": item.term, "choices": choices}

    if exercise_type == "fill_in_the_blank":
        if not item.example_sentence:
            return _build_exercise(item, "multiple_choice_vocab", pool)
        blanked = item.example_sentence.replace(item.term, "___", 1)
        return {"prompt": blanked, "choices": None}

    if exercise_type == "translate_pt_en":
        return {"prompt": item.term_pt or item.term, "choices": None}

    if exercise_type == "translate_en_pt":
        return {"prompt": item.term, "choices": None}

    return {"prompt": item.term, "choices": None}


def seed_progress(db: Session, user: User) -> None:
    """Lazy-seed EnglishProgress rows for items matching user's phase level. Idempotent."""
    difficulties = _difficulty_for_phase(user.current_phase)
    items = db.scalars(
        select(EnglishItem).where(EnglishItem.difficulty.in_(difficulties))
    ).all()

    existing_ids = {
        row.item_id
        for row in db.scalars(
            select(EnglishProgress).where(EnglishProgress.user_id == user.id)
        )
    }

    today = date.today()
    new_rows = [
        EnglishProgress(user_id=user.id, item_id=item.id, due_date=today)
        for item in items
        if item.id not in existing_ids
    ]
    if new_rows:
        db.add_all(new_rows)
        db.commit()


def get_session(db: Session, user: User) -> list[dict]:
    seed_progress(db, user)

    due = db.scalars(
        select(EnglishProgress)
        .where(
            EnglishProgress.user_id == user.id,
            EnglishProgress.due_date <= date.today(),
        )
        .order_by(EnglishProgress.due_date, EnglishProgress.id)
        .limit(SESSION_CAP)
    ).all()

    if not due:
        return []

    item_ids = [p.item_id for p in due]
    items_map = {
        i.id: i
        for i in db.scalars(select(EnglishItem).where(EnglishItem.id.in_(item_ids)))
    }

    pool = db.scalars(
        select(EnglishItem).where(EnglishItem.difficulty == list(items_map.values())[0].difficulty)
    ).all()

    exercises = []
    for progress in due:
        item = items_map.get(progress.item_id)
        if item is None:
            continue
        types = _available_types(item)
        exercise_type = types[progress.repetitions % len(types)]
        ex = _build_exercise(item, exercise_type, pool)
        exercises.append(
            {
                "item_id": item.id,
                "exercise_type": exercise_type,
                "prompt": ex["prompt"],
                "choices": ex["choices"],
            }
        )
    return exercises


def _correct_today(db: Session, user_id: int) -> int:
    today = datetime.now(timezone.utc).date()
    return db.scalar(
        select(func.count())
        .select_from(EnglishAttempt)
        .where(
            EnglishAttempt.user_id == user_id,
            EnglishAttempt.correct.is_(True),
            func.date(EnglishAttempt.attempted_at) == today,
        )
    ) or 0


def validate_and_answer(
    db: Session,
    user: User,
    item_id: int,
    exercise_type: str,
    answer: str,
) -> tuple[bool, str, bool]:
    """Returns (correct, correct_answer, session_complete)."""
    item = db.get(EnglishItem, item_id)
    if item is None:
        return False, "", False

    answer_norm = answer.strip().lower()

    if exercise_type == "multiple_choice_vocab":
        correct_answer = item.definition_en
        correct = answer_norm == correct_answer.strip().lower()

    elif exercise_type == "fill_in_the_blank":
        correct_answer = item.term
        correct = answer_norm == correct_answer.strip().lower()

    elif exercise_type == "translate_pt_en":
        correct_answer = item.term
        correct = answer_norm == correct_answer.strip().lower()

    elif exercise_type == "translate_en_pt":
        correct_answer = item.term_pt or item.term
        correct = answer_norm == correct_answer.strip().lower()

    else:
        return False, "", False

    # Update SM-2-lite progress
    progress = db.scalar(
        select(EnglishProgress).where(
            EnglishProgress.user_id == user.id,
            EnglishProgress.item_id == item_id,
        )
    )
    if progress:
        grade = 2 if correct else 0
        _update_progress(progress, grade)

    db.add(
        EnglishAttempt(
            user_id=user.id,
            item_id=item_id,
            exercise_type=exercise_type,
            correct=correct,
            attempted_at=datetime.now(timezone.utc),
        )
    )
    db.commit()

    correct_count = _correct_today(db, user.id)
    session_complete = correct_count >= CORRECT_CAP
    if session_complete:
        log_item_if_absent(db, user.id, "english_training")
        db.commit()

    return correct, correct_answer, session_complete


def _update_progress(progress: EnglishProgress, grade: int) -> None:
    if grade == 0:
        progress.repetitions = 0
        progress.interval_days = 1
        progress.ease = max(MIN_EASE, progress.ease - 0.2)
    else:
        progress.repetitions += 1
        progress.ease = min(MAX_EASE, progress.ease + 0.1)
        if progress.repetitions == 1:
            progress.interval_days = 1
        elif progress.repetitions == 2:
            progress.interval_days = 3
        else:
            progress.interval_days = max(
                progress.interval_days + 1,
                round(progress.interval_days * progress.ease),
            )

    progress.due_date = date.today() + timedelta(days=progress.interval_days)
    progress.last_reviewed = date.today()


def get_stats(db: Session, user: User) -> dict:
    seed_progress(db, user)
    rows = db.scalars(
        select(EnglishProgress).where(EnglishProgress.user_id == user.id)
    ).all()
    today = date.today()
    due_today = sum(1 for r in rows if r.due_date <= today)
    mature = sum(1 for r in rows if r.repetitions >= 3)

    # Pass rate last 7 days
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    attempts = db.scalars(
        select(EnglishAttempt).where(
            EnglishAttempt.user_id == user.id,
            EnglishAttempt.attempted_at >= week_ago,
        )
    ).all()
    total_attempts = len(attempts)
    correct_attempts = sum(1 for a in attempts if a.correct)
    pass_rate = (correct_attempts / total_attempts) if total_attempts > 0 else 0.0

    return {
        "due_today": due_today,
        "done_today": _correct_today(db, user.id),
        "pass_rate_7d": round(pass_rate, 3),
        "mature_items": mature,
        "total_items": len(rows),
    }


def generate_for_phase(db: Session, user: User, phase_topics: str, difficulty: str) -> None:
    """Call Claude to generate contextual vocabulary items for newly completed phase. Idempotent."""
    import json
    import re

    import anthropic

    from app.core.config import settings

    SYSTEM_PROMPT = (
        "You are generating technical English vocabulary exercises for a developer learning platform. "
        "Output ONLY a JSON array. No prose, no markdown, no code fences. "
        "Each object must have exactly these keys: "
        "term (string, max 3 words, technical English), "
        "term_pt (string, Portuguese equivalent of the term), "
        "definition_en (string, 1 sentence), "
        "definition_pt (string, 1 sentence in Brazilian Portuguese), "
        "example_sentence (string, 1 sentence using the term in a technical context), "
        "category (one of: networking, concurrency, databases, systems, devops, api-design, security, git-workflow)."
    )

    existing_terms = {
        item.term.lower()
        for item in db.scalars(select(EnglishItem).where(EnglishItem.source == "claude"))
    }

    user_prompt = (
        f"Generate 8 vocabulary items for topics: {phase_topics}. "
        f"Difficulty: {difficulty}. "
        f"Do not use any of these terms: {', '.join(sorted(existing_terms)) or 'none'}."
    )

    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=1200,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = response.content[0].text.strip()
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if not match:
            return
        items_data = json.loads(match.group())
        for obj in items_data:
            if not all(k in obj for k in ("term", "definition_en", "definition_pt")):
                continue
            if obj["term"].lower() in existing_terms:
                continue
            db.add(
                EnglishItem(
                    term=obj["term"],
                    term_pt=obj.get("term_pt"),
                    definition_en=obj["definition_en"],
                    definition_pt=obj["definition_pt"],
                    example_sentence=obj.get("example_sentence"),
                    category=obj.get("category", "systems"),
                    difficulty=Difficulty(difficulty),
                    source="claude",
                    created_at=datetime.now(timezone.utc),
                )
            )
        db.commit()
    except Exception:
        logger.exception("English item generation failed for phase")
