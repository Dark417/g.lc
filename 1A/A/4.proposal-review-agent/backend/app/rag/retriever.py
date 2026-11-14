"""Retriever = embedder + vector store. Indexes documents and rules; searches both."""

from app.domain.models import DocumentRecord, Rule
from app.rag.chunker import Chunk
from app.rag.embedder import Embedder
from app.rag.vector_store import Hit, VectorRecord, VectorStore


def source_label(meta: dict) -> str:
    label = meta.get("title", "document")
    if meta.get("heading"):
        label += f" §{meta['heading']}"
    if meta.get("page"):
        label += f" p.{meta['page']}"
    return label


class Retriever:
    def __init__(self, embedder: Embedder, store: VectorStore) -> None:
        self.embedder = embedder
        self.store = store

    async def index_document(self, doc: DocumentRecord, chunks: list[Chunk]) -> int:
        await self.store.delete_ref("doc", doc.id)
        if not chunks:
            return 0
        vectors = await self.embedder.embed([f"{doc.title}. {c.heading}\n{c.text}" for c in chunks])
        await self.store.upsert(
            [
                VectorRecord(
                    id=f"doc:{doc.id}:{i}",
                    kind="doc",
                    ref_id=doc.id,
                    text=c.text,
                    embedding=v,
                    metadata={
                        "document_id": doc.id,
                        "title": doc.title,
                        "heading": c.heading,
                        "page": c.page,
                        "category": doc.category,
                    },
                )
                for i, (c, v) in enumerate(zip(chunks, vectors, strict=True))
            ]
        )
        return len(chunks)

    async def remove_document(self, doc_id: str) -> None:
        await self.store.delete_ref("doc", doc_id)

    async def index_rule(self, rule: Rule) -> None:
        await self.store.delete_ref("rule", rule.code)
        body = f"{rule.code} {rule.title}. {rule.statement} {rule.rationale}".strip()
        [v] = await self.embedder.embed([body])
        await self.store.upsert(
            [
                VectorRecord(
                    id=f"rule:{rule.code}",
                    kind="rule",
                    ref_id=rule.code,
                    text=body,
                    embedding=v,
                    metadata={"severity": rule.severity, "category": rule.category},
                )
            ]
        )

    async def remove_rule(self, code: str) -> None:
        await self.store.delete_ref("rule", code)

    async def _search(self, query: str, kind: str, k: int) -> list[Hit]:
        [v] = await self.embedder.embed([query], task="query")
        return await self.store.search(v, kind=kind, k=k)

    async def search_documents(self, query: str, k: int = 6) -> list[Hit]:
        return await self._search(query, "doc", k)

    async def search_rules(self, query: str, k: int = 15) -> list[Hit]:
        return await self._search(query, "rule", k)
