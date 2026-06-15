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
