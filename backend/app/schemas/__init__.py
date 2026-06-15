from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


# --- Auth ---

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    password_confirm: str = Field(min_length=8)

    @model_validator(mode="after")
    def _passwords_match(self) -> "UserCreate":
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime
    current_phase: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=1)
    new_password: str = Field(min_length=8)


class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=1)


# --- Challenges ---

class ChallengeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date
    title: str
    math_problem: str
    programming_task: str
    difficulty: str
    category: str
    expected_output_example: str
    constraints: str


class SubmissionCreate(BaseModel):
    math_derivation: str = ""
    code_submission: str = Field(min_length=1)


class CodeExecuteRequest(BaseModel):
    code: str = Field(max_length=32_000)
    language: str = Field(pattern="^(java|c)$")


class CodeExecuteResult(BaseModel):
    output: str
    error: bool


class CustomChallengeRequest(BaseModel):
    description: str = Field(min_length=3, max_length=500)
    locale: str = Field(default="pt-BR", max_length=10)


class CustomChallengeOut(BaseModel):
    title: str
    math_problem: str
    programming_task: str
    difficulty: str
    category: str
    expected_output_example: str
    constraints: str


class SubmissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    challenge_id: int
    result: str
    reason: str
    submitted_at: datetime


class ChallengeHistoryItem(BaseModel):
    challenge: ChallengeOut
    submissions: list[SubmissionOut]


# --- Routine ---

class RoutineItemOut(BaseModel):
    item_key: str
    label: str
    status: str | None  # DONE / LATE / SKIPPED / None (not logged)
    logged_at: datetime | None


class RoutineCheckRequest(BaseModel):
    status: str = Field(pattern="^(DONE|SKIPPED)$")


class RoutineDayOut(BaseModel):
    date: date
    items: list[RoutineItemOut]


class RoutineWeekOut(BaseModel):
    days: list[RoutineDayOut]


class RoutineDaySummary(BaseModel):
    date: date
    done: int
    total: int
    skipped: int


class RoutineMonthOut(BaseModel):
    year: int
    month: int
    days: list[RoutineDaySummary]


class UserRoutineItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_key: str
    label: str
    is_system: bool
    is_active: bool
    position: int


class UserRoutineItemCreate(BaseModel):
    label: str = Field(min_length=2, max_length=200)


class UserRoutineItemToggle(BaseModel):
    is_active: bool


# --- Reviews (spaced repetition) ---

class ReviewCardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    topic: str
    phase_id: int
    repetitions: int
    interval_days: int
    due_date: date


class ReviewGradeRequest(BaseModel):
    grade: int = Field(ge=0, le=3, description="0=forgot, 1=hard, 2=good, 3=easy")


class ReviewStatsOut(BaseModel):
    total: int
    due: int
    reviewed_today: int
    mature: int


# --- Trail ---

class PhaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    number: int
    name: str
    weeks: str
    topics: list[str]
    exercises: list[str]


class PhaseProgressOut(BaseModel):
    phase: PhaseOut
    started_at: datetime | None
    completed_at: datetime | None
    summary: str
    is_current: bool


class TrailProgressOut(BaseModel):
    current_phase: int
    phases: list[PhaseProgressOut]


class PhaseCompleteRequest(BaseModel):
    summary: str = Field(min_length=100, description="Written summary of what was learned")


# --- English training ---

class EnglishExercise(BaseModel):
    item_id: int
    exercise_type: str
    prompt: str
    choices: list[str] | None = None


class EnglishSessionOut(BaseModel):
    items: list[EnglishExercise]
    done_today: int
    due_today: int


class EnglishAnswerRequest(BaseModel):
    item_id: int
    exercise_type: str = Field(
        pattern="^(multiple_choice_vocab|fill_in_the_blank|translate_pt_en|translate_en_pt)$"
    )
    answer: str = Field(min_length=1, max_length=500)


class EnglishAnswerResult(BaseModel):
    correct: bool
    correct_answer: str
    session_complete: bool


class EnglishStatsOut(BaseModel):
    due_today: int
    done_today: int
    pass_rate_7d: float
    mature_items: int
    total_items: int


# --- Finance / expense control ---

class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_key: str
    name: str
    emoji: str
    color: str
    group: str
    monthly_budget: float
    is_system: bool
    is_active: bool
    position: int


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    emoji: str = Field(default="tag", max_length=32)  # app icon key
    color: str = Field(default="#a3a3a3", max_length=9)
    group: str = Field(default="NEEDS", pattern="^(NEEDS|WANTS|SAVINGS)$")
    monthly_budget: float = Field(default=0.0, ge=0)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    emoji: str | None = Field(default=None, max_length=32)
    color: str | None = Field(default=None, max_length=9)
    group: str | None = Field(default=None, pattern="^(NEEDS|WANTS|SAVINGS)$")
    monthly_budget: float | None = Field(default=None, ge=0)
    is_active: bool | None = None


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int | None
    description: str
    amount: float
    kind: str
    date: date


class TransactionCreate(BaseModel):
    category_id: int | None = None
    description: str = Field(min_length=1, max_length=255)
    amount: float = Field(gt=0)
    kind: str = Field(default="EXPENSE", pattern="^(EXPENSE|INCOME)$")
    date: date


class BillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int | None
    name: str
    amount: float
    due_day: int
    is_active: bool


class BillCreate(BaseModel):
    category_id: int | None = None
    name: str = Field(min_length=1, max_length=120)
    amount: float = Field(gt=0)
    due_day: int = Field(ge=1, le=31)


class BillUpdate(BaseModel):
    category_id: int | None = None
    name: str | None = Field(default=None, min_length=1, max_length=120)
    amount: float | None = Field(default=None, gt=0)
    due_day: int | None = Field(default=None, ge=1, le=31)
    is_active: bool | None = None


class BillStatusOut(BaseModel):
    """A bill projected onto a specific month with its payment state."""

    id: int
    name: str
    amount: float
    due_day: int
    due_date: date
    category_id: int | None
    paid: bool
    paid_at: datetime | None
    overdue: bool


class CategorySpendOut(BaseModel):
    category_id: int
    name: str
    emoji: str
    color: str
    group: str
    budget: float
    spent: float
    over_budget: bool


class GroupSpendOut(BaseModel):
    group: str
    budget: float
    spent: float
    target_pct: int  # 50 / 30 / 20
    over_budget: bool


class RecommendationGroupOut(BaseModel):
    group: str          # NEEDS / WANTS / SAVINGS
    pct: int            # 50 / 30 / 20
    amount: float       # recommended R$ for this group


class RecommendationItemOut(BaseModel):
    key: str            # housing, food, transport, ...
    group: str
    pct: int
    amount: float


class RecommendationOut(BaseModel):
    income: float
    actual_spending: float
    leftover: float
    savings_rate: float
    status: str         # healthy / tight / over / unknown
    groups: list[RecommendationGroupOut]
    items: list[RecommendationItemOut]


class FinanceOverviewOut(BaseModel):
    year: int
    month: int
    income: float                    # one-off INCOME transactions this month
    expense: float                   # one-off EXPENSE transactions (lançamentos)
    balance: float                   # income - expense (transaction-only)
    savings_rate: float              # net / total_income
    recurring_income: float          # sum of active recurring income (salário + VR/VT)
    total_income: float              # recurring_income + income
    total_spending: float            # expense + bills_total + installments_month
    net: float                       # total_income - total_spending
    recommendation: RecommendationOut
    total_budget: float
    bills_total: float
    bills_paid: float
    bills_pending: float
    bills_overdue: int
    installments_month: float        # sum of installment charges landing this month
    installments_count: int          # how many plans are active this month
    installments_outstanding: float  # total still owed from this month onward
    groups: list[GroupSpendOut]
    categories: list[CategorySpendOut]


# --- Recurring income (renda fixa: salário + benefícios) ---

class RecurringIncomeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    amount: float
    kind: str
    is_active: bool


class RecurringIncomeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    amount: float = Field(gt=0)
    kind: str = Field(default="SALARY", pattern="^(SALARY|BENEFIT|OTHER)$")


class RecurringIncomeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    amount: float | None = Field(default=None, gt=0)
    kind: str | None = Field(default=None, pattern="^(SALARY|BENEFIT|OTHER)$")
    is_active: bool | None = None


# --- Installments (parcelas) ---

class InstallmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int | None
    description: str
    installment_amount: float
    total_installments: int
    start_year: int
    start_month: int
    due_day: int
    is_active: bool


class InstallmentCreate(BaseModel):
    category_id: int | None = None
    description: str = Field(min_length=1, max_length=255)
    installment_amount: float = Field(gt=0)
    total_installments: int = Field(ge=1, le=360)
    start_year: int = Field(ge=2020, le=2100)
    start_month: int = Field(ge=1, le=12)
    due_day: int = Field(default=1, ge=1, le=31)


class InstallmentUpdate(BaseModel):
    category_id: int | None = None
    description: str | None = Field(default=None, min_length=1, max_length=255)
    installment_amount: float | None = Field(default=None, gt=0)
    total_installments: int | None = Field(default=None, ge=1, le=360)
    start_year: int | None = Field(default=None, ge=2020, le=2100)
    start_month: int | None = Field(default=None, ge=1, le=12)
    due_day: int | None = Field(default=None, ge=1, le=31)
    is_active: bool | None = None


class InstallmentStatusOut(BaseModel):
    """An installment plan projected onto a specific month."""

    id: int
    description: str
    category_id: int | None
    installment_amount: float
    number: int               # which installment this month is (1-based)
    total_installments: int
    remaining_count: int      # this charge + future ones
    remaining_amount: float
    due_date: date
    end_year: int
    end_month: int


# --- Savings goals (metas) ---

class SavingsGoalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    target_amount: float
    current_amount: float
    emoji: str
    color: str
    deadline: date | None
    is_active: bool


class SavingsGoalCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    target_amount: float = Field(gt=0)
    current_amount: float = Field(default=0.0, ge=0)
    emoji: str = Field(default="target", max_length=32)  # app icon key
    color: str = Field(default="#4ade80", max_length=9)
    deadline: date | None = None


class SavingsGoalUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    target_amount: float | None = Field(default=None, gt=0)
    current_amount: float | None = Field(default=None, ge=0)
    emoji: str | None = Field(default=None, max_length=32)
    color: str | None = Field(default=None, max_length=9)
    deadline: date | None = None
    is_active: bool | None = None


class SavingsGoalContribute(BaseModel):
    amount: float = Field(gt=0)  # added to current_amount (negative not allowed here)


class TrendPointOut(BaseModel):
    year: int
    month: int
    income: float
    expense: float
    balance: float
