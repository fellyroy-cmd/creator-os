---
name: chat-with-channel
description: Answer a question using everything the creator has ever said on camera — "did I ever cover X?", "what's my take on Y?", "find the clip where I explained Z" — by searching their own indexed video transcripts instead of guessing. Triggers on "chat with my channel", "search my videos", "what have I said about", "/creator-os:chat-with-channel".
---

# Chat with your channel: search what you've actually said, not what you might have said

This answers questions from the creator's **own transcripts only.** If the index doesn't cover something, it
says so — it never fills the gap with a generic AI answer dressed up as something the creator said on camera.

## Step 0: Load the creator and the index
Read `creator/profile.md`. If it doesn't exist, tell the creator to run `/creator-os:setup` first and stop.

Then check `content/transcripts/index.jsonl`. If it doesn't exist:
"You haven't indexed any transcripts yet. Drop a transcript file (.txt, .md, .vtt or .srt) for each video into
`content/transcripts/`, then run `python scripts/ingest_transcripts.py`. See
[references/ingest-setup.md](references/ingest-setup.md) for where to get transcripts from YouTube. Come back
here once that's done." Stop — don't answer from general knowledge instead.

If it exists, run `python scripts/ingest_transcripts.py --check` to see if it's current — this only compares
file timestamps, it doesn't re-read or re-chunk anything, so it's quick. If it reports stale (a transcript
was added, edited or removed since the last ingest), mention that once: "Heads up, [whatever the check output
said] — run `python scripts/ingest_transcripts.py` again to include the latest." Then continue with what's
indexed so far; don't block the question on it.

## Step 1: Find the passages that actually answer the question
Read `content/transcripts/index.jsonl` (one JSON object per line: `id`, `source`, `chunk`, `timestamp`,
`text`). Search it the same way you'd search any document: look for passages whose `text` contains the
question's key terms, synonyms included (a question about "pricing" should also match "cost", "charge",
"how much" in the transcript). Rank by how directly a passage addresses the question, not just keyword count.

Keep the top 3–6 passages. If nothing matches at all, say so plainly in Step 2 rather than stretching a
loosely-related passage into an answer.

## Step 2: Answer from the passages, cited
Write the answer using only what the passages say. Shape:

```
**[Direct answer in 1-3 sentences, in the creator's own words where possible]**

Said in:
- *"[short quote or paraphrase]"* — [source video name]#[chunk] [timestamp if available]
- *"[short quote or paraphrase]"* — [source video name]#[chunk] [timestamp if available]
```

If the passages disagree with each other (the creator's take changed over time), say so and note which is
more recent if the filenames suggest a date.

If nothing in the index covers the question: "You haven't said anything about that in an indexed video yet
— might be a good topic for a new one." Don't answer anyway from general AI knowledge; that defeats the point
of a tool that's supposed to only know what the creator actually said.

## Step 3: Offer the obvious follow-up
If the question sounds like it's for content ("what's my take on X") rather than just curiosity, offer: "Want
me to turn this into a short or a post?" and hand off to `/creator-os:repurpose` or `/creator-os:shorts-script`
with this answer as the source material.

## Keeping the index current
Run `python scripts/ingest_transcripts.py` again any time a new transcript is added — it's not automatic yet
(no watcher, no schedule), but `python scripts/ingest_transcripts.py --check` gives a real, fast answer to
"is it stale right now?" without rebuilding, which is what Step 0 uses. See
[references/ingest-setup.md](references/ingest-setup.md) for the full setup, including where this is headed
next (semantic search instead of keyword match).
