import uuid
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import (
    BillPayment,
    BudgetGroup,
    ExpenseCategory,
    Installment,
    RecurringBill,
    SavingsGoal,
    Transaction,
    TransactionKind,
    User,
)
from app.schemas import (
    BillCreate,
    BillOut,
    BillStatusOut,
    BillUpdate,
    CategoryCreate,
    CategoryOut,
    CategoryUpdate,
    FinanceOverviewOut,
    InstallmentCreate,
    InstallmentOut,
    InstallmentStatusOut,
    InstallmentUpdate,
    SavingsGoalContribute,
    SavingsGoalCreate,
    SavingsGoalOut,
    SavingsGoalUpdate,
    TransactionCreate,
    TransactionOut,
    TrendPointOut,
)
from app.services.finance_service import (
    bills_for_month,
    build_overview,
    get_categories,
    get_savings_goals,
    installments_for_month,
    trend_for_months,
)

router = APIRouter(prefix="/finance", tags=["finance"])


# ── Overview ─────────────────────────────────────────────────────────────────

@router.get("/overview", response_model=FinanceOverviewOut)
def overview(
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return build_overview(db, current_user.id, year, month)


# ── Categories ───────────────────────────────────────────────────────────────

@router.get("/categories", response_model=list[CategoryOut])
def list_categories(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return get_categories(db, current_user.id)


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(
    payload: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    categories = get_categories(db, current_user.id)
    next_pos = max((c.position for c in categories), default=-1) + 1
    category = ExpenseCategory(
        user_id=current_user.id,
        category_key=f"custom_{uuid.uuid4().hex[:12]}",
        name=payload.name,
        emoji=payload.emoji,
        color=payload.color,
        group=BudgetGroup(payload.group),
        monthly_budget=payload.monthly_budget,
        is_system=False,
        is_active=True,
        position=next_pos,
        created_at=datetime.now(timezone.utc),
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.patch("/categories/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    category = db.scalar(
        select(ExpenseCategory).where(
            ExpenseCategory.id == category_id,
            ExpenseCategory.user_id == current_user.id,
        )
    )
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    if payload.name is not None:
        category.name = payload.name
    if payload.emoji is not None:
        category.emoji = payload.emoji
    if payload.color is not None:
        category.color = payload.color
    if payload.group is not None:
        category.group = BudgetGroup(payload.group)
    if payload.monthly_budget is not None:
        category.monthly_budget = payload.monthly_budget
    if payload.is_active is not None:
        category.is_active = payload.is_active

    db.commit()
    db.refresh(category)
    return category


@router.delete("/categories/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    category = db.scalar(
        select(ExpenseCategory).where(
            ExpenseCategory.id == category_id,
            ExpenseCategory.user_id == current_user.id,
        )
    )
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    # System categories are deactivated (not deleted) so seeding won't re-add them
    # and existing transactions keep a valid reference; custom ones are removed.
    if category.is_system:
        category.is_active = False
    else:
        db.delete(category)
    db.commit()


# ── Transactions ─────────────────────────────────────────────────────────────

@router.get("/transactions", response_model=list[TransactionOut])
def list_transactions(
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    import calendar

    _, last = calendar.monthrange(year, month)
    return list(
        db.scalars(
            select(Transaction)
            .where(
                Transaction.user_id == current_user.id,
                Transaction.date >= date(year, month, 1),
                Transaction.date <= date(year, month, last),
            )
            .order_by(Transaction.date.desc(), Transaction.id.desc())
        ).all()
    )


@router.post("/transactions", response_model=TransactionOut, status_code=201)
def create_transaction(
    payload: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.category_id is not None:
        owned = db.scalar(
            select(ExpenseCategory.id).where(
                ExpenseCategory.id == payload.category_id,
                ExpenseCategory.user_id == current_user.id,
            )
        )
        if owned is None:
            raise HTTPException(status_code=404, detail="Category not found")

    txn = Transaction(
        user_id=current_user.id,
        category_id=payload.category_id,
        description=payload.description,
        amount=payload.amount,
        kind=TransactionKind(payload.kind),
        date=payload.date,
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


@router.delete("/transactions/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    txn = db.scalar(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id,
        )
    )
    if txn is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(txn)
    db.commit()


# ── Recurring bills ──────────────────────────────────────────────────────────

@router.get("/bills", response_model=list[BillOut])
def list_bills(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return list(
        db.scalars(
            select(RecurringBill)
            .where(RecurringBill.user_id == current_user.id)
            .order_by(RecurringBill.due_day)
        ).all()
    )


@router.get("/bills/month", response_model=list[BillStatusOut])
def list_bills_month(
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return bills_for_month(db, current_user.id, year, month)


@router.post("/bills", response_model=BillOut, status_code=201)
def create_bill(
    payload: BillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bill = RecurringBill(
        user_id=current_user.id,
        category_id=payload.category_id,
        name=payload.name,
        amount=payload.amount,
        due_day=payload.due_day,
        is_active=True,
    )
    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill


@router.patch("/bills/{bill_id}", response_model=BillOut)
def update_bill(
    bill_id: int,
    payload: BillUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bill = db.scalar(
        select(RecurringBill).where(
            RecurringBill.id == bill_id, RecurringBill.user_id == current_user.id
        )
    )
    if bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")
    if payload.category_id is not None:
        bill.category_id = payload.category_id
    if payload.name is not None:
        bill.name = payload.name
    if payload.amount is not None:
        bill.amount = payload.amount
    if payload.due_day is not None:
        bill.due_day = payload.due_day
    if payload.is_active is not None:
        bill.is_active = payload.is_active
    db.commit()
    db.refresh(bill)
    return bill


@router.delete("/bills/{bill_id}", status_code=204)
def delete_bill(
    bill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bill = db.scalar(
        select(RecurringBill).where(
            RecurringBill.id == bill_id, RecurringBill.user_id == current_user.id
        )
    )
    if bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")
    db.delete(bill)  # BillPayment rows cascade
    db.commit()


@router.post("/bills/{bill_id}/pay", response_model=BillStatusOut)
def mark_bill_paid(
    bill_id: int,
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bill = db.scalar(
        select(RecurringBill).where(
            RecurringBill.id == bill_id, RecurringBill.user_id == current_user.id
        )
    )
    if bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")

    existing = db.scalar(
        select(BillPayment).where(
            BillPayment.bill_id == bill_id,
            BillPayment.year == year,
            BillPayment.month == month,
        )
    )
    if existing is None:
        db.add(
            BillPayment(
                bill_id=bill_id,
                user_id=current_user.id,
                year=year,
                month=month,
                amount=bill.amount,
            )
        )
        try:
            db.commit()
        except IntegrityError:
            db.rollback()

    return _bill_status(db, current_user.id, bill_id, year, month)


@router.delete("/bills/{bill_id}/pay", response_model=BillStatusOut)
def mark_bill_unpaid(
    bill_id: int,
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payment = db.scalar(
        select(BillPayment).where(
            BillPayment.bill_id == bill_id,
            BillPayment.user_id == current_user.id,
            BillPayment.year == year,
            BillPayment.month == month,
        )
    )
    if payment is not None:
        db.delete(payment)
        db.commit()
    return _bill_status(db, current_user.id, bill_id, year, month)


def _bill_status(db: Session, user_id: int, bill_id: int, year: int, month: int) -> dict:
    for status in bills_for_month(db, user_id, year, month):
        if status["id"] == bill_id:
            return status
    raise HTTPException(status_code=404, detail="Bill not found")


def _assert_category_owned(db: Session, user_id: int, category_id: int | None) -> None:
    """Reject a category_id that doesn't belong to the user (None means uncategorized)."""
    if category_id is None:
        return
    owned = db.scalar(
        select(ExpenseCategory.id).where(
            ExpenseCategory.id == category_id, ExpenseCategory.user_id == user_id
        )
    )
    if owned is None:
        raise HTTPException(status_code=404, detail="Category not found")


# ── Trend ────────────────────────────────────────────────────────────────────

@router.get("/trend", response_model=list[TrendPointOut])
def trend(
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
    months: int = Query(6, ge=2, le=24),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return trend_for_months(db, current_user.id, year, month, months)


# ── Installments (parcelas) ──────────────────────────────────────────────────

@router.get("/installments", response_model=list[InstallmentOut])
def list_installments(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return list(
        db.scalars(
            select(Installment)
            .where(Installment.user_id == current_user.id)
            .order_by(Installment.created_at.desc())
        ).all()
    )


@router.get("/installments/month", response_model=list[InstallmentStatusOut])
def list_installments_month(
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return installments_for_month(db, current_user.id, year, month)


@router.post("/installments", response_model=InstallmentOut, status_code=201)
def create_installment(
    payload: InstallmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _assert_category_owned(db, current_user.id, payload.category_id)
    plan = Installment(
        user_id=current_user.id,
        category_id=payload.category_id,
        description=payload.description,
        installment_amount=payload.installment_amount,
        total_installments=payload.total_installments,
        start_year=payload.start_year,
        start_month=payload.start_month,
        due_day=payload.due_day,
        is_active=True,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.patch("/installments/{installment_id}", response_model=InstallmentOut)
def update_installment(
    installment_id: int,
    payload: InstallmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = db.scalar(
        select(Installment).where(
            Installment.id == installment_id, Installment.user_id == current_user.id
        )
    )
    if plan is None:
        raise HTTPException(status_code=404, detail="Installment not found")
    if payload.category_id is not None:
        _assert_category_owned(db, current_user.id, payload.category_id)
        plan.category_id = payload.category_id
    if payload.description is not None:
        plan.description = payload.description
    if payload.installment_amount is not None:
        plan.installment_amount = payload.installment_amount
    if payload.total_installments is not None:
        plan.total_installments = payload.total_installments
    if payload.start_year is not None:
        plan.start_year = payload.start_year
    if payload.start_month is not None:
        plan.start_month = payload.start_month
    if payload.due_day is not None:
        plan.due_day = payload.due_day
    if payload.is_active is not None:
        plan.is_active = payload.is_active
    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/installments/{installment_id}", status_code=204)
def delete_installment(
    installment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = db.scalar(
        select(Installment).where(
            Installment.id == installment_id, Installment.user_id == current_user.id
        )
    )
    if plan is None:
        raise HTTPException(status_code=404, detail="Installment not found")
    db.delete(plan)
    db.commit()


# ── Savings goals (metas) ────────────────────────────────────────────────────

@router.get("/goals", response_model=list[SavingsGoalOut])
def list_goals(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return get_savings_goals(db, current_user.id)


@router.post("/goals", response_model=SavingsGoalOut, status_code=201)
def create_goal(
    payload: SavingsGoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    goal = SavingsGoal(
        user_id=current_user.id,
        name=payload.name,
        target_amount=payload.target_amount,
        current_amount=payload.current_amount,
        emoji=payload.emoji,
        color=payload.color,
        deadline=payload.deadline,
        is_active=True,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.patch("/goals/{goal_id}", response_model=SavingsGoalOut)
def update_goal(
    goal_id: int,
    payload: SavingsGoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    goal = _get_owned_goal(db, current_user.id, goal_id)
    if payload.name is not None:
        goal.name = payload.name
    if payload.target_amount is not None:
        goal.target_amount = payload.target_amount
    if payload.current_amount is not None:
        goal.current_amount = payload.current_amount
    if payload.emoji is not None:
        goal.emoji = payload.emoji
    if payload.color is not None:
        goal.color = payload.color
    if payload.deadline is not None:
        goal.deadline = payload.deadline
    if payload.is_active is not None:
        goal.is_active = payload.is_active
    db.commit()
    db.refresh(goal)
    return goal


@router.post("/goals/{goal_id}/contribute", response_model=SavingsGoalOut)
def contribute_goal(
    goal_id: int,
    payload: SavingsGoalContribute,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    goal = _get_owned_goal(db, current_user.id, goal_id)
    # Clamp at 0 so a future "withdraw" variant can't push the balance negative.
    goal.current_amount = max(0.0, goal.current_amount + payload.amount)
    db.commit()
    db.refresh(goal)
    return goal


@router.delete("/goals/{goal_id}", status_code=204)
def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    goal = _get_owned_goal(db, current_user.id, goal_id)
    db.delete(goal)
    db.commit()


def _get_owned_goal(db: Session, user_id: int, goal_id: int) -> SavingsGoal:
    goal = db.scalar(
        select(SavingsGoal).where(
            SavingsGoal.id == goal_id, SavingsGoal.user_id == user_id
        )
    )
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal
