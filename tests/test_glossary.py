"""Test for the multilingual building glossary."""

import unittest

from evidence_gate.glossary import expand, units

class GlossaryTest(unittest.TestCase):
    def test_three_languages_give_the_same_units(self):
        english = units("piles")
        self.assertEqual(english, units("palen"))
        self.assertEqual(english, units("pilotes"))

    def test_unknown_words_is_its_own_unit(self):
        self.assertEqual(units("rent"), [frozenset(["rent"])])

    def test_repeated_concept_counts_once(self):
        self.assertEqual(len(units("pile piles palen")), 1)

    def test_expand_adds_the_other_languages(self):
        expanded = expand("How long are the piles under block 3?")
        self.assertIn("piles", expanded)
        self.assertIn("blok", expanded)
        self.assertIn("lengte", expanded)

if __name__ == "__main__":
    unittest.main()