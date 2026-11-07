# Connecting your inbox (optional)

Sponsor desk works with zero setup: paste a brand email into chat and it's triaged. This page is for a
creator who's tired of copy-pasting and wants Claude to pull sponsor-looking emails out of their own inbox
for them to pick from instead.

**This connection can only read.** It uses IMAP in Python's built-in read-only mode — the mode itself refuses
any attempt to change a flag, move a message, or delete anything, enforced by the mail server, not just a
promise in this script. `scripts/fetch_sponsor_emails.py` never sends, never auto-replies, and never files
anything into sponsor-desk without the creator picking it first. If a future version adds Gmail labels (so a
triaged email gets tagged "Sponsor — replied" for example), that's a deliberate, separate decision — not
something this script does today.

## Get a Gmail app password (not your real password)

Google blocks plain-password IMAP logins by default — you need a 16-character **app password** instead,
which only works for this one connection and can be revoked any time without touching your real login.

1. Turn on 2-Step Verification if it isn't already: [myaccount.google.com/security](https://myaccount.google.com/security)
2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Name it something you'll recognise later, e.g. "Creator OS sponsor desk"
4. Copy the 16-character password it shows you (spaces don't matter, you can paste it with or without them)

**Secrets live in `.env`, never in `creator/profile.md` or `creator/rate-card.md`.** Those files get shared,
pasted into chats and committed to git. `.env` doesn't (it's in `.gitignore` from this repo's first commit).
Add two lines to `.env` in your project folder:

```
GMAIL_ADDRESS=you@gmail.com
GMAIL_APP_PASSWORD=your16characterapppassword
```

If you ever want to cut this connection off, delete the app password from
[myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) — the `.env` lines stop
working immediately, nothing else to undo.

## Test the connection before trusting it

```
python scripts/fetch_sponsor_emails.py --dry-run
```

This logs in, opens the inbox read-only, confirms both work, and disconnects — it does not search or print
any real email content. If it prints "Missing from .env: ..." you haven't added the two lines above yet. If
it prints a login failure, the app password was probably mistyped, or revoked — generate a new one rather
than guessing at the old one.

## Fetch real matches

```
python scripts/fetch_sponsor_emails.py
python scripts/fetch_sponsor_emails.py --days 14 --limit 10
python scripts/fetch_sponsor_emails.py --query "sponsor OR partnership OR collab"
```

Defaults to the last 7 days of `INBOX`, matching sponsor-ish keywords (sponsor, sponsorship, partnership,
collab, collaboration, advertise, ambassador) in the subject or body, newest first, capped at 15 results.
Every match prints sender, subject, date and the plain-text body so the creator can read through them and
say which one to run through sponsor-desk's Step 1 — this script never decides that for them.

**Only Gmail today.** The script talks IMAP, which most providers support, but it's only been written and
tested against `imap.gmail.com`. A different provider (Outlook, Yahoo, a custom domain) would need its own
IMAP host — that's a reasonable follow-up contribution, not something to guess at here.

## If nothing comes back

- **"Missing from .env: ..."** — add the two lines above, then retry.
- **"Gmail login failed"** — the app password in `.env` is wrong or was revoked; generate a new one.
- **"Could not open folder '...'"** — Gmail labels are case-sensitive; `INBOX` always exists, a custom label
  might not be spelled the way you typed it.
- **"No emails matched"** — the keywords didn't hit anything in the window. Widen it:
  `--days 30` or a broader `--query`.
