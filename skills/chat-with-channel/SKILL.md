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
Run `python scripts/search_transcripts.py "<the creator's question>" --json` and read the result — it
scores every indexed passage by how many of the question's meaningful words it contains (ignoring words
like "the", "what", "my") and returns the top matches, best first. This replaces reading the raw index
yourself: the ranking is a real, testable function instead of an eyeballed guess, and it's the seam where a
future embeddings upgrade slots in without changing this step.

If the question uses different words than the transcript likely does (e.g. "what did you stop using" when
the creator probably said "I switched tools"), also try the obvious synonym as a second search — keyword
matching only finds what's actually written.

Keep the top 3–6 results the script returns. If it reports no matches at all, say so plainly in Step 2
rather than stretching a loosely-related passage into an answer.

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
Run `python scripts/ingest_transcripts.py` again any time a new transcript is added. Step 0 already checks
staleness automatically before every question, so you'll never get a silently-stale answer — but if you'd
rather the index rebuild itself on a timer instead of waiting for you to notice, see
[references/scheduling.md](references/scheduling.md) for a Task Scheduler / cron setup. See
[references/ingest-setup.md](references/ingest-setup.md) for the full setup, including where this is headed
next (semantic search instead of keyword match).
