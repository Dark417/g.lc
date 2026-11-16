# guardrails.03sensitive-grounding Sensitive Information and Contextual Grounding

> The Personally Identifiable Information (PII) + regex policy, and the grounding/relevance check for Retrieval-Augmented Generation (RAG) answers.

## Index

- [1. Sensitive Information](#1-sensitive-information)
  - [1.1 Actions](#11-actions)
  - [1.2 Code: PII and Regex Builder](#12-code-pii-and-regex-builder)
  - [1.3 Limits](#13-limits)
- [2. Contextual Grounding](#2-contextual-grounding)
  - [2.1 How It Scores](#21-how-it-scores)
  - [2.2 Code: Policy and Check](#22-code-policy-and-check)
  - [2.3 Limits](#23-limits)

Back to [00index](guardrails.00index.md).
Deeper PII handling (Comprehend, pseudonyms): [pii-redaction](pii-redaction.00index.md).

## 1. Sensitive Information

Built-in PII entities (31 types) plus custom regexes, each with its own action.

### 1.1 Actions

- BLOCK ⇒ the whole call is refused
- ANONYMIZE ⇒ replaced by `{EMAIL}`, `{PHONE}`, `{REGEX_NAME}`
  - the call continues
- NONE ⇒ detect only
- Regex
  - fields: `name`, `pattern`, `description`, action
  - up to 10 regexes (check the quota page)
  - the regex name doubles as the mask token: `{InternalAccountId}`
- Input ANONYMIZE masks before the model sees it
  - the model cannot echo it back

### 1.2 Code: PII and Regex Builder

```python
# app/infra/_04safety_01guardrails.py
def _pii_item(p: PiiSpec) -> Json:
    return {
        "type": p.type,
        "action": p.action.value,  # BLOCK | ANONYMIZE | NONE
        "inputAction": (p.input_action or p.action).value,  # per-side override, else same as action
        "outputAction": (p.output_action or p.action).value,
        "inputEnabled": True,
        "outputEnabled": True,
    }


def sensitive_information_policy(pii: tuple[PiiSpec, ...], regexes: tuple[RegexSpec, ...]) -> Json:
    """Catch: ANONYMIZE is not applied in async streaming mode; regex units are reported as free units."""
    return {
        "piiEntitiesConfig": [_pii_item(p) for p in pii],
        "regexesConfig": [_regex_item(r) for r in regexes],
    }
```

```python
# app/domain/_04safety_01guardrails.py  (default_spec excerpt)
pii=(
    PiiSpec("EMAIL", PiiAction.ANONYMIZE),
    PiiSpec("PHONE", PiiAction.ANONYMIZE),
    # Names: allowed in (users sign messages), masked out.
    PiiSpec("NAME", PiiAction.ANONYMIZE, input_action=PiiAction.NONE, output_action=PiiAction.ANONYMIZE),
    PiiSpec("US_SOCIAL_SECURITY_NUMBER", PiiAction.BLOCK),
    PiiSpec("CREDIT_DEBIT_CARD_NUMBER", PiiAction.BLOCK),
    PiiSpec("AWS_SECRET_KEY", PiiAction.BLOCK),
),
regexes=(
    RegexSpec(
        "InternalAccountId", r"ACCT-[0-9]{8}", PiiAction.ANONYMIZE, "Internal account id, e.g. ACCT-12345678"
    ),
),
```

### 1.3 Limits

- Machine Learning (ML) detector
  - names and addresses are fuzzier than Social Security Number (SSN)/card patterns
- ANONYMIZE is not applied in async streaming
  - see [06streaming](guardrails.06streaming.md)
- Greedy regexes risk catastrophic backtracking and false hits
  - anchor patterns, test on a corpus

## 2. Contextual Grounding

An output-only check that scores the answer against the retrieved source and the question.

### 2.1 How It Scores

- Needs three pieces (qualifiers)
  - `grounding_source`: retrieved passages
  - `query`: user question
  - `guard_content`: model answer
- GROUNDING score low ⇒ hallucinated relative to the source
- RELEVANCE score low ⇒ off-topic relative to the query
- Block when score < threshold
  - higher threshold = stricter

### 2.2 Code: Policy and Check

- Without the qualifiers the policy is silently skipped

```python
# app/infra/_04safety_01guardrails.py
def contextual_grounding_policy(grounding_threshold: float, relevance_threshold: float, tier: Tier) -> Json:
    return {
        "filtersConfig": [
            # threshold 0..0.99, block when score < threshold
            {"type": "GROUNDING", "threshold": grounding_threshold, "action": "BLOCK", "enabled": True},
            {"type": "RELEVANCE", "threshold": relevance_threshold, "action": "BLOCK", "enabled": True},
        ],
        "tierConfig": {"tierName": tier.value},  # API only; Terraform 6.73 has no tier for grounding
    }


def check_grounding(passages: list[str], query: str, answer: str, version: str | None = None) -> GuardrailVerdict:
    """Catch: the guarantee is relative to the passages you pass; wrong retrieval + faithful answer still passes."""
    blocks = [TextBlock(p, (Qualifier.GROUNDING_SOURCE,)) for p in passages]
    blocks += [TextBlock(query, (Qualifier.QUERY,)), TextBlock(answer, (Qualifier.GUARD_CONTENT,))]
    return apply_guardrail(blocks, Source.OUTPUT, version=version)
```

```python
# app/domain/_04safety_01guardrails.py
@dataclass(frozen=True)
class GroundingSpec:
    grounding_threshold: float = 0.75  # 0..0.99; block if GROUNDING score < threshold
    relevance_threshold: float = 0.5  # 0..0.99; block if RELEVANCE score < threshold
```

### 2.3 Limits

- Checks against the source given, not world truth
- Long sources are truncated
  - check the per-request character limit
  - pass the top-k passages actually cited, not the whole Knowledge Base (KB) result
- Threshold is a precision/recall knob
  - set it from a labeled set of grounded vs hallucinated answers
