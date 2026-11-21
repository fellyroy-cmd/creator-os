"""Search a creator's indexed transcripts for the passages that best match a question.

content/transcripts/index.jsonl holds every transcript passage as one JSON object per line.
Until now, chat-with-channel's Step 1 asked Claude to read that whole file in the chat and pick
passages by eye. This script does the same ranking as a real, testable function instead: score
every passage by how many of the question's words it contains, and return the top matches.

This is still keyword matching, not meaning-based (embeddings) search — same tradeoff
documented in references/ingest-setup.md. The scoring logic lives here now so it can be tested
and improved in one place (e.g. swapped for an embeddings comparison later) without changing how
the skill calls it.

Usage:
    python scripts/search_transcripts.py "what's my take on pricing a first sponsorship"
    python scripts/search_transcripts.py "ai editing tools" --top 3
    python scripts/search_transcripts.py "claude code" --json
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "content" / "transcripts" / "index.jsonl"

WORD_RE = re.compile(r"[a-z0-9]+")

# Common words that would otherwise swamp the score without adding any meaning
# ("what did I say about pricing" shouldn't match every passage containing "I").
STOPWORDS = {
    "a", "about", "after", "again", "all", "am", "an", "and", "any", "are", "as", "at",
    "be", "been", "being", "but", "by", "can", "did", "do", "does", "doing", "down",
    "ever", "for", "from", "had", "has", "have", "having", "how", "i", "if", "in", "into",
    "is", "it", "its", "just", "me", "my", "of", "on", "or", "our", "out", "over", "said",
    "say", "so", "some", "than", "that", "the", "their", "then", "there", "this", "to",
    "up", "was", "we", "were", "what", "when", "where", "which", "who", "why", "will",
    "with", "you", "your",
}


def tokenize(text: str) -> list[str]:
    """Lowercase and split into words, dropping punctuation."""
    return WORD_RE.findall(text.lower())


def keywords(text: str) -> list[str]:
    """Tokenize and drop stopwords — what's left are the terms worth matching on."""
    return [word for word in tokenize(text) if word not in STOPWORDS]


def load_passages() -> list[dict]:
    """Read every passage record from index.jsonl, or [] if it doesn't exist yet."""
    if not INDEX_PATH.exists():
        return []
    passages = []
    with INDEX_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                passages.append(json.loads(line))
    return passages


def score_passage(query_words: list[str], passage_words: list[str]) -> float:
    """Score one passage against the query's keywords.

    Counts how many times each query word appears in the passage, then divides by the
    passage's own length so a short, focused passage beats a long one that only mentions a
    query word once in passing. Returns 0.0 if no query word appears at all.
    """
    if not query_words or not passage_words:
        return 0.0
    passage_word_count = len(passage_words)
    hits = sum(passage_words.count(word) for word in set(query_words))
    if hits == 0:
        return 0.0
    return hits / passage_word_count


def search(query: str, top: int = 5) -> list[dict]:
    """Return the top-scoring passages for a query, each with a "score" field added.

    Passages that score 0 (no query keyword appears at all) are left out entirely — a
    non-match shouldn't take a slot just to pad the result list to `top`.
    """
    query_words = keywords(query)
    results = []
    for passage in load_passages():
        passage_words = tokenize(passage["text"])
        score = score_passage(query_words, passage_words)
        if score > 0:
            results.append({**passage, "score": round(score, 4)})
    results.sort(key=lambda p: p["score"], reverse=True)
    return results[:top]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("query", help="the question to search for, in quotes")
    parser.add_argument("--top", type=int, default=5, help="how many passages to return (default 5)")
    parser.add_argument("--json", action="store_true", help="print raw JSON instead of a readable list")
    args = parser.parse_args()

    if not INDEX_PATH.exists():
        print(f"No index found at {INDEX_PATH.relative_to(ROOT)}. Run "
              f"scripts/ingest_transcripts.py first to build one from your transcripts.")
        sys.exit(1)

    results = search(args.query, args.top)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    if not results:
        print(f"No passages matched \"{args.query}\". Try different words, or this topic "
              f"might not be covered in an indexed transcript yet.")
        return

    print(f"Top {len(results)} match(es) for \"{args.query}\":\n")
    for rank, passage in enumerate(results, start=1):
        where = passage["source"]
        if passage.get("timestamp"):
            where += f" (~{passage['timestamp']})"
        print(f"{rank}. [{passage['score']}] {where} — chunk {passage['chunk']}")
        preview = passage["text"][:160] + ("..." if len(passage["text"]) > 160 else "")
        print(f"   \"{preview}\"\n")


if __name__ == "__main__":
    main()
