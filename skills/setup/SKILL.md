---
name: setup
description: Set up Creator OS for a creator. Asks a few quick questions about their niche, audience, voice, platforms and call-to-action, then writes creator/profile.md and the content folders every other Creator OS skill uses. Run this first, or again whenever the creator's brand changes. Triggers on "set up creator os", "create my creator profile", "/creator-os:setup".
---

# Creator OS setup

Every Creator OS skill reads one file: `creator/profile.md` in the current folder. This skill writes it.

## Step 1: Check what exists
- If `creator/profile.md` already exists, read it, show a 5-line summary and ask: "Update it or start fresh?"
- If the creator pasted a bio, a channel link, a past script or a brand doc, read it first and pre-fill
  every answer you can. Only ask what you still don't know.

## Step 2: Interview (one message, all questions, numbered)
Ask these in a single message so the creator answers in one go. Offer an example answer for each.

1. **Name / handle** you post as
2. **Niche** in one line (e.g. "budget travel in South-East Asia", "AI tools for small businesses")
3. **Audience**: who watches, and what they want from you
4. **Main platform** (where long content lives) and **other platforms** you post to
5. **Voice**: 3 words that describe how you talk, plus words or phrases you never use
6. **Content pillars**: 3–5 recurring types of post (e.g. News, How-to, Opinion, Behind the scenes)
7. **Main call-to-action**: where you send people (newsletter, community, product, follow) + the link
8. **Posting rhythm**: how many long videos and shorts per week, and which days
9. **News sources** you trust for your niche (sites, newsletters, subreddits), optional

If the creator says "just make something up" or skips questions, fill sensible defaults for their niche and
mark them `(default, edit me)`.

## Step 3: Write the profile
Copy [profile-template.md](profile-template.md) to `creator/profile.md` and fill every field from the answers.
Keep their exact wording for the voice section. Don't polish it into marketing language.

## Step 4: Create the folders
Create these if they don't exist (empty `.gitkeep` in each is fine):
```
content/ideas/   content/research/   content/scripts/   content/shorts/
content/repurposed/   content/calendar/
```

## Step 5: Hand over
Reply with:
- one line confirming the profile is saved
- the 5 commands they can run next, one line each:
  `/creator-os:ideas` · `/creator-os:news` · `/creator-os:plan-week` · `/creator-os:repurpose` · `/creator-os:shorts-script`
- "Edit `creator/profile.md` any time. Every skill re-reads it on each run."
