# RFC: Forgot Password + Auth UX Improvements

**Status:** Implemented  
**Author:** FernandoHaeser  
**Date:** 2026-06-11

---

## 1. Motivation

Users who forget their password currently have no recovery path. Additionally, password fields across the app provide no feedback — users cannot see what they are typing, and signup/reset forms have no inline validation rules.

---

## 2. Scope

### In scope

- Forgot-password flow: email form → token email → reset form → success + back-to-login.
- Password reset token: 64-char random URL-safe token, 1-hour TTL, single-use.
- HTML email with reset link, branding, and expiry notice.
- `PasswordInput` component: eye toggle (show/hide) reusable across login, register, reset.
- `PasswordRules` component: inline validation (8+ chars, uppercase, lowercase, digit) shown on register and reset, not on login.
- Backend password validation on register and reset endpoints (422 if rules not met).

### Out of scope

- Magic-link login.
- SMS verification.
- OAuth providers.
- Email change flow.

---

## 3. Backend Design

### 3.1 Token lifecycle

```
POST /auth/forgot-password
  └─ find user by email (no 404 — always 200 to prevent user enumeration)
  └─ delete any existing unused tokens for that user
  └─ create PasswordResetToken (token = secrets.token_urlsafe(48), expires_at = now + 1h)
  └─ send email with FRONTEND_URL/reset-password?token=...
  └─ return {"message": "If that email exists, a reset link was sent."}

POST /auth/reset-password
  └─ look up token (404 if not found)
  └─ reject if expired (410 Gone)
  └─ reject if already used (410 Gone)
  └─ validate new_password strength (422 if fails)
  └─ hash + update user.hashed_password
  └─ mark token used
  └─ return 200
```

### 3.2 Password rules (backend + frontend)

| Rule | Regex / check |
|---|---|
| Minimum 8 characters | `len >= 8` |
| At least 1 uppercase | `[A-Z]` |
| At least 1 lowercase | `[a-z]` |
| At least 1 digit | `[0-9]` |

Applied on: `POST /auth/register`, `POST /auth/reset-password`.

### 3.3 Data model

```sql
password_reset_tokens (
  id          SERIAL PRIMARY KEY,
  user_id     INTEGER REFERENCES users(id) ON DELETE CASCADE,
  token       VARCHAR(128) NOT NULL UNIQUE,
  expires_at  TIMESTAMPTZ NOT NULL,
  used        BOOLEAN NOT NULL DEFAULT false,
  created_at  TIMESTAMPTZ NOT NULL
)
```

### 3.4 Email

Sent via SMTP (`smtplib` + `email.mime`). Config via env vars:

```
SMTP_HOST      mail.example.com
SMTP_PORT      587
SMTP_USER      noreply@discipliner.app
SMTP_PASSWORD  ...
SMTP_FROM      Discipliner <noreply@discipliner.app>
FRONTEND_URL   http://localhost:3000
```

If `SMTP_HOST` is empty, email is skipped and the token URL is logged (dev mode).

### 3.5 Rate limits

- `POST /forgot-password` → 3/minute per IP
- `POST /reset-password` → 10/minute per IP

---

## 4. Frontend Design

### New pages

| Route | Purpose |
|---|---|
| `/forgot-password` | Email input → submit → confirmation message |
| `/reset-password?token=...` | New password input → submit → success screen → back to login |

### New components

**`PasswordInput`** — drop-in replacement for `<Input type="password">`:
- Eye button toggles `type` between `password` and `text`.
- Accepts all `<input>` props.

**`PasswordRules`** — shows inline validation state:
```
● 8+ characters     ✓ uppercase     ✓ lowercase     ✓ number
```
- Each rule: muted dot when unmet, green check when met.
- Shown below password field on register and reset-password screens.
- Hidden on login (no validation required for reading).

### Modified pages

- **Login** — `PasswordInput` replaces plain password `<Input>`. "Esqueceu a senha?" link below form.
- **Register** — `PasswordInput` + `PasswordRules`. Submit blocked until all rules pass.

---

## 5. Security Notes

- `POST /forgot-password` always returns 200 with the same message regardless of whether the email exists (prevents user enumeration).
- Token is 48 bytes of `secrets.token_urlsafe` (384 bits entropy).
- Tokens are single-use and expire in 1 hour.
- Any new `forgot-password` request for the same user deletes previous tokens.
- New password is validated server-side independently of frontend state.
