# Setting up chat with your channel

This feature is in its first, simplest version: it searches your transcripts for matching words. No paid
API, no account, nothing leaves your computer. A smarter version (meaning-based search, so it finds the right
clip even when the wording's different) is planned — see "What's next" below — but the file format won't
change, so transcripts you index now still work once that ships.

## 1. Get a transcript for each video

**From YouTube (free, no extra tools):**
1. Open your video → **Show transcript** (below the video, next to the description) → the transcript panel
   opens on the right.
2. Click the three-dot menu in that panel → **Download transcript** if your channel has it, otherwise copy
   the text out of the panel and paste it into a plain `.txt` file.
3. If your video doesn't have auto-captions yet, YouTube Studio → **Subtitles** → wait for auto-generated
   captions to finish processing, then come back to step 1.

**From YouTube Studio's caption export (keeps timestamps):**
YouTube Studio → your video → **Subtitles** → the English (auto) track → **⋮** → **Download** → `.vtt`. This
format keeps rough timestamps, so answers can point back to roughly where in the video something was said.

**From your own recording, with Whisper (if you'd rather transcribe locally):**
If you already use Whisper for editing (Creator OS's clip maker will, once it ships), its `.srt` or `.vtt`
output works here unchanged — drop it straight into `content/transcripts/`.

## 2. Name the file after the video

```
content/transcripts/2026-09-12-how-i-use-claude-code.txt
content/transcripts/2026-10-01-ai-news-roundup.vtt
```

The filename (without the extension) is what shows up as the source in an answer, so name it something
you'd recognise, ideally with the date first so files sort chronologically.

## 3. Build the index

```
python scripts/ingest_transcripts.py
```

This reads every `.txt`/`.vtt`/`.srt` file in `content/transcripts/`, splits each one into ~220-word passages
(about 90 seconds of talking) with a little overlap between them, and writes `content/transcripts/index.jsonl`
— one line per passage. Re-run it any time you add or change a transcript; it rewrites the whole file, it
doesn't append.

Want to check what it would do first, without writing anything? `python scripts/ingest_transcripts.py --dry-run`

## 4. Ask something

Run `/creator-os:chat-with-channel` and ask a real question — "what's my take on AI replacing editors?",
"did I ever do a video on pricing a first sponsorship?" It answers from the indexed passages only, with the
source video and (if the file had timestamps) roughly where to find it.

## Privacy

`content/transcripts/` and its `index.jsonl` stay out of the repo (`content/` is already in `.gitignore` from
this repo's first commit) — your own video transcripts are yours, never committed, never sent anywhere. The
search in Step 1 of the skill runs by reading the file directly; nothing is uploaded to index it.

## What's next

Keyword matching works well once you have a few dozen videos indexed, but it can miss a passage that answers
a question using different words than the question itself (e.g. the transcript says "I switched tools" and
the question asks "what did you stop using"). A future version can swap the matching step for an embeddings
search (turning each passage into a vector and comparing meaning, not just words) without changing
`index.jsonl`'s format — that's a deliberate seam left in this version so it's a drop-in upgrade, not a
rewrite.
