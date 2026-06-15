"""Overview math: total income (recurring + one-off) vs total spending
(lançamentos + contas fixas + parcelas)."""

from datetime import date

from app.models import (
    IncomeKind,
    Installment,
    RecurringBill,
    RecurringIncome,
    Transaction,
    TransactionKind,
    User,
)
from app.core.security import hash_password
from app.services.finance_service import (
    build_overview,
    spending_recommendation,
    trend_for_months,
)


def _make_user(db) -> User:
    user = User(email="fin@example.com", hashed_password=hash_password("x" * 12))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_overview_totals(db):
    user = _make_user(db)
    y, m = 2026, 6

    # Renda fixa: salário 5000 + VR 800 (ativo) + uma inativa que não conta
    db.add_all(
        [
            RecurringIncome(user_id=user.id, name="Salário", amount=5000, kind=IncomeKind.SALARY),
            RecurringIncome(user_id=user.id, name="VR", amount=800, kind=IncomeKind.BENEFIT),
            RecurringIncome(
                user_id=user.id, name="Antigo", amount=999, kind=IncomeKind.OTHER, is_active=False
            ),
        ]
    )
    # Receita avulsa 200
    db.add(
        Transaction(
            user_id=user.id, description="freela", amount=200,
            kind=TransactionKind.INCOME, date=date(y, m, 5),
        )
    )
    # Lançamento (despesa) 300
    db.add(
        Transaction(
            user_id=user.id, description="mercado", amount=300,
            kind=TransactionKind.EXPENSE, date=date(y, m, 10),
        )
    )
    # Conta fixa 150 (vence dia 8)
    db.add(RecurringBill(user_id=user.id, name="Internet", amount=150, due_day=8))
    # Parcela 420 x10 começando neste mês
    db.add(
        Installment(
            user_id=user.id, description="Macbook", installment_amount=420,
            total_installments=10, start_year=y, start_month=m, due_day=15,
        )
    )
    db.commit()

    ov = build_overview(db, user.id, y, m)

    assert ov["recurring_income"] == 5800            # 5000 + 800, inativa ignorada
    assert ov["income"] == 200                        # avulsa
    assert ov["total_income"] == 6000                 # 5800 + 200
    assert ov["total_spending"] == 870                # 300 + 150 + 420
    assert ov["net"] == 5130                          # 6000 - 870
    assert abs(ov["savings_rate"] - 5130 / 6000) < 1e-9


def test_overview_zero_income_no_div_by_zero(db):
    user = _make_user(db)
    ov = build_overview(db, user.id, 2026, 6)
    assert ov["total_income"] == 0
    assert ov["total_spending"] == 0
    assert ov["savings_rate"] == 0.0


def test_recommendation_amounts_and_status():
    rec = spending_recommendation(income=5000, actual_spending=3000)
    # 50/30/20 group caps
    g = {row["group"]: row for row in rec["groups"]}
    assert g["NEEDS"]["amount"] == 2500
    assert g["WANTS"]["amount"] == 1500
    assert g["SAVINGS"]["amount"] == 1000
    # Per-area fractions sum to the income
    assert round(sum(it["amount"] for it in rec["items"]), 2) == 5000
    # 40% leftover -> healthy
    assert rec["status"] == "healthy"

    assert spending_recommendation(5000, 4500)["status"] == "tight"   # 10% left
    assert spending_recommendation(5000, 6000)["status"] == "over"    # negative
    assert spending_recommendation(0, 0)["status"] == "unknown"


def test_trend_counts_recurring_only_from_creation_month(db):
    """Salary created this month must not inflate previous months' income."""
    user = _make_user(db)
    db.add(
        RecurringIncome(user_id=user.id, name="Salário", amount=5000, kind=IncomeKind.SALARY)
    )
    db.commit()

    points = trend_for_months(db, user.id, 2026, 6, 6)  # jan..jun
    assert points[-1]["month"] == 6
    assert points[-1]["income"] == 5000      # current month: salary counts
    assert all(p["income"] == 0 for p in points[:-1])  # past months: no history
