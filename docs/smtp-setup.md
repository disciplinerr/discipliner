# SMTP Setup — Forgot Password Email

Discipliner sends password reset emails via SMTP. If `SMTP_HOST` is empty (default), the reset URL is logged to stdout instead — useful for local development.

---

## Environment variables

Add these to your `.env`:

```env
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=noreply@yourdomain.com
SMTP_PASSWORD=your_smtp_password
SMTP_FROM=Discipliner <noreply@yourdomain.com>
FRONTEND_URL=https://yourdomain.com
```

---

## Option 1 — Gmail (personal / Google Workspace)

Google requires an **App Password** (not your account password).

1. Enable 2-Step Verification on your Google account.
2. Go to **Google Account → Security → App passwords**.
3. Create a new app password (select "Mail" + "Other").
4. Copy the 16-character password.

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx   # 16-char app password, spaces optional
SMTP_FROM=Discipliner <you@gmail.com>
```

---

## Option 2 — Resend (recommended for production)

[Resend](https://resend.com) is a developer-focused email API with an SMTP interface.

1. Create a free account at resend.com.
2. Add and verify your sending domain.
3. Go to **API Keys** and create a key.

```env
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_USER=resend
SMTP_PASSWORD=re_xxxxxxxxxxxxxxxxxxxxxxxx   # your Resend API key
SMTP_FROM=Discipliner <noreply@yourdomain.com>
```

Free tier: 3,000 emails/month, 100/day.

---

## Option 3 — Mailgun

1. Create an account at mailgun.com.
2. Add and verify your domain.
3. Go to **Sending → Domain Settings → SMTP credentials**.

```env
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@mg.yourdomain.com
SMTP_PASSWORD=your_mailgun_smtp_password
SMTP_FROM=Discipliner <noreply@yourdomain.com>
```

---

## Option 4 — Amazon SES

1. Verify your sending domain in SES.
2. Go to **SMTP Settings** in the SES console.
3. Create SMTP credentials (IAM user with SES send permissions).

```env
SMTP_HOST=email-smtp.us-east-1.amazonaws.com   # change region as needed
SMTP_PORT=587
SMTP_USER=AKIAIOSFODNN7EXAMPLE
SMTP_PASSWORD=your_ses_smtp_password
SMTP_FROM=Discipliner <noreply@yourdomain.com>
```

---

## Dev mode (no SMTP)

Leave `SMTP_HOST` empty. The reset URL is printed to the backend log:

```
INFO  email_service - SMTP_HOST not set — dev mode. Reset URL: http://localhost:3000/reset-password?token=...
```

Copy the URL directly into your browser to test the reset flow.

---

## Troubleshooting

| Error | Likely cause | Fix |
|---|---|---|
| `Connection refused` | Wrong host or port | Check `SMTP_HOST` and `SMTP_PORT` |
| `Authentication failed` | Wrong credentials | Use App Password for Gmail, not account password |
| `TLS required` | Port 465 uses implicit TLS | Change port to 587 (STARTTLS) or update `email_service.py` to use `SMTP_SSL` |
| Emails go to spam | Domain not configured for sending | Set up SPF, DKIM, and DMARC records for your domain |

---

## SPF / DKIM / DMARC (production checklist)

Without these DNS records, email providers will likely mark your messages as spam.

| Record | Purpose |
|---|---|
| `SPF` (TXT) | Lists servers allowed to send email for your domain |
| `DKIM` (TXT) | Cryptographically signs outgoing messages |
| `DMARC` (TXT) | Tells receivers what to do with unauthenticated mail |

Your email provider (Resend, Mailgun, SES) will give you the exact DNS records to add.
