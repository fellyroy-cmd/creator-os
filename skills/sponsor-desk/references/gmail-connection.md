# Connecting your inbox (optional)

Sponsor desk works with zero setup: paste a brand email into chat and it's triaged. This page is for a
creator who's tired of copy-pasting and wants Claude to pull sponsor-looking emails out of their own inbox
for them to pick from instead. Gmail, Outlook/Office365, Yahoo and custom domains (e.g. Google Workspace)
are all supported — pick your section below.

**This connection can only read.** It uses IMAP in Python's built-in read-only mode — the mode itself refuses
any attempt to change a flag, move a message, or delete anything, enforced by the mail server, not just a
promise in this script. `scripts/fetch_sponsor_emails.py` never sends, never auto-replies, and never files
anything into sponsor-desk without the creator picking it first. If a future version adds Gmail labels (so a
triaged email gets tagged "Sponsor — replied" for example), that's a deliberate, separate decision — not
something this script does today.

**All providers below use the same idea:** an app password, not your real login password, that only works
for this one connection and can be revoked any time without touching your main account. **Secrets live in
`.env`, never in `creator/profile.md` or `creator/rate-card.md`** — those files get shared, pasted into
chats and committed to git, `.env` doesn't (it's in `.gitignore` from this repo's first commit).

## Gmail

Google blocks plain-password IMAP logins by default — you need a 16-character app password instead.

1. Turn on 2-Step Verification if it isn't already: [myaccount.google.com/security](https://myaccount.google.com/security)
2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Name it something you'll recognise later, e.g. "Creator OS sponsor desk"
4. Copy the 16-character password it shows you (spaces don't matter, you can paste it with or without them)

Add two lines to `.env` in your project folder:

```
GMAIL_ADDRESS=you@gmail.com
GMAIL_APP_PASSWORD=your16characterapppassword
```

If you ever want to cut this connection off, delete the app password from
[myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) — the `.env` lines stop
working immediately, nothing else to undo.

## Outlook / Office365

1. Turn on 2-factor authentication if it isn't already: [account.microsoft.com/security](https://account.microsoft.com/security)
2. Under Security → Advanced security options, create an **app password**
3. Copy the password it shows you

Add three lines to `.env`:

```
EMAIL_PROVIDER=outlook
EMAIL_ADDRESS=you@outlook.com
EMAIL_APP_PASSWORD=yourapppassword
```

## Yahoo

1. Go to [login.yahoo.com/account/security](https://login.yahoo.com/account/security)
2. Generate an **app password** under "Generate and manage app passwords"
3. Copy the password it shows you

Add three lines to `.env`:

```
EMAIL_PROVIDER=yahoo
EMAIL_ADDRESS=you@yahoo.com
EMAIL_APP_PASSWORD=yourapppassword
```

## A custom domain (e.g. Google Workspace, a business email host)

Only needed if your inbox isn't Gmail, Outlook or Yahoo directly — ask your email provider (or IT person)
for their IMAP server address if you don't already know it.

```
EMAIL_PROVIDER=custom
EMAIL_ADDRESS=you@yourdomain.com
EMAIL_APP_PASSWORD=yourapppassword
IMAP_HOST=imap.yourdomain.com
IMAP_PORT=993
```

`IMAP_PORT` is optional — 993 (IMAP-over-SSL) is already the default and is correct for almost every
provider.

## Test the connection before trusting it

```
python scripts/fetch_sponsor_emails.py --dry-run
```

This logs in, opens the inbox read-only, confirms both work, and disconnects — it does not search or print
any real email content. If it prints "Missing from .env: ..." you haven't added your provider's lines from
the section above yet. If it prints a login failure, the app password was probably mistyped, or revoked —
generate a new one rather than guessing at the old one.

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

## How Claude actually calls this (you shouldn't need to run it by hand)

Inside sponsor-desk's Step 1, Claude runs `python scripts/fetch_sponsor_emails.py --json` itself and turns
the result into a numbered list right there in chat — you just say which number to triage. The plain-text
commands above are for running it yourself in a terminal if you ever want to, but day to day there's no
script to open: ask sponsor-desk to check your inbox and it does this step for you.

`--json` prints the same matches as a JSON array instead of the readable block, each one tagged with a
stable `id` (1, 2, 3, ...) so "triage #2" means the same email every time, and a clean `{"error": "..."}`
shape on any failure (missing `.env`, bad app password, closed folder) so Claude can tell you plainly what
went wrong instead of guessing from a sentence.

**Gmail, Outlook/Office365, Yahoo, and custom IMAP domains are all supported** — see the section above for
yours. A provider not in that list still works via the custom-domain path as long as you know its IMAP
server address.

## If nothing comes back

- **"Missing from .env: ..."** — add the lines for your provider from the section above, then retry.
- **"Login failed for ..."** — the app password in `.env` is wrong, was revoked, or `EMAIL_PROVIDER` doesn't
  match the account you're logging into; generate a new app password or double check the provider name.
- **"Could not open folder '...'"** — folder/label names are case-sensitive; `INBOX` always exists, a custom
  folder might not be spelled the way you typed it.
- **"No emails matched"** — the keywords didn't hit anything in the window. Widen it:
  `--days 30` or a broader `--query`.
