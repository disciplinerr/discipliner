"""Finance domain logic: default-category seeding and monthly overview math.

Design follows two budgeting frameworks banks commonly teach:
- Envelope budgeting: every category carries its own monthly budget; spending
  is compared against it.
- 50/30/20 rule: categories roll up into Needs / Wants / Savings groups whose
  recommended share of income is 50% / 30% / 20%.
"""

import calendar
from datetime import date, datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.models import (
    BillPayment,
    BudgetGroup,
    ExpenseCategory,
    Installment,
    RecurringBill,
    SavingsGoal,
    Transaction,
    TransactionKind,
)

# key -> (name, emoji, color, group)
DEFAULT_CATEGORIES: dict[str, tuple[str, str, str, BudgetGroup]] = {
    "study": ("Educação", "🎓", "#fbbf24", BudgetGroup.NEEDS),
    "housing": ("Moradia", "🏠", "#60a5fa", BudgetGroup.NEEDS),
    "groceries": ("Mercado", "🛒", "#34d399", BudgetGroup.NEEDS),
    "transport": ("Transporte", "🚌", "#fbbf24", BudgetGroup.NEEDS),
    "utilities": ("Contas de casa", "💡", "#f87171", BudgetGroup.NEEDS),
    "health": ("Saúde", "🩺", "#f472b6", BudgetGroup.NEEDS),
    "dining": ("Restaurantes", "🍽️", "#fb923c", BudgetGroup.WANTS),
    "leisure": ("Lazer", "🎮", "#a78bfa", BudgetGroup.WANTS),
    "shopping": ("Compras", "🛍️", "#e879f9", BudgetGroup.WANTS),
    "subscriptions": ("Assinaturas", "📺", "#22d3ee", BudgetGroup.WANTS),
    "savings": ("Reserva / Investimento", "💰", "#4ade80", BudgetGroup.SAVINGS),
    "debt": ("Dívidas", "💳", "#fca5a5", BudgetGroup.SAVINGS),
}

GROUP_TARGETS: dict[BudgetGroup, int] = {
    BudgetGroup.NEEDS: 50,
    BudgetGroup.WANTS: 30,
    BudgetGroup.SAVINGS: 20,
}


def ensure_categories_seeded(db: Session, user_id: int) -> None:
    """Seed default categories per-key — idempotent and concurrency-safe.

    Read endpoints fire in parallel from the frontend, so two requests can both
    observe an empty set and race to insert the same keys. A plain check-then-add
    hits ``uq_expense_category_key``; ``ON CONFLICT DO NOTHING`` makes the insert
    atomic at the DB level, so the loser of the race is silently ignored.
    """
    existing_keys = set(
        db.scalars(
            select(ExpenseCategory.category_key).where(ExpenseCategory.user_id == user_id)
        ).all()
    )
    if len(existing_keys) >= len(DEFAULT_CATEGORIES):
        return

    max_pos = db.scalar(
        select(func.max(ExpenseCategory.position)).where(ExpenseCategory.user_id == user_id)
    )
    next_pos = (max_pos + 1) if max_pos is not None else 0

    now = datetime.now(timezone.utc)
    rows = []
    for key, (name, emoji, color, group) in DEFAULT_CATEGORIES.items():
        if key in existing_keys:
            continue
        rows.append(
            {
                "user_id": user_id,
                "category_key": key,
                "name": name,
                "emoji": emoji,
                "color": color,
                "group": group,
                "monthly_budget": 0.0,
                "is_system": True,
                "is_active": True,
                "position": next_pos,
                "created_at": now,
            }
        )
        next_pos += 1

    if rows:
        stmt = pg_insert(ExpenseCategory).values(rows).on_conflict_do_nothing(
            constraint="uq_expense_category_key"
        )
        db.execute(stmt)
        db.commit()


def get_categories(db: Session, user_id: int, active_only: bool = False) -> list[ExpenseCategory]:
    ensure_categories_seeded(db, user_id)
    stmt = select(ExpenseCategory).where(ExpenseCategory.user_id == user_id)
    if active_only:
        stmt = stmt.where(ExpenseCategory.is_active.is_(True))
    return list(db.scalars(stmt.order_by(ExpenseCategory.position)).all())


def _month_bounds(year: int, month: int) -> tuple[date, date]:
    _, last = calendar.monthrange(year, month)
    return date(year, month, 1), date(year, month, last)


def bills_for_month(db: Session, user_id: int, year: int, month: int) -> list[dict]:
    """Project active recurring bills onto (year, month) with their paid state."""
    _, last_day = calendar.monthrange(year, month)
    bills = db.scalars(
        select(RecurringBill).where(
            RecurringBill.user_id == user_id, RecurringBill.is_active.is_(True)
        ).order_by(RecurringBill.due_day)
    ).all()

    payments = {
        p.bill_id: p
        for p in db.scalars(
            select(BillPayment).where(
                BillPayment.user_id == user_id,
                BillPayment.year == year,
                BillPayment.month == month,
            )
        )
    }

    today = date.today()
    out: list[dict] = []
    for bill in bills:
        day = min(bill.due_day, last_day)  # clamp 31 onto short months
        due = date(year, month, day)
        payment = payments.get(bill.id)
        paid = payment is not None
        out.append(
            {
                "id": bill.id,
                "name": bill.name,
                "amount": bill.amount,
                "due_day": bill.due_day,
                "due_date": due,
                "category_id": bill.category_id,
                "paid": paid,
                "paid_at": payment.paid_at if payment else None,
                "overdue": (not paid) and due < today,
            }
        )
    return out


def _months_between(from_year: int, from_month: int, to_year: int, to_month: int) -> int:
    """Whole months from (from) to (to). Negative if (to) precedes (from)."""
    return (to_year - from_year) * 12 + (to_month - from_month)


def _add_months(year: int, month: int, delta: int) -> tuple[int, int]:
    """Shift a (year, month) by delta months, normalising the month into 1..12."""
    idx = (year * 12 + (month - 1)) + delta
    return idx // 12, (idx % 12) + 1


def installments_for_month(db: Session, user_id: int, year: int, month: int) -> list[dict]:
    """Project active installment plans onto (year, month).

    A plan contributes a charge to this month only if the month falls inside its
    span [start, start + total - 1]. We compute the 1-based installment number and
    how much is still owed from this month onward (this charge + future ones)."""
    plans = db.scalars(
        select(Installment).where(
            Installment.user_id == user_id, Installment.is_active.is_(True)
        )
    ).all()

    _, last_day = calendar.monthrange(year, month)
    out: list[dict] = []
    for p in plans:
        elapsed = _months_between(p.start_year, p.start_month, year, month)
        if elapsed < 0 or elapsed >= p.total_installments:
            continue  # this month is before the plan starts or after it ends
        number = elapsed + 1
        remaining_count = p.total_installments - elapsed  # this charge + the future ones
        end_year, end_month = _add_months(p.start_year, p.start_month, p.total_installments - 1)
        day = min(p.due_day, last_day)
        out.append(
            {
                "id": p.id,
                "description": p.description,
                "category_id": p.category_id,
                "installment_amount": p.installment_amount,
                "number": number,
                "total_installments": p.total_installments,
                "remaining_count": remaining_count,
                "remaining_amount": remaining_count * p.installment_amount,
                "due_date": date(year, month, day),
                "end_year": end_year,
                "end_month": end_month,
            }
        )
    out.sort(key=lambda r: r["due_date"])
    return out


def installments_outstanding(db: Session, user_id: int) -> float:
    """Total amount still owed across all active plans, counting from today's month."""
    today = date.today()
    return sum(
        r["remaining_amount"]
        for r in installments_for_month(db, user_id, today.year, today.month)
    )


def trend_for_months(db: Session, user_id: int, year: int, month: int, months: int) -> list[dict]:
    """Income/expense/balance for the `months` months ending at (year, month)."""
    points: list[dict] = []
    for i in range(months - 1, -1, -1):
        y, m = _add_months(year, month, -i)
        first, last = _month_bounds(y, m)
        txns = db.scalars(
            select(Transaction).where(
                Transaction.user_id == user_id,
                Transaction.date >= first,
                Transaction.date <= last,
            )
        ).all()
        income = sum(t.amount for t in txns if t.kind == TransactionKind.INCOME)
        expense = sum(t.amount for t in txns if t.kind == TransactionKind.EXPENSE)
        points.append(
            {
                "year": y,
                "month": m,
                "income": income,
                "expense": expense,
                "balance": income - expense,
            }
        )
    return points


def get_savings_goals(db: Session, user_id: int) -> list[SavingsGoal]:
    return list(
        db.scalars(
            select(SavingsGoal)
            .where(SavingsGoal.user_id == user_id, SavingsGoal.is_active.is_(True))
            .order_by(SavingsGoal.created_at)
        ).all()
    )


def build_overview(db: Session, user_id: int, year: int, month: int) -> dict:
    """Aggregate everything the finance dashboard needs for one month."""
    ensure_categories_seeded(db, user_id)
    first, last = _month_bounds(year, month)

    txns = db.scalars(
        select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.date >= first,
            Transaction.date <= last,
        )
    ).all()

    income = sum(t.amount for t in txns if t.kind == TransactionKind.INCOME)
    expense = sum(t.amount for t in txns if t.kind == TransactionKind.EXPENSE)
    balance = income - expense
    savings_rate = (balance / income) if income > 0 else 0.0

    categories = get_categories(db, user_id, active_only=True)
    cat_by_id = {c.id: c for c in categories}

    spent_by_cat: dict[int | None, float] = {}
    for t in txns:
        if t.kind == TransactionKind.EXPENSE:
            spent_by_cat[t.category_id] = spent_by_cat.get(t.category_id, 0.0) + t.amount

    cat_rows = []
    for c in categories:
        spent = spent_by_cat.get(c.id, 0.0)
        cat_rows.append(
            {
                "category_id": c.id,
                "name": c.name,
                "emoji": c.emoji,
                "color": c.color,
                "group": c.group.value,
                "budget": c.monthly_budget,
                "spent": spent,
                # Only flag overspend when a budget was actually set (>0).
                "over_budget": c.monthly_budget > 0 and spent > c.monthly_budget,
            }
        )

    group_rows = []
    for group, target in GROUP_TARGETS.items():
        members = [c for c in categories if c.group == group]
        member_ids = {c.id for c in members}
        g_budget = sum(c.monthly_budget for c in members)
        g_spent = sum(amt for cid, amt in spent_by_cat.items() if cid in member_ids)
        group_rows.append(
            {
                "group": group.value,
                "budget": g_budget,
                "spent": g_spent,
                "target_pct": target,
                "over_budget": g_budget > 0 and g_spent > g_budget,
            }
        )

    bills = bills_for_month(db, user_id, year, month)
    bills_total = sum(b["amount"] for b in bills)
    bills_paid = sum(b["amount"] for b in bills if b["paid"])

    installments = installments_for_month(db, user_id, year, month)
    installments_month = sum(i["installment_amount"] for i in installments)
    installments_outstanding_total = sum(i["remaining_amount"] for i in installments)

    return {
        "year": year,
        "month": month,
        "income": income,
        "expense": expense,
        "balance": balance,
        "savings_rate": savings_rate,
        "total_budget": sum(c.monthly_budget for c in categories),
        "bills_total": bills_total,
        "bills_paid": bills_paid,
        "bills_pending": bills_total - bills_paid,
        "bills_overdue": sum(1 for b in bills if b["overdue"]),
        "installments_month": installments_month,
        "installments_count": len(installments),
        "installments_outstanding": installments_outstanding_total,
        "groups": group_rows,
        "categories": cat_rows,
    }
