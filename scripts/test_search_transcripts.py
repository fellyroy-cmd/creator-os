"""Automated tests for search_transcripts.py's scoring logic.

Every script in this repo has been hand-tested with throwaway data each time it changed
(see the build session reports), then the throwaway data gets deleted — so nothing locks
the behaviour in. This file is that lock: it runs the real functions against small, fixed
inputs built right here in the test, no index.jsonl or content/transcripts/ needed. If a
future change (like swapping in embeddings) breaks the scoring in a way nobody meant, this
fails loud instead of someone noticing days later.

Uses only unittest (Python's standard library) — no new dependency, matching the rest of
this repo.

Run: python scripts/test_search_transcripts.py
"""
import unittest

from search_transcripts import (
    document_frequencies,
    keywords,
    score_passage,
    score_passage_weighted,
    tokenize,
)


class TestTokenize(unittest.TestCase):
    def test_lowercases_and_splits_on_punctuation(self):
        self.assertEqual(
            tokenize("What's my take on pricing?"),
            ["what", "s", "my", "take", "on", "pricing"],
        )

    def test_empty_string_gives_empty_list(self):
        self.assertEqual(tokenize(""), [])


class TestKeywords(unittest.TestCase):
    def test_drops_stopwords(self):
        # "what", "did", "i", "say", "about" are all stopwords — only "pricing" is a real keyword.
        self.assertEqual(keywords("What did I say about pricing"), ["pricing"])

    def test_query_of_only_stopwords_gives_empty_list(self):
        self.assertEqual(keywords("what is this"), [])


class TestScorePassage(unittest.TestCase):
    def test_no_shared_words_scores_zero(self):
        self.assertEqual(score_passage(["pricing"], ["editing", "tools", "video"]), 0.0)

    def test_shared_word_gives_positive_score(self):
        score = score_passage(["pricing"], ["pricing", "is", "hard", "to", "figure", "out"])
        self.assertGreater(score, 0.0)

    def test_short_focused_passage_beats_long_passage_with_one_mention(self):
        # Same single hit on "pricing" in both, but the short passage is entirely about it —
        # dividing by passage length is what makes the short one win. This is the exact
        # behaviour the 2026-11-21 build session explained: without normalising, the long
        # passage would win just by being long.
        short_passage = tokenize("pricing is the hardest part of a first sponsorship deal")
        long_passage = tokenize(
            "today I want to talk about my camera gear my lighting setup my editing software "
            "my microphone and also a little bit about pricing before we get into the rest of "
            "my whole workflow from start to finish"
        )
        short_score = score_passage(["pricing"], short_passage)
        long_score = score_passage(["pricing"], long_passage)
        self.assertGreater(short_score, long_score)

    def test_empty_query_words_scores_zero(self):
        self.assertEqual(score_passage([], ["any", "passage", "text"]), 0.0)

    def test_empty_passage_scores_zero(self):
        self.assertEqual(score_passage(["pricing"], []), 0.0)

    def test_repeated_word_in_passage_counts_each_time(self):
        # "tools" appears twice, "ai" once elsewhere in the passage.
        passage_words = tokenize("ai tools are great tools honestly")
        score = score_passage(["tools"], passage_words)
        self.assertAlmostEqual(score, 2 / 6)


class TestDocumentFrequencies(unittest.TestCase):
    def test_counts_how_many_passages_each_word_appears_in(self):
        passages = [
            tokenize("pricing is hard"),
            tokenize("pricing and editing"),
            tokenize("editing software review"),
        ]
        counts = document_frequencies(passages)
        # "pricing" is in 2 of 3 passages, "editing" is in 2 of 3, "review" is in 1 of 3.
        self.assertEqual(counts["pricing"], 2)
        self.assertEqual(counts["editing"], 2)
        self.assertEqual(counts["review"], 1)

    def test_word_repeated_within_one_passage_only_counts_once(self):
        # "tools" appears twice in the one passage — document frequency counts passages,
        # not raw occurrences, so it should still be 1.
        passages = [tokenize("tools tools tools")]
        counts = document_frequencies(passages)
        self.assertEqual(counts["tools"], 1)

    def test_empty_corpus_gives_empty_counts(self):
        self.assertEqual(document_frequencies([]), {})


class TestScorePassageWeighted(unittest.TestCase):
    def test_no_shared_words_scores_zero(self):
        doc_frequencies = {"pricing": 1}
        score = score_passage_weighted(["pricing"], ["editing", "tools"], doc_frequencies, 5)
        self.assertEqual(score, 0.0)

    def test_empty_query_or_passage_scores_zero(self):
        doc_frequencies = {"pricing": 1}
        self.assertEqual(score_passage_weighted([], ["pricing"], doc_frequencies, 5), 0.0)
        self.assertEqual(score_passage_weighted(["pricing"], [], doc_frequencies, 5), 0.0)

    def test_zero_total_passages_scores_zero_instead_of_dividing_by_zero(self):
        self.assertEqual(score_passage_weighted(["pricing"], ["pricing"], {}, 0), 0.0)

    def test_rare_word_scores_higher_than_common_word_with_same_raw_hits(self):
        # Same corpus, two queries that each hit exactly once in the same passage. "sponsorship"
        # appears in only 1 of 5 passages (rare/distinctive); "video" appears in all 5 (common).
        # A real embeddings-style search should reward the rare, specific word — this is the
        # whole point of swapping flat counting for TF-IDF weighting.
        doc_frequencies = {"sponsorship": 1, "video": 5}
        passage_words = tokenize("this video is about sponsorship deals")
        rare_score = score_passage_weighted(["sponsorship"], passage_words, doc_frequencies, 5)
        common_score = score_passage_weighted(["video"], passage_words, doc_frequencies, 5)
        self.assertGreater(rare_score, common_score)

    def test_matches_flat_score_proportionally_when_every_word_is_equally_common(self):
        # If every query word has the same document frequency, the IDF weight is a constant
        # multiplier — so a short, focused passage should still beat a long passage with one
        # mention, exactly like the unweighted score_passage test above.
        doc_frequencies = {"pricing": 2}
        short_passage = tokenize("pricing is the hardest part of a first sponsorship deal")
        long_passage = tokenize(
            "today I want to talk about my camera gear my lighting setup my editing software "
            "my microphone and also a little bit about pricing before we get into the rest of "
            "my whole workflow from start to finish"
        )
        short_score = score_passage_weighted(["pricing"], short_passage, doc_frequencies, 10)
        long_score = score_passage_weighted(["pricing"], long_passage, doc_frequencies, 10)
        self.assertGreater(short_score, long_score)

    def test_word_missing_from_doc_frequencies_falls_back_to_least_distinctive(self):
        # A word that matched the passage but wasn't in doc_frequencies (shouldn't happen with
        # real data from the same corpus, but guards against a mismatched call) should be
        # treated as appearing in every passage — the least interesting case — not crash.
        score = score_passage_weighted(["pricing"], tokenize("pricing talk"), {}, 5)
        self.assertGreater(score, 0.0)


if __name__ == "__main__":
    unittest.main()
