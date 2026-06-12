import re
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.limiter import limiter
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models import PasswordResetToken, User
from app.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    ResetPasswordRequest,
    TokenPair,
    UserCreate,
    UserOut,
)

_PASSWORD_RULES = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, payload: UserCreate, db: Session = Depends(get_db)):
    if not _PASSWORD_RULES.match(payload.password):
        raise HTTPException(
            status_code=422,
            detail="Password must be at least 8 characters and include uppercase, lowercase, and a digit.",
        )
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenPair)
@limiter.limit("10/minute")
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenPair(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/refresh", response_model=TokenPair)
@limiter.limit("20/minute")
def refresh(request: Request, payload: RefreshRequest, db: Session = Depends(get_db)):
    user_id = decode_token(payload.refresh_token, expected_type="refresh")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = db.get(User, int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return TokenPair(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/forgot-password", status_code=200)
@limiter.limit("3/minute")
def forgot_password(request: Request, payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    from app.services.email_service import send_reset_email

    user = db.scalar(select(User).where(User.email == payload.email))
    # Always return same response to prevent user enumeration
    _SAFE_RESPONSE = {"message": "If that email exists, a reset link was sent."}
    if user is None:
        return _SAFE_RESPONSE

    # Delete any previous unused tokens for this user
    old_tokens = db.scalars(
        select(PasswordResetToken).where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used.is_(False),
        )
    ).all()
    for t in old_tokens:
        db.delete(t)

    token_value = secrets.token_urlsafe(48)
    now = datetime.now(timezone.utc)
    db.add(
        PasswordResetToken(
            user_id=user.id,
            token=token_value,
            expires_at=now + timedelta(hours=1),
            used=False,
            created_at=now,
        )
    )
    db.commit()

    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token_value}"
    try:
        send_reset_email(user.email, reset_url)
    except Exception:
        pass  # logged inside send_reset_email; don't reveal failure to client

    return _SAFE_RESPONSE


@router.post("/reset-password", status_code=200)
@limiter.limit("10/minute")
def reset_password(request: Request, payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    record = db.scalar(
        select(PasswordResetToken).where(PasswordResetToken.token == payload.token)
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Invalid reset token")
    if record.used:
        raise HTTPException(status_code=410, detail="Reset token already used")
    if record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Reset token has expired")
    if not _PASSWORD_RULES.match(payload.new_password):
        raise HTTPException(
            status_code=422,
            detail="Password must be at least 8 characters and include uppercase, lowercase, and a digit.",
        )

    user = db.get(User, record.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(payload.new_password)
    record.used = True
    db.commit()
    return {"message": "Password updated successfully."}
