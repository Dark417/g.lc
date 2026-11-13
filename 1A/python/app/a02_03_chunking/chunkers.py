"""Local chunkers, in the order of docs/02.03.chunking.md. Pure logic, no AWS.

Tokens are approximated by words (tokens ≈ words x tokens_per_word, ~1.3 for English, order of magnitude):
- real tokenizers differ per model (Titan, Claude, Cohere), so exact budgets need that model's tokenizer
- Bedrock KB counts tokens itself; these functions exist to show the mechanism and to unit-test chunk shapes
"""

import hashlib
import math
import re

from app.a02_03_chunking.config import get_chunking_settings
from app.a02_03_chunking.domain import Chunk, Embedder, Vector

DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " "]  # paragraph -> line -> sentence -> word
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def _words(text: str) -> list[str]:
    return text.split()


def tokens_to_words(tokens: int) -> int:
    return max(1, int(tokens / get_chunking_settings().tokens_per_word))


def approx_tokens(text: str) -> int:
    return math.ceil(len(_words(text)) * get_chunking_settings().tokens_per_word)


def _chunk_id(prefix: str, start: int, end: int, text: str) -> str:
    # Deterministic id: same content + position => same id => idempotent re-ingest (upsert, not duplicate).
    digest = hashlib.sha256(f"{start}:{end}:{text}".encode()).hexdigest()[:12]
    return f"{prefix}-{start}-{digest}"


# ================================================================ none


def no_chunking(text: str, doc_id: str = "doc") -> list[Chunk]:
    """One chunk per document. When to use: short docs (FAQ entries, tickets) or files pre-chunked upstream.

    Catch: a long document becomes one blurred vector, and may exceed the embedding model's input limit.
    """
    n = len(_words(text))
    return [Chunk(id=_chunk_id(doc_id, 0, n, text), text=text, start_word=0, end_word=n)]


# ================================================================ fixed size with overlap


def fixed_size_chunks(text: str, max_tokens: int = 300, overlap_percentage: int = 20, doc_id: str = "doc") -> list[Chunk]:
    """Sliding window of max_tokens with overlap. Bedrock FIXED_SIZE does the same with real tokens.

    When to use: uniform prose, the baseline to beat. Catch: cuts mid-sentence / mid-table; overlap (10–20%)
    softens boundary loss at the cost of storing and embedding ~overlap% more tokens.
    """
    if not 0 <= overlap_percentage < 100:
        raise ValueError("overlap_percentage must be in [0, 100)")
    words = _words(text)
    size = tokens_to_words(max_tokens)
    step = max(1, size - size * overlap_percentage // 100)
    chunks: list[Chunk] = []
    for start in range(0, len(words), step):
        end = min(start + size, len(words))
        body = " ".join(words[start:end])
        chunks.append(Chunk(id=_chunk_id(doc_id, start, end, body), text=body, start_word=start, end_word=end))
        if end == len(words):
            break
    return chunks


# ================================================================ recursive splitter on separators


def recursive_split(text: str, max_tokens: int = 300, separators: list[str] | None = None) -> list[str]:
    """Split on the coarsest separator that keeps pieces under budget; recurse with finer ones for oversize pieces.

    When to use: structured text (Markdown, code, docs with paragraphs) where boundaries carry meaning.
    Catch: piece sizes vary a lot; tiny pieces are merged greedily up to the budget.
    """
    seps = DEFAULT_SEPARATORS if separators is None else separators
    if approx_tokens(text) <= max_tokens:
        return [text] if text.strip() else []
    if not seps:
        # No separator left: hard cut by words.
        return [c.text for c in fixed_size_chunks(text, max_tokens, 0)]
    sep, finer = seps[0], seps[1:]
    pieces = [p for p in text.split(sep) if p.strip()]
    out: list[str] = []
    current = ""
    for piece in pieces:
        candidate = f"{current}{sep}{piece}" if current else piece
        if approx_tokens(candidate) <= max_tokens:
            current = candidate
            continue
        if current:
            out.append(current)
        if approx_tokens(piece) > max_tokens:
            out.extend(recursive_split(piece, max_tokens, finer))
            current = ""
        else:
            current = piece
    if current:
        out.append(current)
    return out


# ================================================================ hierarchical (parent / child)


def hierarchical_chunks(
    text: str,
    parent_max_tokens: int = 1500,
    child_max_tokens: int = 300,
    overlap_tokens: int = 60,
    doc_id: str = "doc",
) -> tuple[list[Chunk], list[Chunk]]:
    """Two levels: large parents for context, small children for precise matching. Children link to parents.

    Bedrock HIERARCHICAL: only children are embedded; at query time matching children are replaced by their
    parent ⇒ the model sees wide context. Catch: several children of one parent collapse into one result, so
    Retrieve can return fewer than numberOfResults.
    """
    words = _words(text)
    p_size, c_size, ov = tokens_to_words(parent_max_tokens), tokens_to_words(child_max_tokens), tokens_to_words(overlap_tokens)
    if ov >= c_size:
        raise ValueError("overlap must be smaller than the child size")
    parents: list[Chunk] = []
    children: list[Chunk] = []
    p_start = 0
    while p_start < len(words):
        p_end = min(p_start + p_size, len(words))
        p_text = " ".join(words[p_start:p_end])
        parent = Chunk(_chunk_id(doc_id, p_start, p_end, p_text), p_text, p_start, p_end, level="parent")
        parents.append(parent)
        c_start = p_start
        while c_start < p_end:
            c_end = min(c_start + c_size, p_end)
            c_text = " ".join(words[c_start:c_end])
            children.append(Chunk(_chunk_id(doc_id, c_start, c_end, c_text), c_text, c_start, c_end, "child", parent.id))
            if c_end == p_end:
                break
            c_start = c_end - ov
        if p_end == len(words):
            break
        p_start = p_end - ov
    return parents, children


def expand_to_parents(child_hits: list[Chunk], parents: list[Chunk]) -> list[Chunk]:
    """Retrieve child, return parent: dedupe by parent id, keep the best-ranked child's order."""
    by_id = {p.id: p for p in parents}
    seen: set[str] = set()
    out: list[Chunk] = []
    for c in child_hits:
        if c.parent_id and c.parent_id not in seen and c.parent_id in by_id:
            seen.add(c.parent_id)
            out.append(by_id[c.parent_id])
    return out


# ================================================================ semantic (embedding-distance breakpoints)


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_END.split(text) if s.strip()]


def percentile(values: list[float], p: float) -> float:
    """Nearest-rank percentile (p in 0–100)."""
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(0, min(len(ordered) - 1, math.ceil(p / 100 * len(ordered)) - 1))
    return ordered[rank]


def _cosine_distance(a: Vector, b: Vector) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return 1.0 - (dot / (na * nb) if na and nb else 0.0)


def semantic_chunks(
    text: str,
    embedder: Embedder,
    buffer_size: int = 0,
    breakpoint_percentile_threshold: int = 95,
    max_tokens: int = 300,
    doc_id: str = "doc",
) -> list[Chunk]:
    """Break where meaning shifts: embed each sentence (with buffer_size neighbours on each side), compute the
    distance between consecutive windows, and cut where it exceeds the given percentile of all distances.

    When to use: documents whose topics change without headings (transcripts, long emails).
    Catch: one embedding call per sentence at ingestion ⇒ extra cost; max_tokens still caps chunk size.
    """
    sentences = split_sentences(text)
    if len(sentences) <= 1:
        return no_chunking(text, doc_id)
    windows = [
        " ".join(sentences[max(0, i - buffer_size) : i + buffer_size + 1]) for i in range(len(sentences))
    ]
    vectors = [embedder.embed(w) for w in windows]
    distances = [_cosine_distance(vectors[i], vectors[i + 1]) for i in range(len(vectors) - 1)]
    threshold = percentile(distances, breakpoint_percentile_threshold)

    chunks: list[Chunk] = []
    group: list[str] = []
    word_pos = 0
    group_start = 0
    for i, sentence in enumerate(sentences):
        candidate = group + [sentence]
        if group and approx_tokens(" ".join(candidate)) > max_tokens:
            body = " ".join(group)  # size cap reached before a semantic break
            chunks.append(Chunk(_chunk_id(doc_id, group_start, word_pos, body), body, group_start, word_pos))
            group, group_start = [sentence], word_pos
        else:
            group = candidate
        word_pos += len(_words(sentence))
        if i < len(distances) and distances[i] > threshold:
            body = " ".join(group)
            chunks.append(Chunk(_chunk_id(doc_id, group_start, word_pos, body), body, group_start, word_pos))
            group, group_start = [], word_pos
    if group:
        body = " ".join(group)
        chunks.append(Chunk(_chunk_id(doc_id, group_start, word_pos, body), body, group_start, word_pos))
    return chunks


class HashingEmbedder:
    """Fake Embedder for tests and the demo API: hashed bag of words, normalized. Deterministic, no AWS.

    It captures word overlap, not meaning: good enough to see breakpoints between unrelated topics.
    """

    def __init__(self, dims: int = 256) -> None:
        self.dims = dims

    def embed(self, text: str) -> Vector:
        v = [0.0] * self.dims
        for w in re.findall(r"[a-z0-9]+", text.lower()):
            v[int(hashlib.md5(w.encode()).hexdigest(), 16) % self.dims] += 1.0
        n = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / n for x in v]

