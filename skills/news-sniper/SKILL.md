---
name: news-sniper
description: Check right now for breaking news in the creator's niche that's worth a same-day post — a launch, a big announcement, a story suddenly everywhere — and score it so the creator knows what's actually urgent versus just new. Triggers on "check for breaking news", "anything blowing up right now", "news sniper", "/creator-os:news-sniper".
---

# News sniper: catch it while it's still breaking

This is different from `/creator-os:news`. That skill writes a calm weekly digest. This one answers one
question fast: **"is anything happening right now that I should drop everything and post about today?"**

## Step 0: Load the creator
Read `creator/profile.md`. If it doesn't exist, tell the creator to run `/creator-os:setup` first and stop.
Use the **Niche**, the **News sources** list, and the **Breaking news watch** keywords (if set) as your search
targets. No keywords saved? Use the niche itself plus the content pillars — ask the creator for 3–5 keywords
if the result feels too broad.

## Step 1: Search for what's moving right now
Run these (in parallel if you can), using the current date and no date older than 48 hours:
- "[niche] news today"
- One search per "watch for" keyword from the profile, e.g. `"[keyword]" news [today's date]`
- One search per trusted source from the profile with a recency term, e.g. `site:[source] [niche] [this week]`

Open the top 5–10 results. For each candidate story, note: headline, source, a working link, how many hours
old it is, and whether multiple unrelated sources are covering it (that's the signal it's actually big, not
just one outlet's angle).

## Step 2: Score it
Rate each candidate low / medium / high using [references/scoring.md](references/scoring.md). Only high and
medium stories make the report — don't pad it with routine news, that's what `/creator-os:news` is for.

## Step 3: Report
```
# Breaking check — [date] [time]

## 🔴 High — post today if you can
- **[Headline]** — [1 sentence: what happened]. [why it's high, e.g. "3 hours old, every outlet in the niche
  already has it"]. [Source](url)
  **Angle:** [the take only this creator would have] · **Format:** [short / hot take / community post]

## 🟡 Medium — worth a short this week, not urgent
- **[Headline]** — [1 sentence]. [Source](url)

## Nothing found
If there's genuinely nothing above low, say so in one line: "Nothing breaking right now — niche is quiet."
Don't invent urgency.
```

## Step 4: Alert (only if the creator asked to be pinged, not just checking in chat)
If there's at least one 🔴 High story **and** the profile's "Alert channel" is set to something other than
"just tell me in chat": follow [references/alert-channel.md](references/alert-channel.md) for how to send it.
If the secret for that channel isn't in `.env` yet, tell the creator once: "Your alert channel is set to [channel]
but there's no [TELEGRAM_BOT_TOKEN / DISCORD_WEBHOOK_URL] in `.env` yet. Add it there (not in your profile), and
I'll just report here in chat for now."

## Step 5: Save
Append the report to `content/research/breaking/[YYYY-MM-DD].md` (create the file with a one-line header if
it doesn't exist yet — same file for every check that day, newest at the bottom). Reply with the top story
(if any) and the path.

## Running this automatically
This skill works great run by hand whenever the creator wants a check. To run it on a schedule (every 30
minutes, say) without opening Claude Code yourself each time, see
[references/scheduling.md](references/scheduling.md) — it's optional and needs no paid API.
