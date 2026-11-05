"""Send one news-sniper alert to Telegram, Discord or email.

Reads secrets from .env (never from creator/profile.md — see
skills/news-sniper/references/alert-channel.md for why). Each channel needs
its own variables set there:

    TELEGRAM_BOT_TOKEN=...
    TELEGRAM_CHAT_ID=...
    DISCORD_WEBHOOK_URL=...
    ALERT_EMAIL_TO=...
    SMTP_HOST=...  SMTP_PORT=587  SMTP_USER=...  SMTP_PASSWORD=...

Usage:
    python scripts/send_alert.py --channel telegram --text "Big story just broke"
    python scripts/send_alert.py --channel discord --text "..." --dry-run

--dry-run builds the exact message and tells you which .env variables are
missing, but sends nothing — safe to run with no real bot/webhook set up yet.
Without --dry-run, telegram/discord need the `requests` package
(`pip install requests`); email uses only Python's built-in smtplib.
"""
import argparse
import os
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_TELEGRAM_CHARS = 4096
MAX_DISCORD_CHARS = 2000


def load_env(path: Path = ROOT / ".env") -> None:
    """Read KEY=VALUE lines from .env into os.environ, without needing python-dotenv.

    Skips blank lines and lines starting with #. Doesn't overwrite a variable
    that's already set in the real environment (lets a creator override with
    `set` / `export` for a one-off test without editing the file).
    """
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def missing_vars(names: list[str]) -> list[str]:
    """Which of these .env variable names are unset or blank."""
    return [name for name in names if not os.environ.get(name, "").strip()]


def _safe_error(err: Exception, secret: str) -> str:
    """The error message, with any raw secret (token/password/webhook) blanked out.

    requests/smtplib exceptions can embed the full URL or credential in their text —
    this keeps a real token from ever landing in a terminal, a log file or this
    project's own CI output.
    """
    text = str(err)
    if secret:
        text = text.replace(secret, "***")
    return text


def send_telegram(text: str, dry_run: bool) -> str:
    required = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    missing = missing_vars(required)
    if missing:
        return f"Missing from .env: {', '.join(missing)}. Nothing sent."
    if len(text) > MAX_TELEGRAM_CHARS:
        text = text[: MAX_TELEGRAM_CHARS - 1] + "…"

    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "disable_web_page_preview": False}

    if dry_run:
        return f"[dry run] would POST to {url.replace(token, '***')} with chat_id={chat_id}:\n{text}"

    import requests  # imported here so --dry-run never requires it installed

    try:
        r = requests.post(url, json=payload, timeout=20)
        r.raise_for_status()
    except requests.exceptions.RequestException as err:
        raise SystemExit(f"Telegram send failed: {_safe_error(err, token)}")
    return "Sent to Telegram."


def send_discord(text: str, dry_run: bool) -> str:
    required = ["DISCORD_WEBHOOK_URL"]
    missing = missing_vars(required)
    if missing:
        return f"Missing from .env: {', '.join(missing)}. Nothing sent."
    if len(text) > MAX_DISCORD_CHARS:
        text = text[: MAX_DISCORD_CHARS - 1] + "…"

    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
    payload = {"content": text}

    if dry_run:
        safe_url = webhook_url.rsplit("/", 1)[0] + "/***"
        return f"[dry run] would POST to {safe_url} with body:\n{payload}"

    import requests

    try:
        r = requests.post(webhook_url, json=payload, timeout=20)
        r.raise_for_status()
    except requests.exceptions.RequestException as err:
        raise SystemExit(f"Discord send failed: {_safe_error(err, webhook_url)}")
    return "Sent to Discord."


def send_email(text: str, dry_run: bool) -> str:
    required = ["ALERT_EMAIL_TO", "SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD"]
    missing = missing_vars(required)
    if missing:
        return f"Missing from .env: {', '.join(missing)}. Nothing sent."

    to_addr = os.environ["ALERT_EMAIL_TO"]
    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASSWORD"]

    msg = EmailMessage()
    msg["Subject"] = "Breaking news alert — news-sniper"
    msg["From"] = user
    msg["To"] = to_addr
    msg.set_content(text)

    if dry_run:
        return f"[dry run] would send email from {user} to {to_addr} via {host}:{port}:\n{text}"

    try:
        with smtplib.SMTP(host, port, timeout=20) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(msg)
    except smtplib.SMTPException as err:
        raise SystemExit(f"Email send failed: {_safe_error(err, password)}")
    return f"Sent to {to_addr}."


SENDERS = {
    "telegram": send_telegram,
    "discord": send_discord,
    "email": send_email,
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--channel", required=True, choices=sorted(SENDERS), help="where to send the alert")
    parser.add_argument("--text", required=True, help="the alert message (the news-sniper report's top story)")
    parser.add_argument("--dry-run", action="store_true", help="build the message and check .env, but send nothing")
    args = parser.parse_args()

    load_env()
    result = SENDERS[args.channel](args.text, args.dry_run)
    print(result)
    if result.startswith("Missing from .env"):
        sys.exit(1)


if __name__ == "__main__":
    main()
