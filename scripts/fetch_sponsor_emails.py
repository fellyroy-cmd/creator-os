"""Fetch brand/sponsorship emails from the creator's own inbox, read-only.

Connects over IMAP in **read-only mode** (`readonly=True` — the library itself refuses to
change anything on the server this way) and searches the last N days of a chosen folder for
messages matching keywords, then prints each match's sender, subject, date and plain-text body
so the creator can paste one into sponsor-desk's Step 1.

This script never sends anything, never deletes anything, and never modifies a flag or label
unless --mark-read is passed explicitly (off by default — see --mark-read below).

Needs in .env (never in creator/profile.md or creator/rate-card.md — see
skills/sponsor-desk/references/gmail-connection.md for how to get these):

    GMAIL_ADDRESS=you@gmail.com
    GMAIL_APP_PASSWORD=...          # a 16-character Google "app password", not your real password

Usage:
    python scripts/fetch_sponsor_emails.py
    python scripts/fetch_sponsor_emails.py --days 14 --limit 10
    python scripts/fetch_sponsor_emails.py --query "sponsor OR partnership OR collab"
    python scripts/fetch_sponsor_emails.py --dry-run

--dry-run connects, confirms the login works and the folder is reachable, then disconnects
without searching or printing any real email content — safe to run as a first connection test.
"""
import argparse
import email
import email.message
import imaplib
import os
import sys
from datetime import datetime, timedelta
from email.header import decode_header
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993
DEFAULT_QUERY = "sponsor OR sponsorship OR partnership OR collab OR collaboration OR advertise OR ambassador"
MAX_BODY_CHARS = 3000


def load_env(path: Path = ROOT / ".env") -> None:
    """Read KEY=VALUE lines from .env into os.environ, without needing python-dotenv.

    Same loader as scripts/send_alert.py, kept identical on purpose so there's only one
    pattern to learn across the whole project.
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
    return [name for name in names if not os.environ.get(name, "").strip()]


def _decode(raw) -> str:
    """Turn an email header (sender/subject) into a plain readable string."""
    if raw is None:
        return ""
    parts = decode_header(raw)
    out = []
    for text, charset in parts:
        if isinstance(text, bytes):
            out.append(text.decode(charset or "utf-8", errors="replace"))
        else:
            out.append(text)
    return "".join(out)


def _plain_text_body(msg: email.message.Message) -> str:
    """Pull the plain-text part out of an email, falling back to a stripped HTML part."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(part.get_content_charset() or "utf-8", errors="replace")
        for part in msg.walk():
            if part.get_content_type() == "text/html" and not part.get("Content-Disposition"):
                payload = part.get_payload(decode=True)
                if payload:
                    html = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
                    return _strip_html(html)
        return ""
    payload = msg.get_payload(decode=True)
    if not payload:
        return ""
    text = payload.decode(msg.get_content_charset() or "utf-8", errors="replace")
    if msg.get_content_type() == "text/html":
        return _strip_html(text)
    return text


def _strip_html(html: str) -> str:
    """Rough HTML-to-text fallback — good enough for a human to read, not a renderer."""
    import re

    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def _imap_query(query: str, since: datetime) -> str:
    """Build an IMAP SEARCH string: OR'd keywords in subject or body, since a given date.

    IMAP's OR takes exactly two arguments, so a list of keywords has to be nested
    (OR a (OR b (OR c d))) rather than passed flat.
    """
    keywords = [kw.strip() for kw in query.replace(" OR ", "|").split("|") if kw.strip()]
    since_str = since.strftime("%d-%b-%Y")

    def term(kw: str) -> str:
        return f'(OR SUBJECT "{kw}" BODY "{kw}")'

    if not keywords:
        return f"SINCE {since_str}"
    expr = term(keywords[-1])
    for kw in reversed(keywords[:-1]):
        expr = f"OR {term(kw)} {expr}"
    return f"{expr} SINCE {since_str}"


def fetch(days: int, limit: int, query: str, folder: str, mark_read: bool, dry_run: bool) -> list[dict]:
    required = ["GMAIL_ADDRESS", "GMAIL_APP_PASSWORD"]
    missing = missing_vars(required)
    if missing:
        print(f"Missing from .env: {', '.join(missing)}. Nothing fetched.")
        print("See skills/sponsor-desk/references/gmail-connection.md for how to get an app password.")
        sys.exit(1)

    address = os.environ["GMAIL_ADDRESS"]
    app_password = os.environ["GMAIL_APP_PASSWORD"]

    # readonly=True: the server rejects any attempt to change flags, move, or delete over this
    # connection. That's enforced by imaplib/the server, not just a promise in this script.
    imap = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    try:
        imap.login(address, app_password)
    except imaplib.IMAP4.error as err:
        raise SystemExit(
            f"Gmail login failed: {err}. Check GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .env — "
            "most failures here mean the app password was mistyped or has been revoked."
        )

    status, _ = imap.select(folder, readonly=not mark_read)
    if status != "OK":
        imap.logout()
        raise SystemExit(f"Could not open folder '{folder}'. Check the name (Gmail labels are case-sensitive).")

    if dry_run:
        imap.logout()
        print(f"[dry run] Logged in as {address}, opened '{folder}' read-only. Connection works. Nothing searched.")
        return []

    since = datetime.now() - timedelta(days=days)
    search_str = _imap_query(query, since)
    status, data = imap.search(None, search_str)
    if status != "OK":
        imap.logout()
        raise SystemExit("IMAP search failed — try a simpler --query.")

    ids = data[0].split()
    ids = ids[-limit:] if limit else ids  # newest N (IMAP returns ids in ascending order)

    results = []
    for msg_id in reversed(ids):  # newest first
        status, msg_data = imap.fetch(msg_id, "(RFC822)")
        if status != "OK" or not msg_data or not msg_data[0]:
            continue
        msg = email.message_from_bytes(msg_data[0][1])
        body = _plain_text_body(msg).strip()
        if len(body) > MAX_BODY_CHARS:
            body = body[:MAX_BODY_CHARS] + "\n…[truncated]"
        results.append(
            {
                "from": _decode(msg.get("From")),
                "subject": _decode(msg.get("Subject")),
                "date": msg.get("Date", ""),
                "body": body,
            }
        )

    imap.logout()
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--days", type=int, default=7, help="how many days back to search (default: 7)")
    parser.add_argument("--limit", type=int, default=15, help="max matching emails to return (default: 15)")
    parser.add_argument("--query", default=DEFAULT_QUERY, help="keywords, separated by ' OR ' (default: sponsor-ish terms)")
    parser.add_argument("--folder", default="INBOX", help="Gmail folder/label to search (default: INBOX)")
    parser.add_argument(
        "--mark-read",
        action="store_true",
        help="open the folder read-write so matches are marked read (off by default — "
        "fetching normally does NOT change anything on the server)",
    )
    parser.add_argument("--dry-run", action="store_true", help="test the login and folder only, fetch nothing")
    args = parser.parse_args()

    load_env()
    results = fetch(args.days, args.limit, args.query, args.folder, args.mark_read, args.dry_run)

    if args.dry_run:
        return
    if not results:
        print(f"No emails matched in the last {args.days} day(s) of '{args.folder}'.")
        return

    print(f"Found {len(results)} matching email(s):\n")
    for i, msg in enumerate(results, 1):
        print(f"--- [{i}] {msg['subject']} ---")
        print(f"From: {msg['from']}")
        print(f"Date: {msg['date']}")
        print(msg["body"])
        print()


if __name__ == "__main__":
    main()
