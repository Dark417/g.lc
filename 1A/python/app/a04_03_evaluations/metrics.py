"""Tiny local ROUGE-1 / ROUGE-L to show the mechanics (not a replacement for a tested library).

- Tokenizer: lowercase, alphanumeric words. Real ROUGE implementations add stemming and stop-word options,
  so absolute numbers differ; the mechanism is the same.
- Both return precision / recall / F1 against ONE reference: paraphrases score low (the known limit).
"""

import re
from dataclasses import dataclass

_WORD = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class Prf:
    precision: float
    recall: float
    f1: float


def tokenize(text: str) -> list[str]:
    return _WORD.findall(text.lower())


def _prf(overlap: int, cand_len: int, ref_len: int) -> Prf:
    p = overlap / cand_len if cand_len else 0.0
    r = overlap / ref_len if ref_len else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return Prf(p, r, f)


def _ngrams(tokens: list[str], n: int) -> dict[tuple[str, ...], int]:
    counts: dict[tuple[str, ...], int] = {}
    for i in range(len(tokens) - n + 1):
        g = tuple(tokens[i : i + n])
        counts[g] = counts.get(g, 0) + 1
    return counts


def rouge_n(candidate: str, reference: str, n: int = 1) -> Prf:
    """ROUGE-N: shared n-grams, each counted at most as often as it appears in the reference (clipping)."""
    c, r = _ngrams(tokenize(candidate), n), _ngrams(tokenize(reference), n)
    overlap = sum(min(cnt, r.get(g, 0)) for g, cnt in c.items())
    return _prf(overlap, sum(c.values()), sum(r.values()))


def lcs_length(a: list[str], b: list[str]) -> int:
    """Longest common subsequence via DP, O(len(a) * len(b)) time, O(len(b)) memory."""
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b, start=1):
            cur.append(prev[j - 1] + 1 if x == y else max(prev[j], cur[j - 1]))
        prev = cur
    return prev[-1]


def rouge_l(candidate: str, reference: str) -> Prf:
    """ROUGE-L: LCS length as the overlap; rewards in-order matches with gaps allowed."""
    c, r = tokenize(candidate), tokenize(reference)
    return _prf(lcs_length(c, r), len(c), len(r))
