"""Chunk a creator's video transcripts into passages for chat-with-channel to search.

Reads every transcript in content/transcripts/ (plain .txt or .md, or .vtt/.srt caption
files exported from YouTube) and writes content/transcripts/index.jsonl: one JSON object per
passage, each a few hundred words with a little overlap into the next one so an answer
that spans a chunk boundary doesn't get cut in half.

This is retrieval, not an API call: no embeddings, no paid service, nothing leaves the
creator's computer. chat-with-channel finds passages by keyword match over this file.
A smarter (embedding-based) search can replace the matching step later without touching
this script — the index format stays the same.

Usage:
    python scripts/ingest_transcripts.py
    python scripts/ingest_transcripts.py --words-per-chunk 250 --overlap-words 40
    python scripts/ingest_transcripts.py --dry-run
    python scripts/ingest_transcripts.py --check

--dry-run prints how many files and chunks it would write, without touching index.jsonl —
safe to run first to sanity-check a new batch of transcripts before committing to it.

--check reports whether index.jsonl is stale (a transcript file is newer than the index, or
a transcript was removed) and exits — it doesn't read or chunk any transcript, so it's fast
enough to run before every chat-with-channel question as a cheap "is this still current?"
check. Exit code is 0 if the index is current, 1 if it's stale or missing (handy for scripts
or a future scheduled task to key off of).

Supported formats:
    .txt   plain text, one video's transcript, any length
    .md    plain text, same handling as .txt (headers and formatting are indexed as-is)
    .vtt   WebVTT captions (YouTube's "Download captions" export) — timestamp cues stripped,
           text joined into continuous prose, first cue's start time kept per chunk
    .srt   SubRip captions (the other common export) — same handling as .vtt

File naming: name each file after the video so the creator can tell chunks apart later,
e.g. "2026-09-12-how-i-use-claude-code.txt". The filename (minus extension) becomes each
chunk's "source" field.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSCRIPTS_DIR = ROOT / "content" / "transcripts"
INDEX_PATH = TRANSCRIPTS_DIR / "index.jsonl"

TIMESTAMP_LINE = re.compile(
    r"^\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[.,]\d{3}"
)
CUE_NUMBER_LINE = re.compile(r"^\d+$")
FIRST_TIMESTAMP = re.compile(r"(\d{2}:\d{2}:\d{2})")


def strip_captions(text: str) -> tuple[str, str | None]:
    """Turn .vtt/.srt caption text into plain prose, plus the first timestamp seen (or None).

    Drops the WEBVTT header, cue numbers, timestamp lines and caption styling tags
    (like <c> or <00:00:01.500>), then joins what's left into one block of text.
    """
    first_timestamp = None
    lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line == "WEBVTT":
            continue
        if CUE_NUMBER_LINE.match(line):
            continue
        match = TIMESTAMP_LINE.match(line)
        if match:
            if first_timestamp is None:
                found = FIRST_TIMESTAMP.search(line)
                if found:
                    first_timestamp = found.group(1)
            continue
        # Inline cue tags like <00:00:01.040><c> word</c> show up in some auto-generated .vtt files.
        line = re.sub(r"<[^>]+>", "", line)
        if line:
            lines.append(line)
    return " ".join(lines), first_timestamp


def load_transcript(path: Path) -> tuple[str, str | None]:
    """Read one transcript file, return (plain_text, first_timestamp_or_None)."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() in (".vtt", ".srt"):
        return strip_captions(raw)
    return " ".join(raw.split()), None


def chunk_words(words: list[str], words_per_chunk: int, overlap_words: int) -> list[list[str]]:
    """Split a word list into overlapping windows, each words_per_chunk long (last one shorter)."""
    if not words:
        return []
    step = max(words_per_chunk - overlap_words, 1)
    chunks = []
    start = 0
    while start < len(words):
        chunks.append(words[start:start + words_per_chunk])
        if start + words_per_chunk >= len(words):
            break
        start += step
    return chunks


def find_transcript_files() -> list[Path]:
    """List every supported transcript file currently in content/transcripts/, sorted by name."""
    return sorted(
        p for p in TRANSCRIPTS_DIR.glob("*")
        if p.suffix.lower() in (".txt", ".vtt", ".srt", ".md")
    )


def check_staleness() -> tuple[bool, str]:
    """Compare index.jsonl's age and sources against what's in content/transcripts/ right now.

    Returns (is_stale, message). "Stale" covers three cases: the index doesn't exist yet, a
    transcript file is newer than the index (edited or added since the last ingest run), or a
    transcript that's listed in the index no longer exists on disk (deleted since last ingest).
    This only reads file metadata (mtimes) and the index's "source" fields — it never opens or
    re-chunks a transcript, so it's cheap enough to run before every question.
    """
    files = find_transcript_files()

    if not INDEX_PATH.exists():
        if not files:
            return False, "No transcripts indexed yet, and none found to index."
        return True, f"No index yet, but {len(files)} transcript file(s) are waiting to be indexed."

    index_mtime = INDEX_PATH.stat().st_mtime
    newer = [p.name for p in files if p.stat().st_mtime > index_mtime]

    indexed_sources = set()
    with INDEX_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                indexed_sources.add(json.loads(line)["source"])
    current_sources = {p.stem for p in files}
    removed = sorted(indexed_sources - current_sources)

    if not newer and not removed:
        return False, f"Index is current: {len(files)} file(s), matches content/transcripts/."

    parts = []
    if newer:
        parts.append(f"{len(newer)} file(s) changed since last ingest ({', '.join(sorted(newer))})")
    if removed:
        parts.append(f"{len(removed)} indexed source(s) no longer on disk ({', '.join(removed)})")
    return True, "Index is stale: " + "; ".join(parts) + ". Re-run without --check to rebuild."


def build_index(words_per_chunk: int, overlap_words: int) -> list[dict]:
    """Chunk every transcript file in content/transcripts/ into passage records."""
    passages = []
    files = find_transcript_files()
    for path in files:
        source = path.stem
        text, timestamp = load_transcript(path)
        words = text.split()
        for chunk_number, chunk in enumerate(chunk_words(words, words_per_chunk, overlap_words), start=1):
            passages.append({
                "id": f"{source}#{chunk_number}",
                "source": source,
                "chunk": chunk_number,
                "timestamp": timestamp,  # best-effort: the file's first caption time, not per-chunk
                "text": " ".join(chunk),
            })
    return passages


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--words-per-chunk", type=int, default=220,
                         help="words per passage (default 220, roughly 90 seconds of talking)")
    parser.add_argument("--overlap-words", type=int, default=40,
                         help="words repeated at the start of the next chunk (default 40)")
    parser.add_argument("--dry-run", action="store_true",
                         help="report what would be written, without touching index.jsonl")
    parser.add_argument("--check", action="store_true",
                         help="report whether the index is stale, without reading or writing transcripts")
    args = parser.parse_args()

    if not TRANSCRIPTS_DIR.exists():
        print(f"No {TRANSCRIPTS_DIR.relative_to(ROOT)} folder yet. Create it and add your transcripts "
              f"(.txt, .md, .vtt or .srt) — see skills/chat-with-channel/references/ingest-setup.md.")
        sys.exit(1)

    if args.check:
        is_stale, message = check_staleness()
        print(message)
        sys.exit(1 if is_stale else 0)

    passages = build_index(args.words_per_chunk, args.overlap_words)
    file_count = len({p["source"] for p in passages})

    if not passages:
        print(f"No .txt/.md/.vtt/.srt transcripts found in {TRANSCRIPTS_DIR.relative_to(ROOT)}. "
              f"Drop one or more in there and run this again.")
        sys.exit(1)

    if args.dry_run:
        print(f"Would write {len(passages)} passage(s) from {file_count} file(s) to "
              f"{INDEX_PATH.relative_to(ROOT)} (dry run, nothing written).")
        return

    with INDEX_PATH.open("w", encoding="utf-8") as handle:
        for passage in passages:
            handle.write(json.dumps(passage, ensure_ascii=False) + "\n")

    print(f"Wrote {len(passages)} passage(s) from {file_count} file(s) to "
          f"{INDEX_PATH.relative_to(ROOT)}.")


if __name__ == "__main__":
    main()
