# Local Development Setup

## Prerequisites

- Docker + Docker Compose
- An Anthropic API key (only used for daily challenge generation/evaluation)

## Quick start (Docker, recommended)

```bash
cp .env.example .env
# Edit .env: set ANTHROPIC_API_KEY, DB_PASSWORD, SECRET_KEY

docker compose up --build
```

This starts:
- PostgreSQL on `localhost:5432`
- Backend on `http://localhost:8000` (runs migrations + seed automatically)
- Frontend on `http://localhost:3000`

Generate a strong `SECRET_KEY`:

```bash
openssl rand -hex 32
```

## Running without Docker

### Database

```bash
docker compose up -d postgres
```

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export DATABASE_URL=postgresql://discipliner:<DB_PASSWORD>@localhost:5432/discipliner
export ANTHROPIC_API_KEY=<your key>
export SECRET_KEY=<your secret>

alembic upgrade head          # create tables
python -m app.db.seed         # seed trail phases + fallback challenges
uvicorn app.main:app --reload # http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev  # http://localhost:3000
```

## Tests

```bash
cd backend
pytest
```

## Migrations

```bash
cd backend
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

## Production

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

Production compose adds an Nginx reverse proxy on port 80 routing `/api` and `/health` to the backend and everything else to the frontend. Postgres is not exposed externally.
