"""RAG and long-term memory tools. The backend comes from the run's provider profile."""

from app.core.scope import current_scope


async def search_docs(query: str) -> dict:
    """Search the engineering knowledge base (notes on agent frameworks and cloud agent services).

    Always cite the `source` of passages you use.

    Args:
        query: What to look for, in natural language.
    """
    scope = current_scope()
    retriever = scope.provider.retriever
    passages = await retriever.search(query, k=4)
    return {
        "backend": retriever.name,
        "passages": [{**p.as_dict(), "text": p.text[:1200]} for p in passages],
    }


async def remember(fact: str) -> dict:
    """Save a durable fact about the user or their project for future conversations.

    Args:
        fact: One self-contained sentence, e.g. "User deploys to us-east-1".
    """
    scope = current_scope()
    memory = scope.provider.memory
    ref = await memory.add(scope.user_id, fact, scope.session_id)
    return {"status": "saved", "backend": memory.name, "ref": ref}


async def recall(query: str) -> dict:
    """Look up facts remembered about the user in earlier conversations (any framework).

    Args:
        query: What you want to know, e.g. "which AWS region".
    """
    scope = current_scope()
    memory = scope.provider.memory
    records = await memory.search(scope.user_id, query, k=5)
    return {"backend": memory.name, "memories": [r.as_dict() for r in records]}
