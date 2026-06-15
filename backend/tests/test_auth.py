"""
Auth endpoint integration tests.
Covers: register, login, email verification, forgot-password, reset-password.
Requires PostgreSQL (uses `client` fixture from conftest).
"""
import re
from datetime import datetime, timedelta, timezone

import pytest

_PASSWORD_RULES = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _register(client, email, password="Test123!"):
    """Register a user. Returns the response (always 202, anti-enumeration)."""
    return client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "password_confirm": password},
    )


def _latest_verification_token(db, email):
    from sqlalchemy import select
    from app.models import EmailVerificationToken, User

    user = db.scalar(select(User).where(User.email == email))
    return db.scalar(
        select(EmailVerificationToken)
        .where(EmailVerificationToken.user_id == user.id)
        .order_by(EmailVerificationToken.created_at.desc())
    )


def _register_and_verify(client, db, email, password="Test123!"):
    """Register and confirm a user so they can actually log in."""
    _register(client, email, password)
    token = _latest_verification_token(db, email)
    client.post("/api/v1/auth/verify-email", json={"token": token.token})


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
# Integration: register
# ---------------------------------------------------------------------------

def test_register_success(client, db):
    from sqlalchemy import select
    from app.models import User

    r = _register(client, "new@test.com")
    assert r.status_code == 202

    user = db.scalar(select(User).where(User.email == "new@test.com"))
    assert user is not None
    assert user.is_verified is False  # not usable until email confirmed


def test_register_weak_password_rejected(client):
    r = _register(client, "a@b.com", "weakpass")
    assert r.status_code == 422


def test_register_duplicate_email_returns_generic_response(client, db):
    """Re-registering must NOT reveal that the account exists (no enumeration)."""
    from sqlalchemy import select
    from app.models import User

    _register_and_verify(client, db, "dup@test.com")
    r = _register(client, "dup@test.com")
    # Same opaque 202 as a fresh registration.
    assert r.status_code == 202
    # And no second account was created.
    users = db.scalars(select(User).where(User.email == "dup@test.com")).all()
    assert len(users) == 1


def test_register_existing_unverified_resends_verification(client, db):
    """An unverified account re-registering gets a fresh verification token,
    not the dead-end 'you already have an account, just log in' email."""
    _register(client, "pending@test.com")
    first = _latest_verification_token(db, "pending@test.com")

    r = _register(client, "pending@test.com")
    assert r.status_code == 202

    db.expire_all()
    latest = _latest_verification_token(db, "pending@test.com")
    assert latest.token != first.token  # a new token was issued
    assert not latest.used
    assert latest.expires_at > datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Integration: email verification + login gating
# ---------------------------------------------------------------------------

def test_login_unverified_is_forbidden(client, db):
    _register(client, "unverified@test.com")
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "unverified@test.com", "password": "Test123!"},
    )
    assert r.status_code == 403


def test_login_success_after_verification(client, db):
    _register_and_verify(client, db, "login@test.com")
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "login@test.com", "password": "Test123!"},
    )
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_wrong_password(client, db):
    _register_and_verify(client, db, "wrong@test.com")
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@test.com", "password": "WrongPass1"},
    )
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

    _register_and_verify(client, db, "forgot@test.com")
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

    _register_and_verify(client, db, "reset@test.com")
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

    _register_and_verify(client, db, "single@test.com")
    client.post("/api/v1/auth/forgot-password", json={"email": "single@test.com"})

    user = db.scalar(select(User).where(User.email == "single@test.com"))
    token = db.scalar(select(PasswordResetToken).where(PasswordResetToken.user_id == user.id))

    client.post("/api/v1/auth/reset-password", json={"token": token.token, "new_password": "NewPass99!"})
    r2 = client.post("/api/v1/auth/reset-password", json={"token": token.token, "new_password": "AnotherPass1"})
    assert r2.status_code == 410


def test_reset_password_expired_token(client, db):
    from sqlalchemy import select
    from app.models import User, PasswordResetToken

    _register_and_verify(client, db, "expired@test.com")
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

    _register_and_verify(client, db, "weakreset@test.com")
    client.post("/api/v1/auth/forgot-password", json={"email": "weakreset@test.com"})

    user = db.scalar(select(User).where(User.email == "weakreset@test.com"))
    token = db.scalar(select(PasswordResetToken).where(PasswordResetToken.user_id == user.id))

    r = client.post("/api/v1/auth/reset-password", json={"token": token.token, "new_password": "weak"})
    assert r.status_code == 422
