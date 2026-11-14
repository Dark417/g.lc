import pytest

from app.domain.models import RuleIn, RuleUpdate
from app.services.rule_extraction import parse_rules_file
from app.storage.rules_repo import RuleConflict, code_prefix
from tests.conftest import SAMPLES, seed_rules


def rule(**kw):
    base = dict(
        title="Badge rule", statement="Badges must be worn.", severity="hard", category="security"
    )
    return RuleIn(**(base | kw))


async def test_create_generates_codes_per_category(container):
    a = await container.rule_service.create(rule(), "admin")
    b = await container.rule_service.create(rule(title="Second"), "admin")
    c = await container.rule_service.create(rule(category="product-launch"), "admin")
    assert (a.code, b.code, c.code) == ("SECURI-001", "SECURI-002", "PRODUC-001")
    assert code_prefix("ai") == "AI" and code_prefix("---") == "GEN"


async def test_conflict_error_or_renumber(container):
    await container.rule_service.create(rule(code="sec-001"), "admin")
    with pytest.raises(RuleConflict):
        await container.rule_service.create(rule(code="SEC-001"), "admin")
    r = await container.rule_service.create(rule(code="SEC-001"), "admin", on_conflict="renumber")
    assert r.code == "SEC-002"


async def test_update_bumps_version_and_audits(container):
    await container.rule_service.create(rule(code="SEC-001"), "admin")
    r = await container.rule_service.update(
        "sec-001", RuleUpdate(statement="Badges must be visible.", change_note="clarified"), "boss"
    )
    assert r.version == 2 and r.statement == "Badges must be visible."
    versions = await container.rules.versions("SEC-001")
    assert [(v["version"], v["changed_by"], v["change_note"]) for v in versions] == [
        (1, "admin", "created"),
        (2, "boss", "clarified"),
    ]
    assert versions[0]["snapshot"]["statement"] == "Badges must be worn."


async def test_retire_removes_from_search_and_active_list(container):
    await container.rule_service.create(rule(code="SEC-001"), "admin")
    assert await container.vectors.count("rule") == 1
    retired = await container.rule_service.retire("SEC-001", "admin", "obsolete")
    assert retired.status == "retired"
    assert await container.vectors.count("rule") == 0
    assert await container.rules.list() == []
    assert len(await container.rules.list(status=None)) == 1


async def test_list_filters(container):
    await seed_rules(container)
    assert len(await container.rules.list()) == 14
    assert {
        r.code for r in await container.rules.list(category="PRIVACY", severity="flexible")
    } == {"PRIV-004"}
    assert [r.code for r in await container.rules.list(q="parental")] == ["PRIV-003"]
    hits = await container.retriever.search_rules("parental consent for children under 13", k=3)
    assert hits[0].ref_id == "PRIV-003"


def test_parse_rules_files():
    csv_rules = parse_rules_file((SAMPLES / "rules" / "regional-rules.csv").read_bytes(), "r.csv")
    assert [r.code for r in csv_rules] == ["REG-001", "REG-002", "REG-003"]
    assert csv_rules[2].severity == "flexible" and csv_rules[2].exception_process.startswith(
        "Legal"
    )
    json_rules = parse_rules_file(
        b'[{"title":"No code rule","statement":"Must x.","severity":"HARD","category":"ops"}]',
        "r.json",
    )
    assert json_rules[0].code is None and json_rules[0].severity == "hard"
    with pytest.raises(ValueError, match="row 1"):
        parse_rules_file(
            b'[{"title":"x","statement":"y","severity":"maybe","category":"c"}]', "r.json"
        )
