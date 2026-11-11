"""Load the archive's page records from JSONL file and validate them."""

import json
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Record:
    """One archive page: what the drawing says and how to cite it."""

    id: str
    title: str
    sheet: str
    doc_type: str
    text: str
    absence: bool

    @property
    def searchable(self) -> str:
        return f"{self.title} {self.text}"


def load_records(path: Path) -> list[Record]:
    """Read one record per line; fail with the line number on bad input."""
    records: list[Record] = []
    seen_ids: set[str] = set()
    lines = path.read_text(encoding="utf-8").splitlines()
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = Record(**json.loads(line))
        except (json.JSONDecodeError, TypeError) as err:
            raise ValueError(f"{path}:{line_number}: invalid record: {err}") from err
        if record.id in seen_ids:
            raise ValueError(f"{path}:{line_number}: duplicate id {record.id}")
        seen_ids.add(record.id)
        records.append(record)
    return records