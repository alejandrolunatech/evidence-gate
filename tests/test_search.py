"""Tests for the BM25 ranking."""

import unittest
from pathlib import Path

from evidence_gate.records import load_records
from evidence_gate.search import BM25, ranking
from evidence_gate.text import tokenize

ARCHIVE = Path(__file__).parent.parent / "data" / "archive.jsonl"


class BM25Test(unittest.TestCase):
    def test_rare_term_beats_common_term(self):
        bm25 = BM25([["pile", "house"], ["house", "roof"], ["house", "door"]])
        self.assertGreater(bm25.idf["pile"], bm25.idf["house"])

    def test_no_shared_terms_scores_zero(self):
        bm25 = BM25([["pile"], ["roof"]])
        self.assertEqual(bm25.scores(["window"]), [0.0, 0.0])
        self.assertEqual(ranking(bm25.scores(["window"])), [])

    def test_finds_the_pile_plan_of_block_3(self):
        records = load_records(ARCHIVE)
        bm25 = BM25([tokenize(record.searchable) for record in records])
        best = ranking(bm25.scores(tokenize("palenplan blok 3")))[0]
        self.assertEqual(records[best].id, "ZH-0122-p001")


if __name__ == "__main__":
    unittest.main()