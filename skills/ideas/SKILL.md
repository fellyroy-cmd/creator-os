---
name: ideas
description: Brainstorm 10 content ideas for the creator's niche, grounded in what's happening right now and in what the creator has already made, each with a hook, angle and pillar, then rank the top 3. Triggers on "give me content ideas", "what should I post", "video ideas", "/creator-os:ideas".
---

# Ideas: 10 ideas, top 3 ranked

## Step 0: Load the creator
Read `creator/profile.md`. If it doesn't exist, tell the creator to run `/creator-os:setup` first and stop.

## Step 1: Gather fuel (quick, don't over-research)
1. The newest file in `content/research/` (a `/creator-os:news` digest), if one is from the last 7 days.
2. Otherwise WebSearch: "[niche] news this week" and "[niche] trending [current month year]".
3. Skim `content/ideas/` and `content/scripts/` so you don't repeat an idea they already have.
4. If the creator gave a theme ("ideas about pricing"), stay inside it.

## Step 2: Write 10 ideas
Spread them across the profile's pillars. For each:

```
### [N]. [Working title]
**Pillar:** [from the profile]
**Hook:** [the first line they'd say on camera]
**Angle:** [the creator's take, not just "report what happened"]
**Why now:** [timely: what's happening / evergreen: why it keeps getting searched]
**Repurposes into:** [which platforms it suits best]
```

Good ideas are specific. "AI tools for editing" is a topic, not an idea. "I edited a 20-minute video with
only free AI tools. Here's where they broke" is an idea.

## Step 3: Rank the top 3
- **Make this week:** the most timely one
- **Most searchable:** the one people are actively looking for
- **Most comments:** the one the audience will argue about

One line each on why.

## Step 4: Save
Save to `content/ideas/[YYYY-MM-DD]-ideas.md` and tell the creator the path.
Offer the next step: "Want a script for #N? Run `/creator-os:shorts-script` or ask me to outline the long version."
