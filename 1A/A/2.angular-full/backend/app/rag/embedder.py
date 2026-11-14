"""Text -> vector. Two implementations behind one Protocol.

The retriever only needs `embed(list[str]) -> list[list[float]]`. Which one runs is decided by
Settings.embedder in app/rag/factory.py.
"""

import hashlib
import math
import re
from typing import Protocol

Vector = list[float]


class Embedder(Protocol):
    dim: int

    def embed(self, texts: list[str]) -> list[Vector]: ...


class HashingEmbedder:
    """ILLUSTRATION: feature-hashing bag of words. Deterministic, offline, no deps.

    Captures lexical overlap only (no synonyms, no semantics). Good enough to demonstrate the
    RAG pipeline end to end and to make tests hermetic. Not good enough for real retrieval.
    """

    def __init__(self, dim: int = 512) -> None:
        self.dim = dim

    @staticmethod
    def _tokens(text: str) -> list[str]:
        return re.findall(r"[a-z0-9]+", text.lower())

    def embed(self, texts: list[str]) -> list[Vector]:
        out: list[Vector] = []
        for text in texts:
            v = [0.0] * self.dim
            for tok in self._tokens(text):
                h = int(hashlib.md5(tok.encode(), usedforsecurity=False).hexdigest(), 16)
                v[h % self.dim] += 1.0 if (h >> 1) % 2 else -1.0  # signed hashing trick
            norm = math.sqrt(sum(x * x for x in v)) or 1.0
            out.append([x / norm for x in v])
        return out


class GeminiEmbedder:
    """PRODUCTION: Gemini embedding model via google-genai (already a dependency of ADK).

    Real code; select with EMBEDDER=gemini and a GOOGLE_API_KEY. Batch, cache, and rate-limit
    in front of this before indexing anything large.
    """

    def __init__(self, model: str = "gemini-embedding-001", dim: int = 768) -> None:
        from google import genai

        self._client = genai.Client()  # reads GOOGLE_API_KEY
        self._model = model
        self.dim = dim

    def embed(self, texts: list[str]) -> list[Vector]:
        from google.genai import types

        res = self._client.models.embed_content(
            model=self._model,
            contents=texts,
            config=types.EmbedContentConfig(output_dimensionality=self.dim),
        )
        return [list(e.values) for e in res.embeddings]
