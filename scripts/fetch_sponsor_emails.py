"""Fetch brand/sponsorship emails from the creator's own inbox, read-only.

Connects over IMAP in **read-only mode** (`readonly=True` — the library itself refuses to
change anything on the server this way) and searches the last N days of a chosen folder for
messages matching keywords, then prints each match's sender, subject, date and plain-text body
so the creator can paste one into sponsor-desk's Step 1.

This script never sends anything, never deletes anything, and never modifies a flag or label
unless --mark-read is passed explicitly (off by default — see --mark-read below).

Works with Gmail, Outlook/Office365, Yahoo, or any other IMAP inbox.

Gmail — unchanged, exactly as before (never need to touch anything else in .env):

    GMAIL_ADDRESS=you@gmail.com
    GMAIL_APP_PASSWORD=...          # a 16-character Google "app password", not your real password

Outlook/Office365 or Yahoo — set EMAIL_PROVIDER plus the generic address/password pair:

    EMAIL_PROVIDER=outlook          # or "yahoo" (see PROVIDERS below for the full list)
    EMAIL_ADDRESS=you@outlook.com
    EMAIL_APP_PASSWORD=...          # an app password from that provider, same idea as Gmail's

A custom domain (e.g. Google Workspace or a provider not in PROVIDERS) — set the host yourself:

    EMAIL_PROVIDER=custom
    EMAIL_ADDRESS=you@yourdomain.com
    EMAIL_APP_PASSWORD=...
    IMAP_HOST=imap.yourdomain.com
    IMAP_PORT=993                   # optional, this is already the default

See skills/sponsor-desk/references/gmail-connection.md for where each provider's app password setting
lives. Secrets stay in .env, never in creator/profile.md or creator/rate-card.md.

Usage:
    python scripts/fetch_sponsor_emails.py
    python scripts/fetch_sponsor_emails.py --days 14 --limit 10
    python scripts/fetch_sponsor_emails.py --query "sponsor OR partnership OR collab"
    python scripts/fetch_sponsor_emails.py --dry-run
    python scripts/fetch_sponsor_emails.py --json

--dry-run connects, confirms the login works and the folder is reachable, then disconnects
without searching or printing any real email content — safe to run as a first connection test.

--json prints the same matches as a JSON array instead of the human-readable block, with a
stable "id" (1, 2, 3, ...) on each one. This is what Claude reads when it runs this script as
part of sponsor-desk Step 1 — the creator never touches a terminal, Claude shows the list in
chat and the creator just says "run #2", no copy-pasting an email by hand.
"""
import argparse
import email
import email.message
import imaplib
import json
import os
import sys
from datetime import datetime, timedelta
from email.header import decode_header
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_QUERY = "sponsor OR sponsorship OR partnership OR collab OR collaboration OR advertise OR ambassador"
MAX_BODY_CHARS = 3000

# Host/port for the providers creators ask about most. Add a row here (and in
# skills/sponsor-desk/references/gmail-connection.md) before telling someone to use --provider custom —
# IMAP_HOST is only a fallback for inboxes that genuinely aren't on this list.
PROVIDERS = {
    "gmail": ("imap.gmail.com", 993),
    "outlook": ("outlook.office365.com", 993),
    "yahoo": ("imap.mail.yahoo.com", 993),
}


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


def resolve_connection() -> tuple[str, str, str, int] | tuple[None, None, None, None]:
    """Work out (address, app_password, host, port) from .env, or (None, None, None, None) if unset.

    Gmail stays exactly as it was before this function existed: GMAIL_ADDRESS + GMAIL_APP_PASSWORD,
    always imap.gmail.com:993, no EMAIL_PROVIDER needed. That path is checked first and returns
    immediately, so nothing about an existing Gmail setup changes.

    Everyone else sets EMAIL_PROVIDER (outlook, yahoo, or custom) plus EMAIL_ADDRESS/EMAIL_APP_PASSWORD.
    "custom" (or any provider name not in PROVIDERS) requires IMAP_HOST too, since there's no sensible
    default host to guess at for an arbitrary domain. IMAP_PORT defaults to 993 (IMAP-over-SSL, what
    every provider in PROVIDERS uses) unless overridden.
    """
    if os.environ.get("GMAIL_ADDRESS", "").strip() and os.environ.get("GMAIL_APP_PASSWORD", "").strip():
        host, port = PROVIDERS["gmail"]
        return os.environ["GMAIL_ADDRESS"], os.environ["GMAIL_APP_PASSWORD"], host, port

    address = os.environ.get("EMAIL_ADDRESS", "").strip()
    app_password = os.environ.get("EMAIL_APP_PASSWORD", "").strip()
    if not address or not app_password:
        return None, None, None, None

    provider = os.environ.get("EMAIL_PROVIDER", "").strip().lower()
    if provider in PROVIDERS:
        host, port = PROVIDERS[provider]
    else:
        host = os.environ.get("IMAP_HOST", "").strip()
        if not host:
            return None, None, None, None
        port = int(os.environ.get("IMAP_PORT", "993"))
    return address, app_password, host, port


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


def _fail(message: str, as_json: bool) -> None:
    """Exit with a clear reason, in whichever shape the caller asked for.

    Claude running this with --json needs one consistent shape to check (a top-level "error" key)
    instead of sometimes getting JSON and sometimes getting a plain sentence depending on which
    failure path hit — that's what used to make a hand-run of this script feel necessary instead
    of something Claude could just call and react to on its own.
    """
    if as_json:
        print(json.dumps({"error": message}))
    else:
        print(message)
    sys.exit(1)


def fetch(days: int, limit: int, query: str, folder: str, mark_read: bool, dry_run: bool, as_json: bool = False) -> list[dict]:
    address, app_password, host, port = resolve_connection()
    if address is None:
        _fail(
            "Missing from .env: set GMAIL_ADDRESS + GMAIL_APP_PASSWORD for Gmail, or EMAIL_PROVIDER "
            "(outlook/yahoo/custom) + EMAIL_ADDRESS + EMAIL_APP_PASSWORD (+ IMAP_HOST for custom) for "
            "another inbox. Nothing fetched. See skills/sponsor-desk/references/gmail-connection.md.",
            as_json,
        )

    # readonly=True: the server rejects any attempt to change flags, move, or delete over this
    # connection. That's enforced by imaplib/the server, not just a promise in this script.
    imap = imaplib.IMAP4_SSL(host, port)
    try:
        imap.login(address, app_password)
    except imaplib.IMAP4.error as err:
        _fail(
            f"Login failed for {host}: {err}. Check the address and app password in .env — most failures "
            "here mean the app password was mistyped, revoked, or the wrong provider's host got used.",
            as_json,
        )

    status, _ = imap.select(folder, readonly=not mark_read)
    if status != "OK":
        imap.logout()
        _fail(f"Could not open folder '{folder}'. Check the name (folder/label names are case-sensitive).", as_json)

    if dry_run:
        imap.logout()
        if not as_json:
            print(f"[dry run] Logged in as {address}, opened '{folder}' read-only. Connection works. Nothing searched.")
        return []

    since = datetime.now() - timedelta(days=days)
    search_str = _imap_query(query, since)
    status, data = imap.search(None, search_str)
    if status != "OK":
        imap.logout()
        _fail("IMAP search failed — try a simpler --query.", as_json)

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
    parser.add_argument(
        "--json",
        action="store_true",
        help="print matches as a JSON array with a stable numeric id instead of the human-readable "
        "block — this is how Claude reads the results to show a numbered pick-list in chat",
    )
    args = parser.parse_args()

    load_env()
    results = fetch(args.days, args.limit, args.query, args.folder, args.mark_read, args.dry_run, args.json)

    if args.dry_run:
        if args.json:
            print(json.dumps({"dry_run": True, "connected": True}))
        return

    if args.json:
        numbered = [{"id": i, **msg} for i, msg in enumerate(results, 1)]
        print(json.dumps(numbered, indent=2))
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
