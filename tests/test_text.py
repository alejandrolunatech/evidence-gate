"""Tests for text normalization, tokens and n-grams."""

import unittest

from evidence_gate.text import char_ngrams, normalize, tokenize

class TextTest(unittest.TestCase):
    def test_normalize_drops_case_and_accents(self):
        self.assertEqual(normalize("Década Fundación"), "decada fundacion")

    def test_tokenize_keeps_decimal_numbers_and_drops_stopwords(self):
        self.assertEqual(
            tokenize("How long are the piles? 14,50 m"),
            ["long", "piles", "14,50", "m"],
        )

    def test_compound_shares_ngrams_with_its_parts(self):
        shared = set(char_ngrams("palenplan")) & set(char_ngrams("palen"))
        self.assertIn(" pal", shared)

    def test_empty_text_gives_nothing(self):
        self.assertEqual(tokenize("   "), [])
        self.assertEqual(char_ngrams(""), [])

if __name__ == "__main__":
    unittest.main()