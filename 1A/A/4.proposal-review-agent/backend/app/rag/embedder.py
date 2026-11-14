"""Text -> unit vectors. Selected by EMBEDDER in app/container.py."""

import hashlib
import math
import re
from typing import Literal, Protocol

Vector = list[float]
Task = Literal["document", "query"]


class Embedder(Protocol):
    dim: int

    async def embed(self, texts: list[str], *, task: Task = "document") -> list[Vector]: ...


def normalize(v: Vector) -> Vector:
    norm = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / norm for x in v]


class HashingEmbedder:
    """ILLUSTRATION: signed feature hashing over word unigrams + bigrams. Offline, deterministic.

    Lexical only: "refund" and "money back" don't match. Good for tests and no-key runs.
    """

    def __init__(self, dim: int = 768) -> None:
        self.dim = dim

    def _one(self, text: str) -> Vector:
        words = re.findall(r"[a-z0-9]+", text.lower())
        v = [0.0] * self.dim
        for tok in words + [f"{a}_{b}" for a, b in zip(words, words[1:], strict=False)]:
            h = int(hashlib.md5(tok.encode(), usedforsecurity=False).hexdigest(), 16)
            v[h % self.dim] += 1.0 if (h >> 1) % 2 else -1.0
        return normalize(v)

    async def embed(self, texts: list[str], *, task: Task = "document") -> list[Vector]:
        return [self._one(t) for t in texts]


class GeminiEmbedder:
    """PRODUCTION: gemini-embedding-001 through google-genai. Works with a Gemini API key or with
    Vertex AI (GOOGLE_GENAI_USE_VERTEXAI=TRUE + ADC). Vectors are re-normalised because truncated
    output dimensions (768) are not unit length."""

    BATCH = 100

    def __init__(self, model: str, dim: int) -> None:
        self._model, self.dim = model, dim
        self._client = None

    def _c(self):
        if self._client is None:
            from google import genai

            self._client = genai.Client()  # credentials from env (see Settings.export_model_env)
        return self._client

    async def embed(self, texts: list[str], *, task: Task = "document") -> list[Vector]:
        from google.genai import types

        task_type = "RETRIEVAL_QUERY" if task == "query" else "RETRIEVAL_DOCUMENT"
        out: list[Vector] = []
        for i in range(0, len(texts), self.BATCH):
            res = await self._c().aio.models.embed_content(
                model=self._model,
                contents=texts[i : i + self.BATCH],
                config=types.EmbedContentConfig(
                    output_dimensionality=self.dim, task_type=task_type
                ),
            )
            out.extend(normalize(list(e.values)) for e in res.embeddings)
        return out
