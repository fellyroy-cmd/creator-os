"""Automated tests for ingest_transcripts.py's pure chunking logic.

Follows the same pattern CONTRIBUTING.md documents (see test_search_transcripts.py): only the
two functions here that don't touch the filesystem get tested — strip_captions (turns raw
.vtt/.srt caption text into plain prose) and chunk_words (splits a word list into overlapping
windows). check_staleness, build_index and main all read content/transcripts/ from disk, so
they're left to hand-testing with real throwaway files, same as before.

Uses only unittest (Python's standard library) — no new dependency.

Run: python scripts/test_ingest_transcripts.py
"""
import unittest

from ingest_transcripts import chunk_words, strip_captions


class TestStripCaptions(unittest.TestCase):
    def test_strips_vtt_header_cue_numbers_and_timestamps(self):
        vtt = (
            "WEBVTT\n\n"
            "1\n"
            "00:00:00.000 --> 00:00:02.000\n"
            "Hey everyone, welcome back.\n\n"
            "2\n"
            "00:00:02.000 --> 00:00:04.500\n"
            "Today we're talking about pricing.\n"
        )
        text, first_timestamp = strip_captions(vtt)
        self.assertEqual(text, "Hey everyone, welcome back. Today we're talking about pricing.")
        self.assertEqual(first_timestamp, "00:00:00")

    def test_strips_inline_cue_tags(self):
        # Auto-generated .vtt files sometimes wrap individual words in timing/style tags.
        # The leading space survives because it sits between the stripped tags, not around them.
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.040 --> 00:00:03.000\n"
            "<00:00:01.040><c> word</c> one <c>two</c>\n"
        )
        text, _ = strip_captions(vtt)
        self.assertEqual(text, " word one two")

    def test_no_timestamp_lines_gives_none(self):
        text, first_timestamp = strip_captions("WEBVTT\n\njust some text with no cue lines\n")
        self.assertEqual(text, "just some text with no cue lines")
        self.assertIsNone(first_timestamp)

    def test_empty_input_gives_empty_text_and_no_timestamp(self):
        text, first_timestamp = strip_captions("")
        self.assertEqual(text, "")
        self.assertIsNone(first_timestamp)


class TestChunkWords(unittest.TestCase):
    def test_empty_word_list_gives_no_chunks(self):
        self.assertEqual(chunk_words([], words_per_chunk=5, overlap_words=1), [])

    def test_shorter_than_one_chunk_gives_a_single_chunk(self):
        words = ["one", "two", "three"]
        self.assertEqual(chunk_words(words, words_per_chunk=10, overlap_words=2), [words])

    def test_splits_into_overlapping_windows(self):
        words = [str(n) for n in range(1, 11)]  # ["1", ..., "10"]
        chunks = chunk_words(words, words_per_chunk=4, overlap_words=1)
        # step = 4 - 1 = 3, so windows start at 0, 3, 6 — the loop stops once a window
        # reaches the end of the list (start=6 covers index 6..9, i.e. words 7-10, the last word).
        self.assertEqual(chunks, [
            ["1", "2", "3", "4"],
            ["4", "5", "6", "7"],
            ["7", "8", "9", "10"],
        ])

    def test_last_chunk_can_be_shorter_than_the_rest(self):
        words = [str(n) for n in range(1, 8)]  # 7 words
        chunks = chunk_words(words, words_per_chunk=5, overlap_words=0)
        self.assertEqual(chunks, [
            ["1", "2", "3", "4", "5"],
            ["6", "7"],
        ])

    def test_zero_overlap_never_repeats_a_word(self):
        words = [str(n) for n in range(1, 13)]
        chunks = chunk_words(words, words_per_chunk=4, overlap_words=0)
        flattened = [word for chunk in chunks for word in chunk]
        self.assertEqual(flattened, words)


if __name__ == "__main__":
    unittest.main()
