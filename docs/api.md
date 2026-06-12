# API Reference

Base URL: `http://localhost:8000`. All endpoints except `/health`, register, login, and refresh require `Authorization: Bearer <access_token>`.

Interactive docs: `http://localhost:8000/docs` (Swagger UI, auto-generated).

## Auth

### POST /api/v1/auth/register
Request: `{"email": "you@example.com", "password": "min 8 chars"}`
Response `201`: user object. `409` if email taken.

### POST /api/v1/auth/login
Request: `{"email": "...", "password": "..."}`
Response `200`: `{"access_token", "refresh_token", "token_type": "bearer"}`. `401` on bad credentials.

### POST /api/v1/auth/refresh
Request: `{"refresh_token": "..."}`
Response `200`: new token pair. `401` if invalid/expired.

### GET /api/v1/auth/me
Response `200`: `{"id", "email", "created_at", "current_phase"}`.

## Challenges

### GET /api/v1/challenges/today
Returns today's challenge. Generates it (one Claude call) if it does not exist yet; otherwise returns the cached row. There is no regeneration.

Response `200`:
```json
{
  "id": 1,
  "date": "2026-06-10",
  "title": "Projectile Range Optimizer",
  "math_problem": "...",
  "programming_task": "...",
  "difficulty": "beginner",
  "category": "physics",
  "expected_output_example": "max_range(10) → 10.2",
  "constraints": "Do not use any libraries."
}
```

### POST /api/v1/challenges/{id}/submit
Request: `{"math_derivation": "min 50 chars", "code_submission": "..."}`
Response `200`: `{"id", "challenge_id", "result": "PASS|FAIL|PARTIAL|PENDING", "reason", "submitted_at"}`
Errors: `422` if derivation under 50 chars; `404` if challenge not yours.

### GET /api/v1/challenges/history
Response `200`: list of `{"challenge": {...}, "submissions": [...]}`, newest first.

## Routine

Item keys: `wake_up_before_7`, `no_unnecessary_spending`, `study_session`, `daily_challenge`, `trail_review`.

### GET /api/v1/routine/today
Response `200`: `{"date", "items": [{"item_key", "label", "status": "DONE|LATE|SKIPPED|null", "logged_at"}]}`.

### PATCH /api/v1/routine/today/{item_id}
Request: `{"status": "DONE"}` or `{"status": "SKIPPED"}`.
Rules: logging is permanent (`409` if already logged). Checking `wake_up_before_7` as DONE after 7:00 AM server time records `LATE`.
Response `200`: the logged item.

### GET /api/v1/routine/week
Response `200`: `{"days": [RoutineDay × 7]}`, oldest first.

## Reviews (spaced repetition)

Cards are auto-created from trail topics for every phase the user has reached. See [learning-method.md](learning-method.md) for the scheduling algorithm.

### GET /api/v1/reviews/due
Seeds missing cards, then returns cards due today or earlier (oldest first).
Response `200`: `[{"id", "topic", "phase_id", "repetitions", "interval_days", "due_date"}]`.

### GET /api/v1/reviews/stats
Response `200`: `{"total", "due", "reviewed_today", "mature"}` (`mature` = repetitions ≥ 3).

### POST /api/v1/reviews/{card_id}/grade
Request: `{"grade": 0|1|2|3}` — 0=forgot, 1=hard, 2=good, 3=easy.
Reschedules the card (SM-2-lite) and auto-logs the `trail_review` routine item for today.
Response `200`: updated card. `404` if card not yours.

### Auto-logged routine items
- Grading any card → `trail_review` logged DONE.
- Submitting a challenge → `daily_challenge` logged DONE.

## Trail

### GET /api/v1/trail/phases
Response `200`: all 6 phases with topics and exercises.

### GET /api/v1/trail/progress
Response `200`: `{"current_phase", "phases": [{"phase", "started_at", "completed_at", "summary", "is_current"}]}`.

### POST /api/v1/trail/phase/{id}/complete
Request: `{"summary": "min 100 chars — what you learned"}`
Response `204`. Errors: `409` if out of order or already completed; `404` unknown phase; `422` summary too short.
