---
name: plan-week
description: Build the creator's content calendar for the coming week — the main video (titles, hook, outline), what goes out on each platform each day, and the CTA — based on their posting rhythm, this week's news and their saved ideas. Triggers on "plan my week", "content calendar", "what am I posting this week", "/creator-os:plan-week".
---

# Plan the week

## Step 0: Load the creator
Read `creator/profile.md`. If it doesn't exist, tell the creator to run `/creator-os:setup` first and stop.
Use the **Rhythm** section (how many videos and shorts, which days) as the frame for the week.

## Step 1: Gather
- The newest `content/research/*-news.md` from the last 7 days, if any.
- The newest file in `content/ideas/`, if any.
- Last week's plan in `content/calendar/`, so nothing unfinished gets lost.

## Step 2: Pick the main piece (one question max)
If the creator hasn't named this week's main video, suggest the strongest idea from the news or ideas files
in one line and ask: "Go with this, or do you have a topic?" If they said "you pick", just pick.

## Step 3: Write the plan

```
# Content plan — week of [Monday's date]

## Main video: [working title]
**Title options:** 1. [curiosity] 2. [how-to / search] 3. [opinion]
**Search terms people type:** [2–3]
**Hook (first 30s):** [what it promises and why they should stay]
**Outline:** hook → [section 1] → [section 2] → [section 3] → CTA
**Publish:** [day from the rhythm]

## Day by day
| Day | Platform | What | Source |
|---|---|---|---|
| Mon | ... | ... | main video / news #N / idea #N |
...

## Shorts this week
1. [hook line] — [pillar] — [day]
...(as many as the rhythm says)

## Community / CTA
[one post or prompt that drives people to the main CTA in the profile]

## Parked for next week
- ...
```

Rules:
- Match the rhythm exactly. Don't plan 7 shorts for someone who posts 3.
- Every short-form slot gets a specific hook line, not "a short about the video".
- Spread the pillars from the profile across the week. No pillar twice in a row.
- After the main video publishes, plan the repurposed posts (`/creator-os:repurpose`) for the following days.

## Step 4: Save
Save to `content/calendar/week-[YYYY-MM-DD].md` (Monday's date). Reply with the main video title,
the publish day, and what to do first today.
