"""Retriever = embedder + vector store + chunker. This is the whole RAG "R"."""

from dataclasses import dataclass
from pathlib import Path

from app.rag.chunker import chunk_text
from app.rag.embedder import Embedder
from app.rag.vector_store import Hit, VectorStore


@dataclass
class Document:
    id: str
    text: str
    source: str


def load_markdown_dir(directory: str) -> list[Document]:
    docs = []
    for path in sorted(Path(directory).glob("*.md")):
        docs.append(Document(id=path.stem, text=path.read_text(encoding="utf-8"), source=path.name))
    return docs


class Retriever:
    def __init__(self, embedder: Embedder, store: VectorStore) -> None:
        self._embedder = embedder
        self._store = store

    def index(self, docs: list[Document]) -> int:
        ids, texts, metas = [], [], []
        for doc in docs:
            for n, chunk in enumerate(chunk_text(doc.text)):
                ids.append(f"{doc.id}#{n}")
                texts.append(chunk)
                metas.append({"source": doc.source, "chunk": n})
        if texts:
            self._store.add(ids, self._embedder.embed(texts), texts, metas)
        return len(texts)

    def query(self, text: str, k: int = 3) -> list[Hit]:
        [vector] = self._embedder.embed([text])
        return self._store.search(vector, k)
