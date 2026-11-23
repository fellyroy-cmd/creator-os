"""Automated tests for send_alert.py's pure helper functions.

Same convention as test_search_transcripts.py and test_ingest_transcripts.py: lock in the
logic that doesn't touch the filesystem or the network, hand-test the rest. send_alert.py's
three channel senders (send_telegram/send_discord/send_email) all read .env and either make a
real HTTP/SMTP call or build a --dry-run string — that network-and-env-dependent behaviour
stays hand-tested with --dry-run, same boundary this repo has kept since 2026-11-21.

missing_vars and _safe_error take plain data in and return plain data out, nothing else —
the same shape as tokenize/keywords/score_passage and chunk_words/strip_captions before them.
_safe_error is the one worth locking in most: it's the function responsible for keeping a
real token, password or webhook URL out of a terminal, log file or CI output, so a future
edit that breaks the redaction should fail loud here, not get noticed in a leaked secret.

Uses only unittest (Python's standard library) — no new dependency, matching the rest of
this repo.

Run: python scripts/test_send_alert.py
"""
import unittest

from send_alert import _safe_error, missing_vars


class TestMissingVars(unittest.TestCase):
    def test_all_present_returns_empty_list(self):
        import os

        os.environ["TEST_SEND_ALERT_VAR_A"] = "x"
        try:
            self.assertEqual(missing_vars(["TEST_SEND_ALERT_VAR_A"]), [])
        finally:
            del os.environ["TEST_SEND_ALERT_VAR_A"]

    def test_unset_var_is_reported_missing(self):
        self.assertEqual(missing_vars(["TEST_SEND_ALERT_VAR_DOES_NOT_EXIST"]), [
            "TEST_SEND_ALERT_VAR_DOES_NOT_EXIST",
        ])

    def test_blank_value_counts_as_missing(self):
        # A var that's set but empty (e.g. "SMTP_PASSWORD=" left blank in .env) must still
        # be flagged — an empty string is still falsy-but-present, which .strip() catches.
        import os

        os.environ["TEST_SEND_ALERT_VAR_BLANK"] = "   "
        try:
            self.assertEqual(missing_vars(["TEST_SEND_ALERT_VAR_BLANK"]), [
                "TEST_SEND_ALERT_VAR_BLANK",
            ])
        finally:
            del os.environ["TEST_SEND_ALERT_VAR_BLANK"]

    def test_checks_each_name_independently_and_keeps_order(self):
        import os

        os.environ["TEST_SEND_ALERT_VAR_SET"] = "present"
        try:
            result = missing_vars([
                "TEST_SEND_ALERT_VAR_SET",
                "TEST_SEND_ALERT_VAR_MISSING_1",
                "TEST_SEND_ALERT_VAR_MISSING_2",
            ])
            self.assertEqual(result, [
                "TEST_SEND_ALERT_VAR_MISSING_1",
                "TEST_SEND_ALERT_VAR_MISSING_2",
            ])
        finally:
            del os.environ["TEST_SEND_ALERT_VAR_SET"]


class TestSafeError(unittest.TestCase):
    def test_blanks_out_the_secret(self):
        err = Exception("401 Unauthorized for token abc123secret")
        self.assertEqual(_safe_error(err, "abc123secret"), "401 Unauthorized for token ***")

    def test_blanks_every_occurrence_not_just_the_first(self):
        err = Exception("tried xyz789 then retried with xyz789 again")
        self.assertEqual(_safe_error(err, "xyz789"), "tried *** then retried with *** again")

    def test_empty_secret_leaves_message_untouched(self):
        # send_email passes password="" is never the case in practice, but a blank secret
        # string must not turn into replacing every character boundary with "***".
        err = Exception("connection refused")
        self.assertEqual(_safe_error(err, ""), "connection refused")

    def test_secret_not_present_in_message_leaves_it_unchanged(self):
        err = Exception("timed out after 20s")
        self.assertEqual(_safe_error(err, "some-other-token"), "timed out after 20s")


if __name__ == "__main__":
    unittest.main()
