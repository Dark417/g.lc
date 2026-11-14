import pytest

from app.domain.verdicts import VerdictLabel
from app.rag.parsers import UnsupportedFormat
from tests.conftest import SAMPLES, findings_from, seed_rules

DOCS = SAMPLES / "documents"


async def test_ingest_pipeline_end_to_end(container, fake_llm):
    data = (DOCS / "data-privacy-standard.html").read_bytes()
    doc = await container.ingestion.ingest(data, "data-privacy-standard.html", actor="admin")
    assert doc.status == "ready" and doc.title == "Data Privacy Standard"
    assert doc.summary == "Test summary." and doc.category == "testing"  # suggested by summary
    assert doc.chunk_count > 0 and "3. Children" in doc.outline
    assert (await container.docs.get(doc.id)).status == "ready"
    assert "verifiable parental consent" in await container.ingestion.text_of(doc)
    assert await container.ingestion.original_of(doc) == data

    hits = await container.retriever.search_documents("parental consent for kids", k=2)
    assert hits[0].ref_id == doc.id and hits[0].metadata["heading"] == "3. Children"


async def test_ingest_is_idempotent_by_hash(container, fake_llm):
    data = (DOCS / "product-launch-policy.md").read_bytes()
    a = await container.ingestion.ingest(data, "a.md", actor="admin")
    calls = len(fake_llm.calls)
    b = await container.ingestion.ingest(data, "renamed.md", actor="admin")
    assert a.id == b.id and len(fake_llm.calls) == calls  # no re-summary, no re-index
    assert len(await container.docs.list()) == 1


async def test_failed_ingest_is_recorded(container):
    with pytest.raises(UnsupportedFormat):
        await container.ingestion.ingest(b"binary", "sheet.xlsx", actor="admin")
    [rec] = await container.docs.list()
    assert rec.status == "failed" and "unsupported" in rec.error


async def test_find_and_delete(container):
    doc = await container.ingestion.ingest(
        (DOCS / "product-launch-policy.md").read_bytes(), "p.md", actor="a"
    )
    assert (await container.ingestion.find("launch policy")).id == doc.id
    assert (await container.ingestion.find(doc.id)).id == doc.id
    assert await container.ingestion.delete(doc.id)
    assert await container.docs.get(doc.id) is None and await container.vectors.count("doc") == 0


async def test_assessment_hard_violation_blocks_and_persists(container, fake_llm):
    await seed_rules(container)
    await container.ingestion.ingest(
        (DOCS / "data-privacy-standard.html").read_bytes(), "d.html", actor="a"
    )
    fake_llm.findings = findings_from(
        {"PRIV-003": "violated", "MKT-002": "violated", "SEC-001": "satisfied"}
    )

    v = await container.assessment.assess(
        "Email kids without asking parents", user_id="alice@example.com"
    )

    assert v.verdict == VerdictLabel.NON_COMPLIANT
    assert v.blocking == ["PRIV-003: Verifiable parental consent for children under 13"]
    assert v.conditions and v.conditions[0].startswith("MKT-002")
    assert v.rules_considered == 14 and v.findings[0].rule_code == "PRIV-003"  # violations first
    # skipped hard rules came back as unclear, not silently passed
    assert {f.rule_code for f in v.findings if f.status == "unclear"} >= {"PRIV-001", "LAUNCH-001"}

    kind, prompt = fake_llm.calls[-1]
    assert kind == "LlmFindings" and 'code="PRIV-003" severity="hard"' in prompt
    assert "<passage source=" in prompt  # document evidence was retrieved

    [row] = await container.assessments.list(user_id="alice@example.com")
    assert row["verdict"] == "NON_COMPLIANT" and row["id"] == v.assessment_id


async def test_assessment_with_no_rules(container):
    v = await container.assessment.assess("anything", user_id="u")
    assert v.verdict == VerdictLabel.NEEDS_MORE_INFO and "no active rules" in v.summary


async def test_large_rulebase_uses_retrieval(container, fake_llm):
    await seed_rules(container)
    container.settings.assess_inline_rule_limit = 5
    container.settings.assess_top_k_rules = 3
    fake_llm.findings = findings_from({})
    v = await container.assessment.assess("parental consent for children's email", user_id="u")
    assert v.rules_considered == 3
    assert "PRIV-003" in fake_llm.calls[-1][1]
