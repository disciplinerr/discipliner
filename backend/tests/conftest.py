"""
Test configuration.

Pure unit tests (no `db` fixture): run anywhere, no external deps.
Integration tests (use `db` or `client` fixture): require the Docker PostgreSQL
to be reachable on localhost:5432. Run with `pytest tests/` — they skip
automatically if the DB is not available.
"""
import os

# Must be set before any `from app...` import so lru_cache picks them up.
_TEST_SECRET = "discipliner-test-secret-key-for-pytest-only-32plus"
os.environ.setdefault("SECRET_KEY", _TEST_SECRET)
os.environ.setdefault(
    "DATABASE_URL",
    os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://discipliner:Yourboos0202@localhost:5432/discipliner_test",
    ),
)
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker

from app.db.base_class import Base
import app.models  # noqa: F401 — registers all models on Base


# ---------------------------------------------------------------------------
# Test database setup (PostgreSQL, isolated schema)
# ---------------------------------------------------------------------------

_TEST_DB_URL = os.environ["DATABASE_URL"]
_ADMIN_URL = _TEST_DB_URL.rsplit("/", 1)[0] + "/postgres"


def _ensure_test_db() -> bool:
    """Create discipliner_test if missing. Returns True if DB is reachable."""
    try:
        engine = create_engine(
            _ADMIN_URL,
            isolation_level="AUTOCOMMIT",
            connect_args={"connect_timeout": 3},
        )
        with engine.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = 'discipliner_test'")
            ).scalar()
            if not exists:
                conn.execute(text("CREATE DATABASE discipliner_test"))
        engine.dispose()
        return True
    except Exception:
        return False


_DB_AVAILABLE = _ensure_test_db()


@pytest.fixture(scope="session")
def engine():
    if not _DB_AVAILABLE:
        pytest.skip("PostgreSQL not reachable — skipping integration tests")
    eng = create_engine(_TEST_DB_URL)
    # Create all tables (idempotent — uses checkfirst)
    Base.metadata.create_all(eng, checkfirst=True)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture()
def db(engine):
    """
    Transactional DB session: each test runs inside a savepoint that is
    rolled back after the test, leaving the DB clean for the next one.
    """
    connection = engine.connect()
    transaction = connection.begin()
    TestSession = sessionmaker(bind=connection, autocommit=False, autoflush=False)
    session = TestSession()

    # Nested savepoint so rollback inside the service doesn't close the outer tx
    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    """FastAPI TestClient with the test DB wired in and rate limiting disabled."""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.db.session import get_db
    from app.core.limiter import limiter

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Reset in-memory rate limit counters so tests don't bleed into each other
    try:
        limiter._storage.reset()
    except Exception:
        pass

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()
