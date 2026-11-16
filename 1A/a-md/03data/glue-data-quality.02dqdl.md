# glue-data-quality Data Quality Definition Language (DQDL)

> Data Quality Definition Language (DQDL) is declarative: rule type, column, expression; the run returns Pass or Fail per rule.

## Index

- [1. Shape And Rule Types](#1-shape-and-rule-types)
- [2. Rules As Data](#2-rules-as-data)
- [3. Storing The Ruleset](#3-storing-the-ruleset)

## 1. Shape And Rule Types

A ruleset is a list of `RuleType "column" expression` lines.

- **Shape**: rules in a `Rules = [ ... ]` list
- **Common rule types**
  - `IsComplete "col"`: no nulls
  - `Completeness "col" > 0.95`: ratio of non-null
  - `IsUnique "col"`, `Uniqueness "col" > 0.99`
  - `ColumnValues "col" in ["a","b"]`, or `> 0`, or `matches "regex"`
  - `ColumnLength "col" between 1 and 5000`
  - `RowCount > 0`
  - `CustomSql "select count(*) from primary where ..." = 0`: any check Structured Query Language (SQL) can express
  - Also: `DataFreshness`, `ReferentialIntegrity`, `ColumnCorrelation`, `StandardDeviation`
- **Expressions**: `=`, `<`, `>`, `between a and b`, `in [...]`
- The rule list is validated when the ruleset is created or updated

```text
Rules = [
  RowCount > 0,
  IsComplete "doc_id",
  IsUnique "doc_id",
  Completeness "title" > 0.95,
  ColumnValues "language" in ["en", "de", "fr"],
  ColumnValues "char_count" between 1 and 1000000,
  CustomSql "select count(*) from primary where source is null or trim(source) = ''" = 0
]
```

- **Catch**: rules check shape, not meaning
  - All green can still be a bad corpus ⇒ add semantic evals

## 2. Rules As Data

The domain layer builds the DQDL string from typed rules, so the ruleset is testable without Amazon Web Services (AWS).

- `CustomSql` runs against the alias `primary`
- Double quotes inside the SQL must be avoided
  - The SQL itself is wrapped in double quotes

```python
# app/domain/_03data_02glue_data_quality.py
@dataclass(frozen=True)
class Rule:
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
```

- **Catch**: `CustomSql` scans the table
  - Put it on a sample size ceiling for large tables

## 3. Storing The Ruleset

Create-or-update keeps the ruleset as code without a separate existence check.

- Names are unique
  - `CreateDataQualityRuleset` raises `AlreadyExistsException`
  - The code falls back to update
- `TargetTable` attaches the ruleset to a catalog table
  - Needed for catalog-based evaluation runs
- Production: version rulesets in Terraform; keep thresholds in the ruleset, not in code

```python
# app/infra/_03data_02glue_data_quality.py
def upsert_ruleset(rules: list[Rule], name: str | None = None) -> str:
    cfg = get_glue_dq_settings()
    name = name or cfg.ruleset_name
    dqdl = build_ruleset(rules)
    try:
        _glue().create_data_quality_ruleset(
            Name=name,
            Description="Corpus metadata checks",
            Ruleset=dqdl,
            TargetTable={"DatabaseName": cfg.database, "TableName": cfg.table},
            ClientToken=str(uuid.uuid5(uuid.NAMESPACE_URL, f"dq/{name}/{dqdl}")),
        )
    except ClientError as e:
        if e.response["Error"]["Code"] != "AlreadyExistsException":
            raise
        _glue().update_data_quality_ruleset(Name=name, Description="Corpus metadata checks", Ruleset=dqdl)
    return dqdl
```

```python
# app/api/_03data_02glue_data_quality.py
@router.get("/ruleset")
def ruleset() -> dict[str, str]:
    return {"dqdl": build_ruleset(default_rules())}
```

- **Catch**: DQDL syntax errors or unknown columns raise `InvalidInputException`
  - Validate against the catalog schema
