from app.config import Settings
from app.rag.chunker import chunk_text
from app.rag.embedder import HashingEmbedder
from app.rag.factory import build_retriever
from app.rag.retriever import Document, Retriever
from app.rag.vector_store import InMemoryVectorStore
from app.tools.rag_tools import build_rag_tool


def test_chunker_respects_budget_and_overlap():
    text = "\n\n".join(f"paragraph {i} " * 10 for i in range(8))
    chunks = chunk_text(text, max_chars=300, overlap_chars=40)
    assert len(chunks) > 1 and all(len(c) <= 300 for c in chunks)


def test_hashing_embedder_is_deterministic_and_normalised():
    e = HashingEmbedder(dim=64)
    [a], [b] = e.embed(["down sleeping bag"]), e.embed(["down sleeping bag"])
    assert a == b and abs(sum(x * x for x in a) - 1.0) < 1e-6


def test_retriever_finds_relevant_doc():
    r = Retriever(HashingEmbedder(), InMemoryVectorStore())
    r.index(
        [
            Document(
                id="ship",
                text="Orders ship within 1 business day. Express shipping costs 14.90.",
                source="s.md",
            ),
            Document(
                id="wash",
                text="Wash down sleeping bags with down detergent, tumble dry low.",
                source="w.md",
            ),
        ]
    )
    assert r.query("how do I wash my sleeping bag")[0].id.startswith("wash")
    assert r.query("express shipping cost")[0].id.startswith("ship")


def test_factory_indexes_real_knowledge_dir_and_tool_formats_hits():
    settings = Settings(knowledge_dir="data/knowledge", _env_file=None)
    retriever = build_retriever(settings)
    search = build_rag_tool(retriever, top_k=2)
    res = search("return an unused item for a refund")
    assert res["status"] == "ok" and len(res["passages"]) == 2
    assert res["passages"][0]["source"] == "returns-policy.md"
