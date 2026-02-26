import random
import string
import smtplib
import os
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


CODE_LENGTH    = 6
EXPIRY_SECONDS = 600   
MAX_ATTEMPTS   = 5

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)


_store: dict = {}


def _clean_expired() -> None:
    now = time.time()
    for k in [k for k, v in _store.items() if v["expires"] < now]:
        del _store[k]


def generate_code(email: str) -> str:
    _clean_expired()
    code = "".join(random.choices(string.digits, k=CODE_LENGTH))
    _store[email.lower()] = {
        "code":     code,
        "expires":  time.time() + EXPIRY_SECONDS,
        "attempts": 0,
    }
    return code


def validate_code(email: str, code: str) -> tuple[bool, str]:
    _clean_expired()
    email = email.lower()
    entry = _store.get(email)

    if not entry:
        return False, "Código no encontrado o expirado"
    if time.time() > entry["expires"]:
        del _store[email]
        return False, "El código ha expirado. Solicita uno nuevo"

    if entry["code"] != code.strip():
        entry["attempts"] += 1
        if entry["attempts"] >= MAX_ATTEMPTS:
            del _store[email]
            return False, "Demasiados intentos. Solicita un nuevo código"
        remaining = MAX_ATTEMPTS - entry["attempts"]
        return False, f"Código incorrecto · {remaining} intentos restantes"

    del _store[email]
    return True, "ok"


def _build_html(code: str, username: str) -> str:
    digits = "".join(
        f'<span style="display:inline-block;width:48px;height:60px;line-height:60px;'
        f'text-align:center;font-size:28px;font-weight:900;color:#1c190d;'
        f'background:#f4d125;border-radius:10px;margin:0 4px;">{d}</span>'
        for d in code
    )
    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f0ede0;font-family:'Helvetica Neue',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0ede0;padding:40px 0;">
    <tr><td align="center">
      <table width="520" cellpadding="0" cellspacing="0"
             style="background:#ffffff;border-radius:20px;overflow:hidden;
                    box-shadow:0 8px 32px rgba(0,0,0,0.10);">
        <!-- Header -->
        <tr>
          <td style="background:#f4d125;padding:36px 48px 32px;">
            <table width="100%" cellpadding="0" cellspacing="0"><tr>
              <td>
                <span style="font-size:28px;font-weight:900;color:#1c190d;letter-spacing:-0.5px;">
                  &#x2328; PYLEARN
                </span>
                <p style="margin:6px 0 0;font-size:13px;color:#5a5020;font-weight:500;">
                  Python Learning Platform
                </p>
              </td>
              <td align="right"><span style="font-size:48px;line-height:1;">&#x1F40D;</span></td>
            </tr></table>
          </td>
        </tr>
        <!-- Body -->
        <tr>
          <td style="padding:40px 48px 32px;">
            <p style="margin:0 0 8px;font-size:22px;font-weight:800;color:#1c190d;">
              &#x1F44B; ¡Hola, {username}!
            </p>
            <p style="margin:0 0 28px;font-size:15px;color:#666;line-height:1.6;">
              Aquí tienes tu código de verificación para completar
              el registro en <strong style="color:#1c190d;">PYLEARN</strong>.
              Introdúcelo en la pantalla de registro.
            </p>
            <!-- Code tiles -->
            <div style="text-align:center;margin:0 0 28px;">
              <div style="display:inline-block;background:#faf8f0;border:2px solid #f4d125;
                          border-radius:16px;padding:24px 28px;">
                {digits}
              </div>
              <p style="margin:14px 0 0;font-size:12px;color:#999;">
                &#x23F1; Válido durante <strong>10 minutos</strong>
              </p>
            </div>
            <!-- Warning -->
            <div style="background:#faf8f0;border-left:4px solid #f4d125;
                        border-radius:8px;padding:16px 20px;">
              <p style="margin:0;font-size:13px;color:#666;line-height:1.6;">
                &#x1F512; Si no solicitaste este código, ignora este mensaje.
                Tu cuenta permanecerá segura.
              </p>
            </div>
          </td>
        </tr>
        <!-- Footer -->
        <tr>
          <td style="background:#f8f8f5;padding:24px 48px;border-top:1px solid #eee;">
            <p style="margin:0;font-size:12px;color:#aaa;text-align:center;line-height:1.6;">
              Email automático de PYLEARN · Por favor no respondas a este mensaje.
            </p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def send_verification_email(email: str, code: str, username: str = "desarrollador") -> tuple[bool, str]:
    """Send the 6-digit code by email. Falls back to console in dev mode."""
    if not SMTP_USER or not SMTP_PASS:
        print(f"\n[DEV] ── Código para {email}: {code} ──\n")
        return True, "Código enviado (modo desarrollo — revisa la consola)"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"{code} es tu código de verificación · PYLEARN"
    msg["From"]    = f"PYLEARN <{SMTP_FROM}>"
    msg["To"]      = email
    msg.attach(MIMEText(_build_html(code, username), "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_FROM, [email], msg.as_string())
        return True, "Código enviado. Revisa tu bandeja de entrada."
    except smtplib.SMTPAuthenticationError:
        return False, "Error de autenticación SMTP. Revisa tus credenciales."
    except Exception as exc:
        return False, f"No se pudo enviar el email: {exc}"
