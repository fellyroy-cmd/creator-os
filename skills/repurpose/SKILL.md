---
name: repurpose
description: Turn one piece of long content (a YouTube script, transcript, video link, podcast notes or blog post) into ready-to-post versions for every platform in the creator's profile — X thread, LinkedIn post, Instagram carousel + Reel script, TikTok script and a newsletter section — in the creator's own voice. Triggers on "repurpose this", "turn this video into posts", "make posts from my script", "/creator-os:repurpose".
---

# Repurpose: one video → every platform

## Step 0: Load the creator
Read `creator/profile.md`. If it doesn't exist, stop and say:
"Run `/creator-os:setup` first. It takes 2 minutes and makes every post sound like you."

Pull from it: voice (how I sound / never say / example line), audience, platforms, pillars, CTA + link, hashtags.

## Step 1: Get the source
- Pasted text or a file path → read it.
- A video link with no transcript → ask the creator to paste the transcript or key points (one question).
- Nothing given → ask: "Paste the script or transcript, or give me the topic and 3–5 key points."

Before writing, pull out of the source:
- **The core idea** in one sentence
- **3–7 key points**, with every number, name and example exactly as the source states them
- **The best hook line**: the most surprising claim, number or result in the source
- **The title** (for the folder name)

## Step 2: Write only the platforms in the profile
Write a section for each platform the creator listed. Skip the rest. Formats:

### X / Twitter thread (6–10 posts)
- Post 1: the hook. Stands alone, makes sense without the thread.
- One point per post, conversational. Numbers as digits.
- Second-last post: the personal take.
- Last post: the CTA from the profile + link.

### LinkedIn post
- First line is the insight itself, no warm-up ("I've been thinking about…" is banned).
- 4–6 short paragraphs, one blank line between.
- End with a real question the audience can answer from their own experience.
- 3–5 hashtags max.

### Instagram carousel (7–10 slides) + caption
- Slide 1: hook headline, ≤ 10 words.
- One point per slide, ≤ 25 words each.
- Second-last slide: the takeaway. Last slide: CTA.
- Caption: hook line, 2–4 sentences, CTA, hashtags from the profile.

### Short-form script (Reels / TikTok / Shorts, 30–45s)
- 0–3s hook, then 3 fast points, then the payoff, then the CTA.
- Written to be spoken: contractions, short sentences.
- For a scroll-stopping script built beat by beat, point the creator to `/creator-os:shorts-script`.

### Newsletter section
- 3 subject line options (≤ 50 characters).
- 2–3 sentence intro that connects to the reader.
- The key points as bullets, then a link to the full video + the CTA.

## Rules for every platform
- **Sound like the profile**, not like a marketer. Use their "I always" habits; never use their "I never say" words.
- Also never use: "game-changer", "unlock", "dive in", "in today's fast-paced world", "let's explore".
- **Honesty:** only claims, numbers and quotes that are in the source. Don't round up, don't invent stats.
- Each platform gets its own angle on the same idea. Don't paste the same sentences five times.
- CTA from the profile on every platform, worded for that platform.

## Step 3: Save
Save to `content/repurposed/[YYYY-MM-DD]-[title-slug]/`, one file per platform
(`x-thread.md`, `linkedin.md`, `instagram.md`, `short-script.md`, `newsletter.md`).
Reply with the folder path and the one piece you'd post first, with one line on why.
