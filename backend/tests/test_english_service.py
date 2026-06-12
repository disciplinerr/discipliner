"""
Technical English service tests.
Pure unit: SM-2 update logic, exercise building.
Integration: seed_progress idempotency (concurrent inserts via ON CONFLICT DO NOTHING).
"""
from datetime import date, timedelta

import pytest

from app.models import Difficulty, EnglishItem, EnglishProgress, User


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_item(**kwargs) -> EnglishItem:
    defaults = dict(
        id=1,
        term="latency",
        term_pt="latência",
        definition_en="Time between request and response.",
        definition_pt="Tempo entre requisição e resposta.",
        example_sentence="High latency degrades user experience.",
        category="networking",
        difficulty=Difficulty.beginner,
        source="seed",
        created_at=date.today(),
    )
    defaults.update(kwargs)
    return EnglishItem(**defaults)


def make_progress(**kwargs) -> EnglishProgress:
    defaults = dict(
        user_id=1,
        item_id=1,
        ease=2.5,
        interval_days=0,
        repetitions=0,
        due_date=date.today(),
        last_reviewed=None,
    )
    defaults.update(kwargs)
    return EnglishProgress(**defaults)


# ---------------------------------------------------------------------------
# Pure unit: SM-2 update
# ---------------------------------------------------------------------------

def test_correct_answer_advances_interval():
    from app.services.english_service import _update_progress
    prog = make_progress()
    _update_progress(prog, grade=2)
    assert prog.repetitions == 1
    assert prog.interval_days == 1
    assert prog.due_date == date.today() + timedelta(days=1)


def test_wrong_answer_resets_interval():
    from app.services.english_service import _update_progress
    prog = make_progress(repetitions=3, interval_days=10, ease=2.5)
    _update_progress(prog, grade=0)
    assert prog.repetitions == 0
    assert prog.interval_days == 1
    assert prog.due_date == date.today() + timedelta(days=1)


def test_ease_grows_with_repeated_correct():
    from app.services.english_service import _update_progress
    prog = make_progress()
    initial_ease = prog.ease
    _update_progress(prog, grade=2)
    _update_progress(prog, grade=2)
    assert prog.ease >= initial_ease


def test_ease_clamped_min():
    from app.services.english_service import _update_progress, MIN_EASE
    prog = make_progress(ease=MIN_EASE)
    _update_progress(prog, grade=0)
    assert prog.ease >= MIN_EASE


def test_ease_clamped_max():
    from app.services.english_service import _update_progress, MAX_EASE
    prog = make_progress(ease=MAX_EASE)
    _update_progress(prog, grade=2)
    assert prog.ease <= MAX_EASE


# ---------------------------------------------------------------------------
# Pure unit: exercise builder
# ---------------------------------------------------------------------------

def test_multiple_choice_has_correct_answer_in_choices():
    from app.services.english_service import _build_exercise
    item = make_item()
    pool = [item] + [
        make_item(id=i, term=f"term{i}", definition_en=f"def{i}")
        for i in range(2, 6)
    ]
    result = _build_exercise(item, "multiple_choice_vocab", pool)
    assert item.definition_en in result["choices"]
    assert len(result["choices"]) <= 4


def test_fill_blank_replaces_term():
    from app.services.english_service import _build_exercise
    item = make_item()
    result = _build_exercise(item, "fill_in_the_blank", [item])
    assert "___" in result["prompt"]
    assert item.term not in result["prompt"]


def test_fill_blank_fallback_when_no_sentence():
    from app.services.english_service import _build_exercise
    item = make_item(example_sentence=None)
    pool = [item] + [make_item(id=i, definition_en=f"def{i}") for i in range(2, 5)]
    result = _build_exercise(item, "fill_in_the_blank", pool)
    # falls back to multiple_choice_vocab
    assert result["choices"] is not None


def test_translate_pt_en_uses_portuguese_term():
    from app.services.english_service import _build_exercise
    item = make_item(term_pt="latência")
    result = _build_exercise(item, "translate_pt_en", [item])
    assert result["prompt"] == "latência"
    assert result["choices"] is None


# ---------------------------------------------------------------------------
# Pure unit: difficulty bucketing by phase
# ---------------------------------------------------------------------------

def test_phase_1_only_beginner():
    from app.services.english_service import _difficulty_for_phase
    assert _difficulty_for_phase(1) == [Difficulty.beginner]


def test_phase_3_includes_intermediate():
    from app.services.english_service import _difficulty_for_phase
    levels = _difficulty_for_phase(3)
    assert Difficulty.intermediate in levels
    assert Difficulty.advanced not in levels


def test_phase_5_all_levels():
    from app.services.english_service import _difficulty_for_phase
    levels = _difficulty_for_phase(5)
    assert Difficulty.advanced in levels


# ---------------------------------------------------------------------------
# Integration: seed_progress idempotency / ON CONFLICT DO NOTHING
# ---------------------------------------------------------------------------

def _insert_user(db) -> User:
    from sqlalchemy import select
    user = User(email=f"eng-{id(db)}@test.com", hashed_password="x")
    db.add(user)
    db.flush()
    return user


def _insert_item(db, idx: int) -> EnglishItem:
    item = EnglishItem(
        term=f"term{idx}",
        term_pt=f"termo{idx}",
        definition_en=f"def{idx}",
        definition_pt=f"def_pt{idx}",
        example_sentence=f"example {idx}",
        category="networking",
        difficulty=Difficulty.beginner,
        source="test",
        created_at=date.today(),
    )
    db.add(item)
    db.flush()
    return item


def test_seed_progress_creates_rows(db):
    from app.services.english_service import seed_progress
    user = _insert_user(db)
    _insert_item(db, 1)
    _insert_item(db, 2)
    db.commit()

    seed_progress(db, user)

    from sqlalchemy import select
    rows = db.scalars(
        select(EnglishProgress).where(EnglishProgress.user_id == user.id)
    ).all()
    assert len(rows) == 2


def test_seed_progress_idempotent(db):
    """Calling seed_progress twice must not raise and must not duplicate rows."""
    from app.services.english_service import seed_progress
    from sqlalchemy import select

    user = _insert_user(db)
    _insert_item(db, 10)
    db.commit()

    seed_progress(db, user)
    seed_progress(db, user)  # second call — must not raise UniqueViolation

    rows = db.scalars(
        select(EnglishProgress).where(EnglishProgress.user_id == user.id)
    ).all()
    assert len(rows) == 1


def test_seed_progress_no_duplicate_on_repeated_flush(db):
    """
    ON CONFLICT DO NOTHING: even if session flushes and re-calls seed, no error.
    Validates the race-condition fix (concurrent page-load requests hit same endpoint).
    """
    from app.services.english_service import seed_progress
    from sqlalchemy import select

    user = _insert_user(db)
    _insert_item(db, 20)
    _insert_item(db, 21)
    db.commit()

    # Simulate two near-simultaneous calls (same session, models already flushed)
    seed_progress(db, user)
    db.flush()
    seed_progress(db, user)  # must not raise

    rows = db.scalars(
        select(EnglishProgress).where(EnglishProgress.user_id == user.id)
    ).all()
    assert len(rows) == 2
