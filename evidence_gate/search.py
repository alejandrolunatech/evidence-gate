"""Rank archive records against a question: BM25, n-grams TF-IDF, and RRF."""

import math
from collections import Counter

class BM25:
    """Okapi BM25 over pre-tokenized documents."""

    def __init__(self, documents: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.term_counts = [Counter(document) for document in documents]
        self.lengths = [len(document) for document in documents]
        self.average_length = sum(self.lengths) / max(len(documents), 1)
        document_frequency = Counter(term for document in documents for term in set(document))
        total = len(documents)
        self.idf = {
            term: math.log(1 + (total - count + 0.5) / (count + 0.5))
            for term, count in document_frequency.items()
        }

    def scores(self, query: list[str]) -> list[float]:
        """One score per document, in the same order as the documents."""
        results = []
        for counts, length in zip(self.term_counts, self.lengths):
            score = 0.0
            for term in query:
                frequency = counts[term]
                if frequency == 0:
                    continue
                damping = self.k1 * (1 - self.b + self.b * length / self.average_length)
                score += self.idf[term] * frequency * (self.k1 + 1) / (frequency + damping)
            results.append(score)
        return results

def ranking(scores: list[float]) -> list[int]:
    """Document positions from best to worst, leaving out zero scores."""
    order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    return [i for i in order if scores[i] > 0]