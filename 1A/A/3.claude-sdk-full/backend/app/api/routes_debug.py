"""Peek at the RAG index without going through the model. Handy while tuning chunking."""

from fastapi import APIRouter, Query, Request

router = APIRouter(prefix="/api/v1/debug", tags=["debug"])


@router.get("/rag/search")
async def rag_search(request: Request, q: str = Query(min_length=1), k: int = 3) -> dict:
    hits = request.app.state.retriever.query(q, k=k)
    return {
        "query": q,
        "hits": [
            {"id": h.id, "score": round(h.score, 3), "text": h.text, **h.metadata} for h in hits
        ],
    }
