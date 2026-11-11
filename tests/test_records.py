"""Tests for loading and validating archive records."""

import tempfile
import unittest
from pathlib import Path

from evidence_gate.records import Record, load_records

ARCHIVE = Path(__file__).parent.parent / "data" / "archive.jsonl"
GOOD_LINE = (
    '{"id": "A-1", "title": "t", "sheet": "1", "doc_type": "other",'
    ' "text": "x", "absence": false}'
)

class LoadRecordsTest(unittest.TestCase):
    def load_text(self,content: str):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "records.jsonl"
            path.write_text(content, encoding="utf-8")
            return load_records(path)

    def test_loads_the_archive(self):
        records = load_records(ARCHIVE)
        self.assertEqual(len(records), 23)
        self.assertEqual(records[0].id, "ZH-0101-p001")

    def test_absence_notes_are_flagged(self):
        records = load_records(ARCHIVE)
        self.assertTrue(any(record.absence for record in records))

    def test_bad_json_names_the_line(self):
        with self.assertRaisesRegex(ValueError, r":2: invalid record"):
            self.load_text(GOOD_LINE + "\n{not json\n")

    def test_duplicate_id_is_rejected(self):
        with self.assertRaisesRegex(ValueError, r":2: duplicate id A-1"):
            self.load_text(GOOD_LINE + "\n" + GOOD_LINE + "\n")

if __name__ == "__main__":
    unittest.main()