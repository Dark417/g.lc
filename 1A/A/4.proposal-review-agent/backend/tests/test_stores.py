"""Storage adapters. The integration tests run against real Postgres+pgvector and MongoDB when
TEST_PG_URL / TEST_MONGO_URL are set (CI provides both as service containers)."""

import uuid

import pytest
from google.adk.events import Event
from google.adk.sessions import DatabaseSessionService
from google.genai import types

from app.domain.models import DocumentRecord, RuleIn
from app.rag.embedder import HashingEmbedder
from app.rag.vector_store import PgVectorStore, VectorRecord
from app.services.memory import SqlMemoryService
from app.storage.blobs import LocalBlobStore
from app.storage.documents_repo import JsonFileDocumentRepository, MongoDocumentRepository
from app.storage.rules_repo import SqlRuleRepository
from app.storage.sql import init_schema, make_engine, make_sessionmaker
from tests.conftest import integration_url


def _doc(i: int, category: str = "privacy") -> DocumentRecord:
    return DocumentRecord(
        id=f"doc_{i}",
        title=f"Doc {i}",
        filename=f"d{i}.md",
        format="md",
        mime_type="text/markdown",
        size_bytes=1,
        sha256=f"sha{i}",
        category=category,
        uploaded_by="t",
        outline=["A"],
    )


async def _exercise_doc_repo(repo) -> None:
    await repo.init()
    await repo.upsert(_doc(1))
    await repo.upsert(_doc(2, "marketing"))
    got = await repo.get("doc_1")
    assert got.title == "Doc 1" and got.outline == ["A"]
    assert (await repo.get_by_sha("sha2")).id == "doc_2"
    assert [d.id for d in await repo.list(category="marketing")] == ["doc_2"]
    got.summary = "updated"
    await repo.upsert(got)
    assert (await repo.get("doc_1")).summary == "updated"
    await repo.delete("doc_1")
    assert await repo.get("doc_1") is None


async def test_file_document_repo(tmp_path):
    await _exercise_doc_repo(JsonFileDocumentRepository(str(tmp_path / "d.json")))


async def test_local_blobs(tmp_path):
    b = LocalBlobStore(str(tmp_path))
    uri = await b.put("documents/x/a.txt", b"hi")
    assert uri.startswith("file://") and await b.get("documents/x/a.txt") == b"hi"
    assert await b.list("documents") == ["documents/x/a.txt"]
    await b.delete_prefix("documents/x")
    assert await b.list("documents") == []
    with pytest.raises(ValueError):
        await b.put("../escape.txt", b"x")


async def test_sql_memory_is_scoped_per_user(container):
    mem = container.memory
    s = await container.sessions.create_session(app_name="compliance_agent", user_id="alice")
    for author, text in [
        ("user", "We are planning the EU launch of Product Falcon"),
        ("compliance_agent", "Noted."),
    ]:
        await container.sessions.append_event(
            s,
            Event(author=author, content=types.Content(role="user", parts=[types.Part(text=text)])),
        )
    s = await container.sessions.get_session(
        app_name="compliance_agent", user_id="alice", session_id=s.id
    )
    await mem.add_session_to_memory(s)
    await mem.add_session_to_memory(s)  # idempotent by event id

    res = await mem.search_memory(
        app_name="compliance_agent", user_id="alice", query="EU launch Falcon"
    )
    assert res.memories and "Falcon" in res.memories[0].content.parts[0].text
    assert len(res.memories) == 1  # "Noted." is below the similarity floor
    other = await mem.search_memory(
        app_name="compliance_agent", user_id="bob", query="EU launch Falcon"
    )
    assert other.memories == []

    await mem.delete_session(app_name="compliance_agent", user_id="alice", session_id=s.id)
    assert (
        await mem.search_memory(app_name="compliance_agent", user_id="alice", query="Falcon")
    ).memories == []


# ------------------------------------------------------------------ integration (real servers)
@pytest.mark.integration
async def test_mongo_document_repo():
    url = integration_url("TEST_MONGO_URL")
    repo = MongoDocumentRepository(url, f"test_{uuid.uuid4().hex[:8]}")
    try:
        await _exercise_doc_repo(repo)
    finally:
        await repo._client.drop_database(repo._col.database.name)
        await repo.close()


@pytest.fixture
async def pg_engine():
    engine = make_engine(integration_url("TEST_PG_URL"))
    yield engine
    await engine.dispose()


@pytest.mark.integration
async def test_pgvector_store(pg_engine):
    emb = HashingEmbedder(64)
    store = PgVectorStore(pg_engine, 64)
    store.TABLE = f"chunk_embeddings_{uuid.uuid4().hex[:8]}"
    await store.init()
    texts = {
        "a": "parental consent for children",
        "b": "encrypt data at rest",
        "c": "discount approval by CFO",
    }
    vecs = await emb.embed(list(texts.values()))
    await store.upsert(
        [
            VectorRecord(
                id=f"doc:{k}", kind="doc", ref_id=k, text=t, embedding=v, metadata={"title": k}
            )
            for (k, t), v in zip(texts.items(), vecs, strict=True)
        ]
    )
    [q] = await emb.embed(["children parental consent"], task="query")
    hits = await store.search(q, kind="doc", k=2)
    assert hits[0].ref_id == "a" and hits[0].metadata == {"title": "a"} and 0 < hits[0].score <= 1
    await store.upsert(
        [VectorRecord(id="doc:a", kind="doc", ref_id="a", text="changed", embedding=vecs[0])]
    )
    assert await store.count("doc") == 3
    await store.delete_ref("doc", "a")
    assert await store.count("doc") == 2
    async with pg_engine.begin() as conn:
        from sqlalchemy import text

        await conn.execute(text(f"DROP TABLE {store.TABLE}"))


@pytest.mark.integration
async def test_postgres_rules_and_adk_sessions(pg_engine):
    await init_schema(pg_engine)
    repo = SqlRuleRepository(make_sessionmaker(pg_engine))
    prefix = f"T{uuid.uuid4().hex[:4].upper()}"
    r = await repo.create(
        RuleIn(
            code=f"{prefix}-001",
            title="Pg rule title",
            statement="Must work.",
            severity="hard",
            category="tests",
        ),
        "ci",
    )
    assert (await repo.get(r.code)).version == 1

    sessions = DatabaseSessionService(db_url=integration_url("TEST_PG_URL"))
    s = await sessions.create_session(
        app_name="compliance_agent", user_id="pg-user", state={"title": "hello"}
    )
    listed = await sessions.list_sessions(app_name="compliance_agent", user_id="pg-user")
    assert s.id in {x.id for x in listed.sessions}
    await sessions.delete_session(app_name="compliance_agent", user_id="pg-user", session_id=s.id)


@pytest.mark.integration
async def test_memory_on_postgres(pg_engine):
    await init_schema(pg_engine)
    mem = SqlMemoryService(make_sessionmaker(pg_engine), HashingEmbedder(64), min_score=0.0)
    res = await mem.search_memory(app_name="x", user_id=f"nobody-{uuid.uuid4().hex}", query="q")
    assert res.memories == []
