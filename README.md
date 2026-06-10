# Discipliner

A personal discipline and study tracker. Not a friendly productivity app — a training ground.

Every day it generates **one** challenge (math/physics problem + programming task), enforces a strict routine checklist, and tracks progress through a linear Backend + DevOps learning trail. AI never explains solutions: evaluation is PASS / FAIL / PARTIAL plus one sentence, nothing more.

The learning dynamic is built on the two techniques rated "high utility" by the research (Dunlosky et al., 2013): **spaced repetition** and **active recall** — trail topics automatically become review cards scheduled by an SM-2-lite algorithm — plus **Feynman explanations** to complete phases and a built-in **Pomodoro** timer for study sessions. See [docs/learning-method.md](docs/learning-method.md).

## Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| Backend | FastAPI (Python 3.12), SQLAlchemy 2, Alembic |
| Database | PostgreSQL 16 |
| Auth | JWT (python-jose) + bcrypt |
| AI | Anthropic Claude API (`claude-fable-5`) — challenge generation + evaluation only |
| Infra | Docker Compose (+ Nginx in production) |

## Quick start

```bash
cp .env.example .env   # fill in ANTHROPIC_API_KEY, DB_PASSWORD, SECRET_KEY
docker compose up --build
```

- Frontend: http://localhost:3000
- API: http://localhost:8000 (Swagger at /docs)

Full instructions: [docs/setup.md](docs/setup.md)

## Non-negotiable rules

1. No AI explains the solution. Evaluation = PASS/FAIL/PARTIAL + one sentence.
2. No skipping routine items. SKIPPED is permanently logged.
3. No skipping trail phases. The API rejects out-of-order completions.
4. The challenge is the same challenge all day. No regeneration button.
5. The math derivation is required (minimum 50 characters).
6. Plain textarea code editor. No syntax highlighting, no autocomplete, no AI.

## Documentation

- [Architecture](docs/architecture.md) — system overview + sequence diagrams
- [Learning method](docs/learning-method.md) — the evidence and how each technique maps to features
- [API reference](docs/api.md)
- [Learning trail](docs/trail.md) — the 6 phases
- [Setup](docs/setup.md) — local dev + production
# discipliner
