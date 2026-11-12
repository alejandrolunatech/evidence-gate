"""Tests for how the evaluation names each outcome."""

import unittest

from evidence_gate.evaluate import outcome


class OutcomeTest(unittest.TestCase):
    def test_answerable_question(self):
        self.assertEqual(outcome(True, "A", True, ["A", "B"]), "right_page")
        self.assertEqual(outcome(True, "C", True, ["A", "B"]), "wrong_page")
        self.assertEqual(outcome(False, None, True, ["A"]), "refused_answerable")

    def test_unanswerable_question(self):
        self.assertEqual(outcome(False, None, False, []), "refused_correctly")
        self.assertEqual(outcome(True, "A", False, []), "answered_unanswerable")


if __name__ == "__main__":
    unittest.main()