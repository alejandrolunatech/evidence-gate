"""Command line: ask the archive one question."""

import argparse
from pathlib import Path

from evidence_gate.gate import EvidenceGate
from evidence_gate.records import load_records

DEFAULT_ARCHIVE = Path(__file__).parent.parent / "data" / "archive.jsonl"


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="evidence_gate",
        description="Answer a question from the archive with a citation, or refuse.",
    )
    parser.add_argument("question", help="the question, in Dutch, English or Spanish")
    parser.add_argument(
        "--archive", type=Path, default=DEFAULT_ARCHIVE, help="JSONL file of page records"
    )
    arguments = parser.parse_args()

    gate = EvidenceGate(load_records(arguments.archive))
    answer = gate.ask(arguments.question)
    print(answer.text)
    if answer.answered:
        print(f"[1] {answer.citation}")
    print(f"({answer.reason}; coverage {answer.coverage:.2f})")


if __name__ == "__main__":
    main()