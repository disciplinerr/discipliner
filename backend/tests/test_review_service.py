from datetime import date, timedelta

import pytest

from app.models import ReviewCard
from app.services.review_service import grade_card


def make_card(**kwargs) -> ReviewCard:
    defaults = dict(
        user_id=1,
        phase_id=1,
        topic="HTTP",
        ease=2.5,
        interval_days=0,
        repetitions=0,
        due_date=date.today(),
    )
    defaults.update(kwargs)
    return ReviewCard(**defaults)


def test_first_good_review_schedules_tomorrow():
    card = make_card()
    grade_card(card, 2)
    assert card.repetitions == 1
    assert card.interval_days == 1
    assert card.due_date == date.today() + timedelta(days=1)


def test_second_review_schedules_three_days():
    card = make_card(repetitions=1, interval_days=1)
    grade_card(card, 2)
    assert card.interval_days == 3


def test_intervals_expand_with_repetitions():
    card = make_card(repetitions=2, interval_days=3, ease=2.5)
    grade_card(card, 2)
    assert card.interval_days == round(3 * 2.5)  # 8 days


def test_forgot_resets_card():
    card = make_card(repetitions=5, interval_days=30, ease=2.5)
    grade_card(card, 0)
    assert card.repetitions == 0
    assert card.interval_days == 1
    assert card.ease == pytest.approx(2.3)
    assert card.due_date == date.today() + timedelta(days=1)


def test_easy_increases_ease_hard_decreases():
    easy = make_card()
    grade_card(easy, 3)
    assert easy.ease == pytest.approx(2.65)

    hard = make_card()
    grade_card(hard, 1)
    assert hard.ease == pytest.approx(2.35)


def test_ease_clamped_to_bounds():
    card = make_card(ease=1.3)
    grade_card(card, 1)
    assert card.ease == 1.3

    card = make_card(ease=3.0)
    grade_card(card, 3)
    assert card.ease == 3.0


def test_invalid_grade_rejected():
    with pytest.raises(ValueError):
        grade_card(make_card(), 4)
