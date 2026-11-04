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

## Telegram
- Needs `TELEGRAM_BOT_TOKEN` (from @BotFather) and `TELEGRAM_CHAT_ID` in `.env`.
- If `scripts/send_alert.py` exists in this project, run it:
  `python scripts/send_alert.py --channel telegram --text "..."` (it reads both from `.env`).
- No script yet? Tell the creator the message is ready and give them the raw Telegram Bot API call as a
  fallback (a POST to `https://api.telegram.org/bot<TOKEN>/sendMessage` with `chat_id` and `text`), and
  suggest they ask you to build `scripts/send_alert.py` once — then every future alert just works.

## Discord
- Needs `DISCORD_WEBHOOK_URL` in `.env` (Server Settings → Integrations → Webhooks → copy URL).
  A webhook does not need a bot token or any OAuth — it's a single URL, the simplest option here.
- Same pattern: use `scripts/send_alert.py --channel discord` if it exists, otherwise describe the
  POST (JSON body `{"content": "..."}` to the webhook URL) and offer to build the script.

## Email
- Needs `ALERT_EMAIL_TO` plus SMTP settings in `.env`. This one almost always needs a script — don't try to "send" an email yourself in chat.
  Offer to build `scripts/send_alert.py --channel email` once, using whatever email account they want to
  send from.

## "Just tell me in chat"
- Nothing in `.env` needed. No alert to send — the Step 3 report in chat already is the alert. This is the default and needs nothing
  set up, which is why `/creator-os:news-sniper` works with zero configuration.

## Building `scripts/send_alert.py`
If the creator wants real pings and no script exists yet, offer to write one: a small Python file that reads
`TELEGRAM_BOT_TOKEN` / `DISCORD_WEBHOOK_URL` / email credentials from `.env` (never hardcoded, never read from
`profile.md`) and sends one message. Keep it to one file, one function per channel, no extra dependencies
beyond `requests`. Remind the creator to add the real token to `.env` themselves — you never generate or
guess a token.
