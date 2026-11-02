---
name: news
description: Write a news digest for the creator's niche — the week's top stories with sources, new tools or launches, and the content angles each story opens up. Uses the creator's trusted sources from their profile plus web search. Triggers on "what's new in my niche", "news digest", "what happened this week", "/creator-os:news".
---

# News: what happened in your niche this week

## Step 0: Load the creator
Read `creator/profile.md`. If it doesn't exist, tell the creator to run `/creator-os:setup` first and stop.
Note the niche, audience and the "News sources" list.

## Step 1: Search
Run these searches (in parallel if you can), using the current date:
- "[niche] news [this week / current month year]"
- "[niche] new tools launched [current month year]"
- One search per trusted source in the profile (e.g. `site:theverge.com [niche]`), max 3.

Then open the 5–8 most promising results to confirm the details. **Every story needs a working source link
and a date.** Drop anything older than 7 days unless the creator asked for a longer window.

## Step 2: Write the digest

```
# [Niche] news — week of [date]

## Top stories
1. **[Headline in plain words]** — what happened, in 1–2 sentences. Why it matters to [audience]. [Source](url), [date]
...(5 stories)

## New tools / launches
- **[Name]** — what it does, who it's for, price if known. [Source](url)

## Content angles
- **Long video:** [title idea] — from story #N
- **Short:** [hook line] — from story #N
- **Hot take:** [the opinion only this creator would have]
- **Newsletter lead:** story #N, because [reason]
```

Rules:
- Plain language. Explain jargon the audience wouldn't know.
- Rumours and leaks are labelled as such. If two sources disagree, say so.
- No story without a source. No invented numbers.

## Step 3: Save
Save to `content/research/[YYYY-MM-DD]-news.md`. Reply with the top 3 headlines and the path.
`/creator-os:ideas` and `/creator-os:plan-week` read this file automatically.
