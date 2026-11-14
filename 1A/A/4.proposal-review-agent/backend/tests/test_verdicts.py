"""The verdict policy, exhaustively. No model involved."""

from datetime import UTC, datetime

import pytest

from app.domain.models import Rule, Severity
from app.domain.verdicts import (
    Finding,
    FindingStatus,
    LlmFinding,
    VerdictLabel,
    aggregate,
    validate_findings,
)

H, F = Severity.HARD, Severity.FLEXIBLE
V, S, U, NA = "violated", "satisfied", "unclear", "not_applicable"


def f(code, severity, status, exception=""):
    return Finding(
        rule_code=code,
        rule_title=code,
        severity=severity,
        status=status,
        reasoning="",
        remediation="do x",
        exception_process=exception,
    )


@pytest.mark.parametrize(
    "findings, expected",
    [
        ([f("H1", H, V)], VerdictLabel.NON_COMPLIANT),
        ([f("H1", H, V), f("F1", F, S)], VerdictLabel.NON_COMPLIANT),
        ([f("H1", H, V), f("H2", H, U)], VerdictLabel.NON_COMPLIANT),  # violation beats unclear
        ([f("H1", H, U), f("F1", F, V)], VerdictLabel.NEEDS_MORE_INFO),
        ([f("H1", H, S), f("F1", F, V)], VerdictLabel.CONDITIONALLY_COMPLIANT),
        ([f("H1", H, S), f("F1", F, U)], VerdictLabel.CONDITIONALLY_COMPLIANT),
        ([f("H1", H, S), f("F1", F, S)], VerdictLabel.COMPLIANT),
        ([f("H1", H, NA), f("F1", F, S)], VerdictLabel.COMPLIANT),
        ([f("H1", H, NA), f("F1", F, NA)], VerdictLabel.NEEDS_MORE_INFO),  # nothing applies
        ([], VerdictLabel.NEEDS_MORE_INFO),
    ],
)
def test_aggregate_policy(findings, expected):
    assert aggregate(findings)[0] == expected


def test_blocking_and_conditions_text():
    label, blocking, conditions = aggregate(
        [f("PRIV-003", H, V), f("MKT-002", F, V, exception="Legal may approve")]
    )
    assert label == VerdictLabel.NON_COMPLIANT
    assert blocking == ["PRIV-003: PRIV-003"]
    assert conditions == ["MKT-002: do x (exception: Legal may approve)"]


def _rule(code, severity, exception=""):
    now = datetime.now(UTC)
    return Rule(
        id=code,
        code=code,
        title=f"title {code}",
        statement="must do x",
        severity=severity,
        category="cat",
        exception_process=exception,
        version=1,
        created_by="t",
        created_at=now,
        updated_at=now,
    )


def test_validate_drops_hallucinations_and_forces_db_severity():
    candidates = {"H1": _rule("H1", H), "F1": _rule("F1", F, "VP approves")}
    raw = [
        LlmFinding(rule_code="h1", status=S, reasoning="", evidence=[], remediation=""),
        LlmFinding(rule_code="H1", status=V, reasoning="dup", evidence=[], remediation=""),
        LlmFinding(rule_code="GHOST-9", status=V, reasoning="", evidence=[], remediation=""),
        LlmFinding(rule_code="F1", status=V, reasoning="", evidence=[], remediation="x"),
    ]
    out = {x.rule_code: x for x in validate_findings(raw, candidates)}
    assert set(out) == {"H1", "F1"}  # ghost dropped
    assert out["H1"].status == FindingStatus.SATISFIED  # first finding wins, dupes ignored
    assert out["F1"].severity == F and out["F1"].exception_process == "VP approves"


def test_validate_skipped_rules_are_conservative():
    candidates = {"H1": _rule("H1", H), "F1": _rule("F1", F)}
    out = {x.rule_code: x for x in validate_findings([], candidates)}
    assert out["H1"].status == FindingStatus.UNCLEAR  # skipped hard rule can't pass silently
    assert out["F1"].status == FindingStatus.NOT_APPLICABLE
    assert aggregate(list(out.values()))[0] == VerdictLabel.NEEDS_MORE_INFO
