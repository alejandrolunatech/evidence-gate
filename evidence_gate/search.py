"""Rank archive records against a question: BM25, n-grams TF-IDF, and RRF."""

import math
from collections import Counter
from evidence_gate.records import Record
from evidence_gate.text import char_ngrams, tokenize

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

class NgramIndex:
    """TF-IDF cosine similarity over character n-grams."""

    def __init__(self, documents: list[list[str]]):
        document_frequency = Counter(gram for document in documents for gram in set(document))
        total = len(documents)
        self.idf = {gram: math.log(1 + total / count) for gram, count in document_frequency.items()}
        self.vectors = [self._vector(document) for document in documents]

    def _vector(self, grams: list[str]) -> dict[str, float]:
        """Weight each known gram by count times IDF, scaled to length 1."""
        weights = {
            gram: count * self.idf[gram]
            for gram, count in Counter(grams).items()
            if gram in self.idf
        }
        length = math.sqrt(sum(weight * weight for weight in weights.values()))
        if length == 0:
            return {}
        return {gram: weight / length for gram, weight in weights.items()}

    def scores(self, query: list[str]) -> list[float]:
        """Cosine similarity between the query and every document."""
        query_vector = self._vector(query)
        return [
            sum(weight * vector.get(gram, 0.0) for gram, weight in query_vector.items())
            for vector in self.vectors
        ]

def rrf(rankings: list[list[int]], k: int = 60) -> list[int]:
    """Reciprocal Rank Fusion: merge rankings by position, not by score."""
    fused: dict[int, float] = {}
    for one_ranking in rankings:
        for place, document in enumerate(one_ranking, start=1):
            fused[document] = fused.get(document, 0.0) + 1 / (k + place)
    return sorted(fused, key=lambda document: (-fused[document], document))

class Searcher:
    """Both retrievers over one archive, fused into a single ranking."""

    def __init__(self, records: list[Record]):
        self.records = records
        self.bm25 = BM25([tokenize(record.searchable) for record in records])
        self.ngrams = NgramIndex([char_ngrams(record.searchable) for record in records])

    def search(self, query: str, limit: int = 5) -> list[Record]:
        by_words = ranking(self.bm25.scores(tokenize(query)))
        by_grams = ranking(self.ngrams.scores(char_ngrams(query)))
        return [self.records[i] for i in rrf([by_words, by_grams])[:limit]]