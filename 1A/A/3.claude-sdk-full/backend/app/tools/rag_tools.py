from collections.abc import Callable

from app.rag.retriever import Retriever


def build_rag_tool(retriever: Retriever, top_k: int = 3) -> Callable:
    def search_knowledge_base(query: str) -> dict:
        """Search the company knowledge base (policies, shipping, product care).

        Use this before answering any question about store policies, returns, shipping, warranty,
        or product care. Quote or paraphrase the passages and cite the source file.

        Args:
            query: A short natural-language search query.
        """
        hits = retriever.query(query, k=top_k)
        return {
            "status": "ok",
            "passages": [
                {"source": h.metadata.get("source"), "score": round(h.score, 3), "text": h.text}
                for h in hits
            ],
        }

    return search_knowledge_base
