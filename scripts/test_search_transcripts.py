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

from search_transcripts import keywords, score_passage, tokenize


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


if __name__ == "__main__":
    unittest.main()
