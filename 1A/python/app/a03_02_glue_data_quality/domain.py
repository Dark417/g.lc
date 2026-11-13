"""DQDL builder: rules as data -> ruleset string. No SDK imports."""

from dataclasses import dataclass, field
from enum import StrEnum


class RunStatus(StrEnum):
    # TaskStatusType values returned by the Get*Run calls
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"


TERMINAL = {RunStatus.STOPPED, RunStatus.SUCCEEDED, RunStatus.FAILED, RunStatus.TIMEOUT}


@dataclass(frozen=True)
class Rule:
    """One DQDL rule: RuleType ["column"] [expression].

    Examples
      Rule("RowCount", expression="> 0")                          -> RowCount > 0
      Rule("IsComplete", "doc_id")                                -> IsComplete "doc_id"
      Rule("Completeness", "title", "> 0.95")                     -> Completeness "title" > 0.95
      Rule("ColumnValues", "language", 'in ["en","de"]')          -> ColumnValues "language" in ["en","de"]
      Rule("CustomSql", expression='= 0', sql="select count(*) from primary where ...")
    """

    rule_type: str
    column: str = ""
    expression: str = ""
    sql: str = ""  # CustomSql only: the SQL runs against the alias "primary"

    def to_dqdl(self) -> str:
        parts = [self.rule_type]
        if self.sql:
            parts.append(f'"{self.sql}"')  # NB: double quotes inside the SQL must be avoided
        elif self.column:
            parts.append(f'"{self.column}"')
        if self.expression:
            parts.append(self.expression)
        return " ".join(parts)


def build_ruleset(rules: list[Rule]) -> str:
    body = ",\n  ".join(r.to_dqdl() for r in rules)
    return f"Rules = [\n  {body}\n]"


def default_rules() -> list[Rule]:
    """Same rules as the Terraform ruleset."""
    return [
        Rule("RowCount", expression="> 0"),
        Rule("IsComplete", "doc_id"),
        Rule("IsUnique", "doc_id"),
        Rule("Completeness", "title", "> 0.95"),
        Rule("ColumnValues", "language", 'in ["en", "de", "fr"]'),
        Rule("ColumnValues", "char_count", "between 1 and 1000000"),
        Rule("CustomSql", expression="= 0", sql="select count(*) from primary where source is null or trim(source) = ''"),
    ]


@dataclass
class RuleOutcome:
    name: str
    result: str  # PASS | FAIL | ERROR
    message: str = ""


@dataclass
class QualityReport:
    result_id: str
    score: float  # 0..1, fraction of passing rules (as reported by Glue)
    outcomes: list[RuleOutcome] = field(default_factory=list)

    @property
    def failed(self) -> list[RuleOutcome]:
        return [o for o in self.outcomes if o.result != "PASS"]
