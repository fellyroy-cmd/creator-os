---
name: shorts-script
description: Write scroll-stopping short-form video scripts (Reels, TikTok, YouTube Shorts, 25–45 seconds) from any source — an idea, a link, a long video, a news story or a build update — using a 7-beat structure (hook, proof, head fake, rehook, list, payoff, CTA) in the creator's voice. Writes 2–3 hook variants and recommends one, plus a recording sheet. Triggers on "write a short", "reel script", "tiktok script", "script a short about", "/creator-os:shorts-script".
---

# Shorts script: 7 beats, 25–45 seconds

## Step 0: Load the creator
Read `creator/profile.md`. If it doesn't exist, tell the creator to run `/creator-os:setup` first and stop.
Then read [references/script-formula.md](references/script-formula.md). It's the whole method.

## Step 1: Understand the source
- A link → open it. A file → read it. An idea → use what they gave you plus a quick search if it needs facts.
- Write down, with sources: the **most surprising number**, the **common belief it breaks**, **3 concrete
  things** (steps, tools, results), and the **one transformation** the viewer gets.
- No number available? Use a concrete detail instead (a time, a price, a before/after). Never invent one.

## Step 2: Avoid repeats
Read the last 5 scripts in `content/shorts/` (if any). Don't reuse their hook pattern, rehook line or CTA type.

## Step 3: Write 3 variants
Same source, different **hook angle** (see the formula): number, contrarian, result. Each variant is the full
7 beats. Mark each beat in brackets so the creator sees the structure:

```
### Variant A: number hook
[HOOK] ...
[PROOF] ...
[HEAD FAKE] ...
[REHOOK] ...
[LIST] ...
[PAYOFF] ...
[CTA] ...
(~[word count] words, ~[seconds]s)
```

Then: **Recommended: A/B/C**, with one line on why it fits this source and this audience.

## Step 4: Recording sheet
Below the variants, add the recommended script as a clean **read-aloud version**: no brackets, one sentence per
line, plus one line of delivery direction (energy, where to pause, what to gesture). That's what goes on the
phone while recording.

## Step 5: Save
Save to `content/shorts/[YYYY-MM-DD]-[slug]/script.md`. Reply with the recommended hook line, the length and the path.
