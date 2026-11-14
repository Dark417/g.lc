"""Findings and verdicts. `aggregate` is the heart of "hard rules are hard".

The model assesses each rule. This module decides what those findings mean. Nothing here calls
a model, so every branch is unit-tested. See docs/design/03-agent-and-verdicts.md.
"""

from enum import StrEnum

from pydantic import BaseModel

from app.domain.models import Rule, Severity

DISCLAIMER = "Decision support, not legal advice. Contact Compliance for a binding answer."


class FindingStatus(StrEnum):
    SATISFIED = "satisfied"
    VIOLATED = "violated"
    UNCLEAR = "unclear"
    NOT_APPLICABLE = "not_applicable"


class VerdictLabel(StrEnum):
    COMPLIANT = "COMPLIANT"
    CONDITIONALLY_COMPLIANT = "CONDITIONALLY_COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    NEEDS_MORE_INFO = "NEEDS_MORE_INFO"


class Evidence(BaseModel):
    source: str
    quote: str


# --- what the model returns (no defaults: Gemini response_schema) ---
class LlmFinding(BaseModel):
    rule_code: str
    status: FindingStatus
    reasoning: str
    evidence: list[Evidence]
    remediation: str


class LlmFindings(BaseModel):
    findings: list[LlmFinding]
    missing_information: list[str]
    summary: str


# --- what we return ---
class Finding(BaseModel):
    rule_code: str
    rule_title: str
    severity: Severity
    status: FindingStatus
    reasoning: str
    evidence: list[Evidence] = []
    remediation: str = ""
    exception_process: str = ""


class Verdict(BaseModel):
    assessment_id: str = ""
    verdict: VerdictLabel
    summary: str
    blocking: list[str] = []
    conditions: list[str] = []
    missing_information: list[str] = []
    findings: list[Finding] = []
    rules_considered: int = 0
    disclaimer: str = DISCLAIMER


def validate_findings(raw: list[LlmFinding], candidates: dict[str, Rule]) -> list[Finding]:
    """Trust the model's reading of each rule, never its bookkeeping.

    - Findings for codes we didn't send are dropped (hallucinated rules).
    - Severity, title, and exception process come from the database, not the model.
    - A candidate the model skipped: hard -> unclear (conservative), flexible -> not_applicable.
    """
    by_code: dict[str, Finding] = {}
    for f in raw:
        code = f.rule_code.strip().upper()
        rule = candidates.get(code)
        if rule is None or code in by_code:
            continue
        by_code[code] = Finding(
            rule_code=code,
            rule_title=rule.title,
            severity=rule.severity,
            status=f.status,
            reasoning=f.reasoning,
            evidence=f.evidence,
            remediation=f.remediation,
            exception_process=rule.exception_process,
        )
    for code, rule in candidates.items():
        if code not in by_code:
            hard = rule.severity == Severity.HARD
            by_code[code] = Finding(
                rule_code=code,
                rule_title=rule.title,
                severity=rule.severity,
                status=FindingStatus.UNCLEAR if hard else FindingStatus.NOT_APPLICABLE,
                reasoning="Not assessed by the reviewer model; treated conservatively.",
                exception_process=rule.exception_process,
            )
    return list(by_code.values())


def aggregate(findings: list[Finding]) -> tuple[VerdictLabel, list[str], list[str]]:
    """findings -> (verdict, blocking rules, conditions). Order of checks is the policy."""
    hard = [f for f in findings if f.severity == Severity.HARD]
    flexible = [f for f in findings if f.severity == Severity.FLEXIBLE]
    open_statuses = (FindingStatus.VIOLATED, FindingStatus.UNCLEAR)

    blocking = [
        f"{f.rule_code}: {f.rule_title}" for f in hard if f.status == FindingStatus.VIOLATED
    ]
    conditions = []
    for f in flexible:
        if f.status in open_statuses:
            text = f"{f.rule_code}: {f.remediation or 'Clarify how this rule is met.'}"
            if f.exception_process:
                text += f" (exception: {f.exception_process})"
            conditions.append(text)

    if blocking:
        return VerdictLabel.NON_COMPLIANT, blocking, conditions
    if any(f.status == FindingStatus.UNCLEAR for f in hard):
        return VerdictLabel.NEEDS_MORE_INFO, blocking, conditions
    if conditions:
        return VerdictLabel.CONDITIONALLY_COMPLIANT, blocking, conditions
    if all(f.status == FindingStatus.NOT_APPLICABLE for f in findings):
        return VerdictLabel.NEEDS_MORE_INFO, blocking, conditions
    return VerdictLabel.COMPLIANT, blocking, conditions
