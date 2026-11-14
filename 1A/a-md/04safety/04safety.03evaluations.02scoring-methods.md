# 04safety.03evaluations.02scoring-methods Scoring Methods and Automatic Metrics

> Automatic metrics vs Large Language Model (LLM)-as-a-judge vs humans, and how Recall-Oriented Understudy for Gisting Evaluation (ROUGE), Bilingual Evaluation Understudy (BLEU), and BERTScore actually compute.

## Index

- [1. Three Ways to Score](#1-three-ways-to-score)
- [2. ROUGE-1](#2-rouge-1)
- [3. ROUGE-L](#3-rouge-l)
- [4. BLEU](#4-bleu)
- [5. BERTScore](#5-bertscore)
- [6. Limits of Automatic Metrics](#6-limits-of-automatic-metrics)

Back to [00index](04safety.03evaluations.00index.md).
Judge details: [05llm-judge](04safety.03evaluations.05llm-judge.md).

## 1. Three Ways to Score

Each method trades cost and speed against nuance.

| Method | Mechanism | Strength | Weakness | Cost (order of magnitude) |
|---|---|---|---|---|
| Automatic metrics | n-gram overlap, embedding similarity, exact match, classifiers | deterministic, cheap, fast | needs a reference; punishes paraphrase | ~free |
| LLM-as-a-judge | rubric prompt → score + reason from a judge model | scales; handles paraphrase; any criterion | bias; judge cost; drift with judge version | judge tokens per item |
| Human | raters on a work team | ground truth; nuance | slow; costly; inter-rater disagreement | per item per rater |

- Default stack
  - Automatic for regression smoke tests
  - Judge for most quality dimensions
  - Humans on a small sample to calibrate the judge

## 2. ROUGE-1

Recall-oriented; used for summarization.

- Count unigrams shared by candidate and reference
  - clipped by counts: each counted at most as often as it appears in the reference
- Precision = overlap / candidate words
- Recall = overlap / reference words
- Report F1

```python
# app/service/_04safety_03evaluations/metrics.py
def _prf(overlap: int, cand_len: int, ref_len: int) -> Prf:
    p = overlap / cand_len if cand_len else 0.0
    r = overlap / ref_len if ref_len else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return Prf(p, r, f)


def rouge_n(candidate: str, reference: str, n: int = 1) -> Prf:
    """ROUGE-N: shared n-grams, each counted at most as often as it appears in the reference (clipping)."""
    c, r = _ngrams(tokenize(candidate), n), _ngrams(tokenize(reference), n)
    overlap = sum(min(cnt, r.get(g, 0)) for g, cnt in c.items())  # clipped overlap
    return _prf(overlap, sum(c.values()), sum(r.values()))
```

- Catch
  - The tokenizer is lowercase alphanumeric words only
  - real ROUGE adds stemming and stop-word options, so absolute numbers differ
  - the mechanism is the same; not a replacement for a tested library

## 3. ROUGE-L

Longest common subsequence: in order, gaps allowed.

- Longest Common Subsequence (LCS) between candidate and reference is the overlap
- Rewards correct word order without needing contiguous n-grams

```python
# app/service/_04safety_03evaluations/metrics.py
def lcs_length(a: list[str], b: list[str]) -> int:
    """Longest common subsequence via DP, O(len(a) * len(b)) time, O(len(b)) memory."""
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b, start=1):
            cur.append(prev[j - 1] + 1 if x == y else max(prev[j], cur[j - 1]))
        prev = cur  # keep only one previous row
    return prev[-1]


def rouge_l(candidate: str, reference: str) -> Prf:
    c, r = tokenize(candidate), tokenize(reference)
    return _prf(lcs_length(c, r), len(c), len(r))
```

## 4. BLEU

Precision-oriented; used for translation.

- Geometric mean of 1–4-gram precisions
- × brevity penalty for short candidates
- Corpus-level metric
  - noisy per sentence
- Described, not implemented in the repo

## 5. BERTScore

Embedding similarity instead of exact word match.

→ Embed every token of both texts with a BERT-family model.  
→ Greedy-match tokens by cosine similarity.  
→ Average into precision/recall/F1.

- Handles synonyms
- Still needs a reference
- Depends on the embedding model
- Described, not implemented in the repo

## 6. Limits of Automatic Metrics

- All four measure similarity to one reference
  - not correctness or groundedness
  - paraphrases score low; wrong answers with shared words score high
- Bedrock's automatic "Accuracy" uses a task-specific metric
  - e.g. BERTScore for summarization, F1 for Question Answering (QA)
  - check the metric table in the docs
- Fine for constrained outputs (extraction, short summaries)
  - and as cheap regression signals
