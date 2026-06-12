"""
Auth endpoint integration tests.
Covers: register, login, forgot-password, reset-password.
Requires PostgreSQL (uses `client` fixture from conftest).
"""
import re
from datetime import datetime, timedelta, timezone

import pytest

_PASSWORD_RULES = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")

# ---------------------------------------------------------------------------
# Pure unit: password validation regex
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("password,valid", [
    ("Test123!", True),
    ("Abcdefg1", True),
    ("abcdefg1", False),   # no uppercase
    ("ABCDEFG1", False),   # no lowercase
    ("Abcdefgh", False),   # no digit
    ("Ab1", False),        # too short
    ("", False),
])
def test_password_rules_regex(password, valid):
    assert bool(_PASSWORD_RULES.match(password)) == valid


# ---------------------------------------------------------------------------
# Integration: register & login
# ---------------------------------------------------------------------------

def test_register_success(client):
    r = client.post("/api/v1/auth/register", json={"email": "new@test.com", "password": "Test123!"})
    assert r.status_code == 201
    assert r.json()["email"] == "new@test.com"


def test_register_weak_password_rejected(client):
    r = client.post("/api/v1/auth/register", json={"email": "a@b.com", "password": "weakpass"})
    assert r.status_code == 422


def test_register_duplicate_email_rejected(client):
    payload = {"email": "dup@test.com", "password": "Test123!"}
    client.post("/api/v1/auth/register", json=payload)
    r = client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 409


def test_login_success(client):
    client.post("/api/v1/auth/register", json={"email": "login@test.com", "password": "Test123!"})
    r = client.post("/api/v1/auth/login", json={"email": "login@test.com", "password": "Test123!"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_wrong_password(client):
    client.post("/api/v1/auth/register", json={"email": "wrong@test.com", "password": "Test123!"})
    r = client.post("/api/v1/auth/login", json={"email": "wrong@test.com", "password": "WrongPass1"})
    assert r.status_code == 401


# ---------------------------------------------------------------------------
# Integration: forgot-password / reset-password
# ---------------------------------------------------------------------------

def test_forgot_password_unknown_email_still_200(client):
    r = client.post("/api/v1/auth/forgot-password", json={"email": "ghost@nowhere.com"})
    assert r.status_code == 200


def test_forgot_password_known_email_creates_token(client, db):
    from sqlalchemy import select
    from app.models import User, PasswordResetToken

    client.post("/api/v1/auth/register", json={"email": "forgot@test.com", "password": "Test123!"})
    r = client.post("/api/v1/auth/forgot-password", json={"email": "forgot@test.com"})
    assert r.status_code == 200

    user = db.scalar(select(User).where(User.email == "forgot@test.com"))
    token = db.scalar(select(PasswordResetToken).where(PasswordResetToken.user_id == user.id))
    assert token is not None
    assert not token.used
    assert token.expires_at > datetime.now(timezone.utc)


def test_reset_password_success(client, db):
    from sqlalchemy import select
    from app.models import User, PasswordResetToken

    client.post("/api/v1/auth/register", json={"email": "reset@test.com", "password": "Test123!"})
    client.post("/api/v1/auth/forgot-password", json={"email": "reset@test.com"})

    user = db.scalar(select(User).where(User.email == "reset@test.com"))
    token = db.scalar(select(PasswordResetToken).where(PasswordResetToken.user_id == user.id))

    r = client.post("/api/v1/auth/reset-password", json={
        "token": token.token,
        "new_password": "NewPass99!",
    })
    assert r.status_code == 200

    db.refresh(token)
    assert token.used


def test_reset_password_token_single_use(client, db):
    from sqlalchemy import select
    from app.models import User, PasswordResetToken

    client.post("/api/v1/auth/register", json={"email": "single@test.com", "password": "Test123!"})
    client.post("/api/v1/auth/forgot-password", json={"email": "single@test.com"})

    user = db.scalar(select(User).where(User.email == "single@test.com"))
    token = db.scalar(select(PasswordResetToken).where(PasswordResetToken.user_id == user.id))

    client.post("/api/v1/auth/reset-password", json={"token": token.token, "new_password": "NewPass99!"})
    r2 = client.post("/api/v1/auth/reset-password", json={"token": token.token, "new_password": "AnotherPass1"})
    assert r2.status_code == 410


def test_reset_password_expired_token(client, db):
    from sqlalchemy import select
    from app.models import User, PasswordResetToken

    client.post("/api/v1/auth/register", json={"email": "expired@test.com", "password": "Test123!"})
    client.post("/api/v1/auth/forgot-password", json={"email": "expired@test.com"})

    user = db.scalar(select(User).where(User.email == "expired@test.com"))
    token = db.scalar(select(PasswordResetToken).where(PasswordResetToken.user_id == user.id))

    token.expires_at = datetime.now(timezone.utc) - timedelta(hours=2)
    db.commit()

    r = client.post("/api/v1/auth/reset-password", json={"token": token.token, "new_password": "NewPass99!"})
    assert r.status_code == 410


def test_reset_password_weak_password_rejected(client, db):
    from sqlalchemy import select
    from app.models import User, PasswordResetToken

    client.post("/api/v1/auth/register", json={"email": "weakreset@test.com", "password": "Test123!"})
    client.post("/api/v1/auth/forgot-password", json={"email": "weakreset@test.com"})

    user = db.scalar(select(User).where(User.email == "weakreset@test.com"))
    token = db.scalar(select(PasswordResetToken).where(PasswordResetToken.user_id == user.id))

    r = client.post("/api/v1/auth/reset-password", json={"token": token.token, "new_password": "weak"})
    assert r.status_code == 422
