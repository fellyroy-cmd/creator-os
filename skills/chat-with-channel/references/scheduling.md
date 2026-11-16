# Keeping the index fresh automatically

Two ways to make sure `content/transcripts/index.jsonl` never falls far behind your transcripts, from
least to most setup:

## You don't need to do anything (recommended for most creators)

`/creator-os:chat-with-channel` already runs `python scripts/ingest_transcripts.py --check` as the first
thing it does, every single time you ask it a question. If the index is stale it tells you once, then
answers anyway from what's indexed so far. For most creators — who add a transcript every time they post
a new video, then ask a question some time later — this is already "automatic": you'll never get a
silently-stale answer, because the check happens right before every answer.

The one gap this doesn't cover: if you want the index to be rebuilt *before* you ask, not just flagged
as stale when you ask, you need one of the options below.

## Option A: run it yourself, whenever you add a transcript

No scheduler needed. Right after dropping a new transcript file into `content/transcripts/`:

```
python scripts/ingest_transcripts.py
```

This is the simplest option and matches how most creators actually work — a transcript shows up once per
video, not continuously, so there's rarely a real need to check more often than "right after I publish."

## Option B: a real scheduled job (for creators who manage transcripts outside Claude Code)

If transcripts land in `content/transcripts/` from some other automation — an editor's workflow, a
Whisper batch job, a shared drive sync — and you want the index to always be ready without remembering to
run anything, point your OS's own scheduler at the script directly. Unlike `news-sniper`'s scheduling
(which needs Claude Code running to make a judgment call), `ingest_transcripts.py` is a plain Python
script — no Claude Code, no API key, no internet needed to run it on a timer.

**Windows: Task Scheduler**
1. Open Task Scheduler → Create Task.
2. Trigger: "Daily", repeat every hour (or however often new transcripts realistically show up).
3. Action: "Start a program" →
   - Program: `python`
   - Arguments: `scripts\ingest_transcripts.py`
   - Start in: the full path to your Creator OS project folder (required — this is how the script finds
     `content/transcripts/` relative to itself).

**Mac/Linux: cron**
```
0 * * * * cd /path/to/your/creator-os-folder && python3 scripts/ingest_transcripts.py >> ingest.log 2>&1
```
Runs once an hour. `crontab -e` to add it, and the `>> ingest.log` keeps a record of each run instead of
emailing you (cron's default) every time.

## Keep it light
- Re-running `ingest_transcripts.py` is cheap (it only reads transcript files, not an API), but there's
  still no benefit to running it every minute — once an hour is already far more often than most creators
  publish.
- A scheduled rebuild and the in-chat `--check` aren't competing with each other: `--check` only reports
  staleness without changing anything, so even with Option B running hourly, Step 0 of the skill will
  still correctly say "current" between scheduled runs and only flag staleness in the gap right after a
  new transcript lands.
- This is entirely optional, same as `news-sniper`'s scheduling. Option A (run it by hand after every new
  video) is what the index relies on today and works fine with zero setup.
