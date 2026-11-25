"""Search a creator's indexed transcripts for the passages that best match a question.

content/transcripts/index.jsonl holds every transcript passage as one JSON object per line.
Until now, chat-with-channel's Step 1 asked Claude to read that whole file in the chat and pick
passages by eye. This script does the same ranking as a real, testable function instead.

Scoring is now TF-IDF weighted, not a flat word count. Every creator repeats certain words in
almost every video ("video", "content", "honestly") — those words tell the search nothing about
which passage actually answers the question, but a flat count treats them the same as a rare,
specific word like "sponsorship" or "pricing". TF-IDF fixes this by weighting each matched word
by how rare it is *across this creator's whole indexed channel*: a word that shows up in 2 of 50
passages counts for far more than one that shows up in 48 of 50. This is still a from-scratch,
local calculation over word counts, not a neural embedding — but it's the same underlying idea
(each passage becomes a weighted vector, matched by overlap with the query's vector) and the
genuine next step before a real embeddings swap, which is still future work (see
references/ingest-setup.md). No new dependency: corpus statistics are plain stdlib math over
the same index.jsonl this script already reads.

Usage:
    python scripts/search_transcripts.py "what's my take on pricing a first sponsorship"
    python scripts/search_transcripts.py "ai editing tools" --top 3
    python scripts/search_transcripts.py "claude code" --json
"""
import argparse
import json
import math
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
    """Score one passage against the query's keywords, ignoring how rare each word is.

    Counts how many times each query word appears in the passage, then divides by the
    passage's own length so a short, focused passage beats a long one that only mentions a
    query word once in passing. Returns 0.0 if no query word appears at all.

    This is the plain term-overlap score from the first version of this script. `search()`
    no longer calls it directly — it's kept (and still tested) as the simple building block
    `document_frequencies`/`score_passage_weighted` are compared against, and because it's
    still a reasonable score for a single passage in isolation, with no corpus to weight against.
    """
    if not query_words or not passage_words:
        return 0.0
    passage_word_count = len(passage_words)
    hits = sum(passage_words.count(word) for word in set(query_words))
    if hits == 0:
        return 0.0
    return hits / passage_word_count


def document_frequencies(all_passage_words: list[list[str]]) -> dict[str, int]:
    """For every word seen anywhere, how many passages it appears in at least once.

    This is the corpus-wide count TF-IDF weighting needs: a word that shows up in nearly
    every passage (document frequency close to the total passage count) is common for this
    creator and tells a search almost nothing; a word that shows up in only one or two
    passages is distinctive and should count for much more when it matches the query.
    """
    counts: dict[str, int] = {}
    for words in all_passage_words:
        for word in set(words):
            counts[word] = counts.get(word, 0) + 1
    return counts


def score_passage_weighted(
    query_words: list[str],
    passage_words: list[str],
    doc_frequencies: dict[str, int],
    total_passages: int,
) -> float:
    """Score one passage against the query, weighting each matched word by how rare it is.

    Same shape as score_passage (count matches, normalise by passage length) but each word's
    contribution is multiplied by its inverse document frequency (IDF) instead of counting 1
    per hit: log(total_passages / document_frequency), so a word indexed in just a couple of
    passages scores far higher than one that shows up almost everywhere. A word with no
    recorded document frequency (shouldn't happen if doc_frequencies came from the same corpus
    being searched, but keeps this safe against mismatched inputs) is treated as appearing in
    every passage — the least distinctive case, not a crash.
    """
    if not query_words or not passage_words or total_passages <= 0:
        return 0.0
    passage_word_count = len(passage_words)
    weighted_hits = 0.0
    for word in set(query_words):
        occurrences = passage_words.count(word)
        if occurrences == 0:
            continue
        doc_frequency = doc_frequencies.get(word, total_passages)
        idf = math.log((total_passages + 1) / (doc_frequency + 1)) + 1
        weighted_hits += occurrences * idf
    if weighted_hits == 0.0:
        return 0.0
    return weighted_hits / passage_word_count


def search(query: str, top: int = 5) -> list[dict]:
    """Return the top-scoring passages for a query, each with a "score" field added.

    Scores with TF-IDF weighting (score_passage_weighted) so a rare, distinctive word in the
    question counts for more than a word the creator uses in almost every video. Passages that
    score 0 (no query keyword appears at all) are left out entirely — a non-match shouldn't
    take a slot just to pad the result list to `top`.
    """
    query_words = keywords(query)
    passages = load_passages()
    all_passage_words = [tokenize(passage["text"]) for passage in passages]
    doc_frequencies = document_frequencies(all_passage_words)
    total_passages = len(passages)

    results = []
    for passage, passage_words in zip(passages, all_passage_words):
        score = score_passage_weighted(query_words, passage_words, doc_frequencies, total_passages)
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

    if args.top <= 0:
        # Without this check, --top 0 (or a negative number) silently returns an empty result
        # list, which prints the exact same "No passages matched" message as a genuine no-match
        # case — misleading the creator into thinking a topic isn't covered when it actually is,
        # and --top is just set to return nothing. A clear, immediate error beats a confusing
        # false negative.
        parser.error(f"--top must be a positive number (got {args.top}).")

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
