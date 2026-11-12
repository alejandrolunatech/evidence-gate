"""Measure the gate on the golden questions: right page, wrong page, refusals."""

import json
from collections import Counter
from pathlib import Path

from evidence_gate.gate import EvidenceGate
from evidence_gate.records import load_records

DATA = Path(__file__).parent.parent / "data"

def outcome(answered: bool, citation: str | None, answerable: bool, expected: list[str]) -> str:
    """Name what happened for one question."""
    if not answerable:
        return "refused_correctly" if not answered else "answered_unanswerable"
    if not answered:
        return "refused_answerable" 
    return "right_page" if citation in expected else "wrong_page"

def main() -> None:
    gate = EvidenceGate(load_records(DATA / "archive.jsonl"))
    lines = (DATA / "golden.jsonl").read_text(encoding="utf-8").splitlines()
    questions = [json.loads(line) for line in lines if line.strip()]
    counts: Counter[str] = Counter()
    for item in questions:
        answer = gate.ask(item["question"])
        result = outcome(
            answer.answered, answer.citation, item["answerable"], item["expected_pages"]
        )
        counts[result] += 1
        if result not in ("right_page", "refused_correctly"):
            print(f"miss {item['id']}: {result} ({answer.coverage:.2f}) {item['question']}")
    answerable = sum(1 for item in questions if item["answerable"])
    print()
    print(f"answerable questions:   {answerable}")
    print(f"  right page cited:     {counts['right_page']}")
    print(f"  wrong page cited:     {counts['wrong_page']}")
    print(f"  refused (a miss):     {counts['refused_answerable']}")
    print(f"unanswerable questions: {len(questions) - answerable}")
    print(f"  refused correctly:    {counts['refused_correctly']}")
    print(f"  answered (dangerous): {counts['answered_unanswerable']}")

if __name__ == "__main__":
    main()