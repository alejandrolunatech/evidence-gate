"""Tests for the evidence gate: answer with a citation, or refuse."""

import unittest
from pathlib import Path

from evidence_gate.gate import MIN_COVERAGE, REFUSAL, EvidenceGate
from evidence_gate.records import load_records

ARCHIVE = Path(__file__).parent.parent / "data" / "archive.jsonl"


class EvidenceGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gate = EvidenceGate(load_records(ARCHIVE))

    def test_answers_with_a_citation(self):
        answer = self.gate.ask("How long are the piles under block 3?")
        self.assertTrue(answer.answered)
        self.assertEqual(answer.citation, "ZH-0122-p001")
        self.assertIn("14,50", answer.text)
        self.assertIn("[1]", answer.text)

    def test_same_page_in_dutch_and_spanish(self):
        questions = (
            "Hoe lang zijn de palen van blok 3?",
            "¿Qué longitud tienen los pilotes del bloque 3?",
        )
        for question in questions:
            with self.subTest(question=question):
                self.assertEqual(self.gate.ask(question).citation, "ZH-0122-p001")

    def test_refuses_when_coverage_is_low(self):
        answer = self.gate.ask("What is the monthly rent of a type A house?")
        self.assertFalse(answer.answered)
        self.assertEqual(answer.text, REFUSAL)
        self.assertEqual(answer.reason, "low_coverage")
        self.assertLess(answer.coverage, MIN_COVERAGE)

    def test_refuses_when_the_best_page_says_the_archive_lacks_it(self):
        answer = self.gate.ask("Is there asbestos in the roof boarding?")
        self.assertFalse(answer.answered)
        self.assertEqual(answer.reason, "archive_lacks_this")

    def test_empty_question_is_refused(self):
        answer = self.gate.ask("")
        self.assertFalse(answer.answered)
        self.assertEqual(answer.reason, "no_candidates")


if __name__ == "__main__":
    unittest.main()