# Sending the alert

Read the profile's **Alert channel** field. Match the channel to how you send it.
None of these need a paid API — all have a free tier that's enough for one creator's alerts.

**Secrets live in `.env`, never in `creator/profile.md`.** The profile gets shared, pasted into chats and
committed to git. `.env` doesn't. Each channel's secret has one name:

```
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
DISCORD_WEBHOOK_URL=...
ALERT_EMAIL_TO=...
SMTP_HOST=...  SMTP_USER=...  SMTP_PASSWORD=...
```

If you find a token or webhook URL in the profile, move it to `.env`, replace it with "yes" in the profile,
check `.env` is listed in `.gitignore`, and tell the creator you did. Never print a secret back in chat.

`scripts/send_alert.py` exists and handles all three channels — run it instead of posting anything yourself:

```
python scripts/send_alert.py --channel telegram --text "..."
python scripts/send_alert.py --channel discord --text "..."
python scripts/send_alert.py --channel email --text "..."
```

Pass the top 🔴 High story from Step 3's report as `--text` (headline + one line + the link is plenty — see
"Keep it short" below). It reads the right `.env` variables for that channel itself and tells you plainly if
one is missing ("Missing from .env: ...") instead of sending a broken alert.

**Add `--dry-run` to test the message without sending anything** — useful the first time a creator sets up a
channel, or if you're not sure the destination is right yet. It prints exactly what would be sent (with the
token/webhook masked) and sends nothing.

## Telegram
- Needs `TELEGRAM_BOT_TOKEN` (from @BotFather) and `TELEGRAM_CHAT_ID` in `.env`.
- Messages over 4096 characters get truncated — keep the `--text` short, this is a ping not the full report.

## Discord
- Needs `DISCORD_WEBHOOK_URL` in `.env` (Server Settings → Integrations → Webhooks → copy URL).
  A webhook does not need a bot token or any OAuth — it's a single URL, the simplest option here.
- Messages over 2000 characters get truncated, same reason as Telegram.

## Email
- Needs `ALERT_EMAIL_TO` plus `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` (`SMTP_PORT` optional, defaults to 587)
  in `.env`. Most email providers (Gmail, Outlook, etc.) call this an "app password" — the creator's real
  login password usually won't work and they'll need to generate one from their provider's security settings.

## "Just tell me in chat"
- Nothing in `.env` needed, and don't run `send_alert.py` at all. No alert to send — the Step 3 report in
  chat already is the alert. This is the default and needs nothing set up, which is why
  `/creator-os:news-sniper` works with zero configuration.

## Keep it short
Whatever channel, `--text` should be the headline, one sentence of why it's urgent, and the link — not the
whole Step 3 report. A ping should take five seconds to read; the full report is already saved to
`content/research/breaking/`.

## If it fails
`send_alert.py` prints a one-line reason and exits non-zero — it never prints the raw token or webhook URL
back, even on error. Common cases:
- **"Missing from .env: ..."** — the creator hasn't added that secret yet. Tell them which name(s), point at
  `.env`, and remind them it never goes in `profile.md`.
- **A real send error** (e.g. "401 Unauthorized", "404 Not Found")** — the secret is present but wrong
  (expired token, wrong chat id, deleted webhook). Tell the creator to double-check the value in `.env`
  against the source (BotFather, Discord webhook settings) rather than guessing a fix.
