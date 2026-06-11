"""Email delivery via SMTP.

If SMTP_HOST is empty, the reset URL is logged to stdout (dev mode).
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


def _html_reset_email(reset_url: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Redefinir senha — Discipliner</title>
</head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#e5e5e5;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0a;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="480" cellpadding="0" cellspacing="0" style="background:#111;border:1px solid #222;border-radius:16px;overflow:hidden;">

          <!-- Header -->
          <tr>
            <td style="padding:32px 40px 24px;border-bottom:1px solid #222;">
              <p style="margin:0;font-size:20px;font-weight:800;letter-spacing:-0.5px;color:#fff;">
                discipliner
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:32px 40px;">
              <h1 style="margin:0 0 12px;font-size:22px;font-weight:800;letter-spacing:-0.3px;color:#fff;">
                Redefinir sua senha
              </h1>
              <p style="margin:0 0 24px;font-size:15px;line-height:1.6;color:#999;">
                Recebemos uma solicitação para redefinir a senha da sua conta.
                Clique no botão abaixo para criar uma nova senha.
              </p>

              <!-- CTA Button -->
              <table cellpadding="0" cellspacing="0" style="margin:0 0 28px;">
                <tr>
                  <td style="border-radius:10px;background:#fff;">
                    <a href="{reset_url}"
                       style="display:inline-block;padding:12px 28px;font-size:14px;font-weight:700;color:#0a0a0a;text-decoration:none;letter-spacing:-0.2px;">
                      Redefinir senha →
                    </a>
                  </td>
                </tr>
              </table>

              <p style="margin:0 0 8px;font-size:13px;color:#666;">
                Este link expira em <strong style="color:#999;">1 hora</strong>.
              </p>
              <p style="margin:0;font-size:13px;color:#555;">
                Se você não solicitou a redefinição, ignore este e-mail. Sua senha permanece a mesma.
              </p>
            </td>
          </tr>

          <!-- URL fallback -->
          <tr>
            <td style="padding:0 40px 32px;">
              <p style="margin:0 0 6px;font-size:11px;color:#444;text-transform:uppercase;letter-spacing:0.08em;">
                Link direto
              </p>
              <p style="margin:0;font-size:11px;color:#555;word-break:break-all;">
                {reset_url}
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:20px 40px;border-top:1px solid #1a1a1a;">
              <p style="margin:0;font-size:11px;color:#444;text-align:center;">
                Discipliner — Sem atalhos. Sem gamificação.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def send_reset_email(to_email: str, reset_url: str) -> None:
    if not settings.SMTP_HOST:
        logger.info("SMTP_HOST not set — dev mode. Reset URL: %s", reset_url)
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Redefinir senha — Discipliner"
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email

    plain = (
        f"Discipliner — Redefinir senha\n\n"
        f"Clique no link abaixo para redefinir sua senha (válido por 1 hora):\n\n"
        f"{reset_url}\n\n"
        f"Se você não solicitou isso, ignore este e-mail."
    )
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(_html_reset_email(reset_url), "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.sendmail(settings.SMTP_FROM, to_email, msg.as_string())
    except Exception:
        logger.exception("Failed to send reset email to %s", to_email)
        raise
