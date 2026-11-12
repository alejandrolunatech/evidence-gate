"""Answer from the best archive page with a citation, or refuse."""

from dataclasses import dataclass

from evidence_gate.glossary import expand, units
from evidence_gate.records import Record
from evidence_gate.search import Searcher
from evidence_gate.text import tokenize

MIN_COVERAGE = 0.5  # fraction of query words that must be in the answer
REFUSAL = "I don't know. I can't find a relevant page in the archive."

@dataclass(frozen=True)
class Answer:
    answered: bool
    text: str
    citation: str | None
    coverage: float
    reason: str

class EvidenceGate:
    """Search, measure how much of the question the best page covers, then decide."""

    def __init__(self, records: list[Record]):
        self.searcher = Searcher(records)
        self.words = {record.id: set(tokenize(record.searchable)) for record in records}
        self.idf = self.searcher.bm25.idf
        self.rarest = max(self.idf.values(), default=1.0)

    def weight(self, unit: frozenset[str]) -> float:
        """A unit weighs as much as its rarest known word; unknown words weigh the most."""
        known = [self.idf[word] for word in unit if word in self.idf]
        return max(known) if known else self.rarest

    def coverage(self, question: str, record: Record) -> float:
        """Share of the question's weight that the record contains, from 0 to 1."""
        question_units = units(question)
        total = sum(self.weight(unit) for unit in question_units)
        if total == 0:
            return 0.0
        found = sum(self.weight(unit) for unit in question_units if unit & self.words[record.id])
        return found / total

    def ask(self, question: str) -> Answer:
        """Return the best answer with a citation, or refuse."""
        candidates = self.searcher.search(expand(question))
        if not candidates:
            return Answer(False, REFUSAL, None, 0.0, "no_candidates")
        best = max(candidates, key=lambda record: self.coverage(question, record))
        score = self.coverage(question, best)
        if score < MIN_COVERAGE:
            return Answer(False, REFUSAL, None, score, "low_coverage")
        if best.absence:
            return Answer(False, REFUSAL, best.id, score, "archive_lacks_this")
        text = f"According to sheet {best.sheet}, {best.title}: {best.text} [1]"
        return Answer(True, text, best.id, score, "answered")