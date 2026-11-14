"""Local RAG over data/corpus/*.md.

# ILLUSTRATION: hashing embedder + in-memory cosine search. Deterministic, offline, no deps.
# PRODUCTION: a managed index. In this project that is the provider branch itself:
#   bedrock -> BedrockKbRetriever (app/rag/bedrock_kb.py)
#   vertex  -> VertexRagRetriever (app/rag/vertex_rag.py)
"""

import hashlib
import math
import re
from pathlib import Path

from app.rag.base import Passage

_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = set("a an and are as at be by for from how in is it of on or that the this to with".split())


def _tokens(text: str) -> list[str]:
    return [t for t in _TOKEN.findall(text.lower()) if t not in _STOP]


class HashingEmbedder:
    """Bag of words + bigrams hashed into a fixed-size vector (the "hashing trick")."""

    def __init__(self, dim: int = 512):
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        toks = _tokens(text)
        for feat in toks + [f"{a}_{b}" for a, b in zip(toks, toks[1:], strict=False)]:
            h = int.from_bytes(hashlib.blake2b(feat.encode(), digest_size=8).digest(), "big")
            vec[h % self.dim] += 1.0 if (h >> 63) & 1 else -1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]


def chunk_markdown(path: Path) -> list[tuple[str, str]]:
    """Split a markdown file by `## ` headings -> [(source, text)]."""
    text = path.read_text(encoding="utf-8")
    title = next((ln[2:].strip() for ln in text.splitlines() if ln.startswith("# ")), path.stem)
    chunks: list[tuple[str, str]] = []
    for part in re.split(r"\n(?=## )", text):
        part = part.strip()
        if not part:
            continue
        heading = part.splitlines()[0].lstrip("# ").strip()
        source = path.name if heading == title else f"{path.name}#{heading}"
        body = part if part.startswith("# ") else f"{title} — {part}"
        chunks.append((source, body))
    return chunks


class LocalRetriever:
    name = "local"

    def __init__(self, corpus_dir: Path, embedder: HashingEmbedder | None = None):
        self.embedder = embedder or HashingEmbedder()
        self._items: list[tuple[str, str, list[float]]] = []
        for path in sorted(Path(corpus_dir).glob("*.md")):
            for source, text in chunk_markdown(path):
                self._items.append((source, text, self.embedder.embed(text)))

    def __len__(self) -> int:
        return len(self._items)

    async def search(self, query: str, k: int = 4) -> list[Passage]:
        q = self.embedder.embed(query)
        scored = [
            (sum(a * b for a, b in zip(q, vec, strict=True)), source, text)
            for source, text, vec in self._items
        ]
        scored.sort(reverse=True)
        return [Passage(source=s, text=t, score=round(sc, 4)) for sc, s, t in scored[:k] if sc > 0]
