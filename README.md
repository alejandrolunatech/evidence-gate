# Evidence gate

Code for the joint review, Option A (own project): Bouwarchief AI.

## What this is

This repo is a small, hand-written part of Bouwarchief AI, the application I
will show live during the interview. It answers a question about a building
archive in Dutch, English or Spanish by citing one archive page, or it refuses
when the archive does not say.

The real application works on scanned building drawings from 1975 to 1977
(287 PDFs, 339 pages, many handwritten, no text layer). That archive is
private, so this repo runs on synthetic data: `data/archive.jsonl` holds 23
page records of a made-up housing complex, "Zuiderhof", in the same format
the real pipeline produces after reading the scans.

## Run it

## Run it

Python 3.10 or newer, standard library only. No install, no network. From this folder:

```
python3 -m evidence_gate "How long are the piles under block 3?"
```

The same question type in Dutch and Spanish:

```
python3 -m evidence_gate "Hoe hoog is de kruipruimte?"
python3 -m evidence_gate "Is de spouw geïsoleerd?"
python3 -m evidence_gate "¿Qué longitud tienen los pilotes del bloque 3?"
```

Two questions the gate refuses, for different reasons:

```
python3 -m evidence_gate "Wie woont er op nummer 12?"
python3 -m evidence_gate "Is there asbestos in the roof boarding?"
```

The first has low coverage: no page is about who lives where. For the second,
the best page is a note saying the archive holds no asbestos inventory, so the
honest answer is that the archive does not say.

Tests and evaluation:

```
python3 -m unittest discover -s tests -v
python3 -m evidence_gate.evaluate
```n3 -m evidence_gate.evaluate
```

## How to read it

Start with `evidence_gate/gate.py`. `EvidenceGate.ask()` is the whole flow.

| File | What it does |
| --- | --- |
| `gate.py` | Picks the candidate page that covers most of the question, then answers with a citation or refuses (coverage below 0.5, or the best page is an "archive lacks this" note). |
| `glossary.py` | 13 building concepts in three languages, so "piles", "palen" and "pilotes" count as the same thing. |
| `search.py` | Two deterministic retrievers, BM25 on words and TF-IDF on character n-grams, fused with Reciprocal Rank Fusion. |
| `text.py` | Normalizing, tokenizing and character n-grams. |
| `records.py` | Loads and validates the page records. |
| `evaluate.py` | Runs the 22 golden questions and counts right pages, wrong pages and refusals. |

Every module has unit tests in `tests/` (26 in total), including the error
paths and the refusal cases.

## Where it fits in the real application

This is the deterministic half: lexical search and the refusal gate. The
production system adds three model-backed components that are not in this repo:

- Dense retrieval: Amazon Titan embeddings stored in Amazon S3 Vectors, fused with the lexical search.
- Amazon Rerank on Bedrock, after the fusion.
- Claude Haiku 4.5 on Bedrock, which writes the answer from the top five pages. Its citations are checked against those pages.

It also has a page classifier, a DiT vision model I fine-tuned in Google
Colab with PyTorch, which sorts pages by drawing type. Macro F1 went from
0.826 with a logistic-regression baseline to 0.902.

On the real archive (48 golden questions),
hit@1 was 60.5% offline, 78.9% with lexical search plus the reranker, and
81.6% with hybrid search plus the reranker.

## Results of this repo

From `python3 -m evidence_gate.evaluate`, run on 12 November 2026:

| | Count |
| --- | --- |
| Answerable questions | 16 |
| Right page cited | 9 |
| Wrong page cited | 2 |
| Refused (a miss) | 5 |
| Unanswerable questions | 6 |
| Refused correctly | 6 |
| Answered | 0 |

In all seven misses the right page was among the search candidates, so the
weak part is the coverage measure, not retrieval:

- Words that are not in the archive ("who", "made", "get") weigh the maximum, so filler words push a good page below the threshold.
- "a" is a stopword, so "type A" loses its letter and ties with "type B".
- A tie in coverage is broken by search order instead of being refused.

I did not fix these against 22 questions, because that would be tuning on the test set.

## What I would change before production

- Give unknown filler words less weight, and keep one-letter identifiers.
- Refuse or show both pages on a tie.
- Return several citations instead of one.
- Calibrate the 0.5 threshold on a larger set of real questions from the client.

## Data

23 page records and 22 questions, all synthetic, generated with AI and
reviewed by me. Limits: the set is small, and the questions were written by
someone who knew the records, so real questions will be harder.
