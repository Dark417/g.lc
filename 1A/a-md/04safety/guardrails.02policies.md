# guardrails.02policies The Six Policies

> What each guardrail policy detects, and how content filters, denied topics, and word filters are configured.

## Index

- [1. Policy Overview](#1-policy-overview)
- [2. Spec As Code](#2-spec-as-code)
- [3. Content Filters](#3-content-filters)
  - [3.1 Strength vs Confidence](#31-strength-vs-confidence)
  - [3.2 Prompt Attack Filter](#32-prompt-attack-filter)
  - [3.3 Code: Content Policy Builder](#33-code-content-policy-builder)
- [4. Denied Topics](#4-denied-topics)
- [5. Word Filters](#5-word-filters)

Back to [00index](guardrails.00index.md).
Sensitive information and grounding: [03sensitive-grounding](guardrails.03sensitive-grounding.md).
Automated Reasoning: [08automated-reasoning](guardrails.08automated-reasoning.md).

## 1. Policy Overview

One guardrail holds up to six policies; each has its own Application Programming Interface (API) field and actions.

| Policy | API field (create) | What it detects | Actions | Input / output |
|---|---|---|---|---|
| Content filters | `contentPolicyConfig.filtersConfig[]` | HATE, INSULTS, SEXUAL, VIOLENCE, MISCONDUCT, PROMPT_ATTACK | strength NONE/LOW/MEDIUM/HIGH; action BLOCK/NONE | both (PROMPT_ATTACK input only) |
| Denied topics | `topicPolicyConfig.topicsConfig[]` | natural-language topic definition + examples | BLOCK/NONE | both |
| Word filters | `wordPolicyConfig.wordsConfig[]`, `managedWordListsConfig[]` | exact words/phrases; managed PROFANITY list | BLOCK/NONE | both |
| Sensitive information | `sensitiveInformationPolicyConfig.piiEntitiesConfig[]`, `regexesConfig[]` | 31 built-in Personally Identifiable Information (PII) types + custom regex | BLOCK / ANONYMIZE / NONE | both |
| Contextual grounding | `contextualGroundingPolicyConfig.filtersConfig[]` | GROUNDING (answer supported by source), RELEVANCE (answer addresses query) | threshold 0–0.99; BLOCK/NONE | output only |
| Automated Reasoning | `automatedReasoningPolicyConfig.policies[]` | answer vs formal rules extracted from a policy document | findings only (you decide) | output |

## 2. Spec As Code

The repo models the full guardrail as a frozen spec that mirrors the Terraform module field by field.

- `GuardrailSpec` = every policy + messages + tier + Key Management Service (KMS) + Automated Reasoning (AR) Amazon Resource Names (ARNs)
- `build_guardrail_request` turns it into the `CreateGuardrail` body
  - one builder per policy type
  - `UpdateGuardrail` takes the same body + `guardrailIdentifier`
- `default_spec` = the same policy set as Terraform
  - so code and Terraform can be diffed line by line

```python
# app/infra/_04safety_01guardrails.py
def build_guardrail_request(spec: GuardrailSpec) -> Json:
    """Full CreateGuardrail body from a spec. UpdateGuardrail takes the same body + guardrailIdentifier."""
    body: Json = {
        "name": spec.name,
        "description": spec.description,
        "blockedInputMessaging": spec.blocked_input_messaging,
        "blockedOutputsMessaging": spec.blocked_outputs_messaging,
        "contentPolicyConfig": content_policy(spec.content_filters, spec.tier),
        "topicPolicyConfig": topic_policy(spec.topics, spec.tier),
        "wordPolicyConfig": word_policy(spec.words, spec.managed_word_lists),
        "sensitiveInformationPolicyConfig": sensitive_information_policy(spec.pii, spec.regexes),
    }
    if spec.grounding is not None:
        body["contextualGroundingPolicyConfig"] = contextual_grounding_policy(
            spec.grounding.grounding_threshold, spec.grounding.relevance_threshold, spec.tier
        )
    ar = automated_reasoning_policy(spec.ar_policy_arns, spec.ar_confidence_threshold)
    if ar is not None:
        body["automatedReasoningPolicyConfig"] = ar
    xr = cross_region_config(spec.tier, spec.guardrail_profile_id)
    if xr is not None:
        body["crossRegionConfig"] = xr
    if spec.kms_key_id:
        body["kmsKeyId"] = spec.kms_key_id  # CMK; callers then need kms:Decrypt on it
    return body
```

- `create_guardrail` is idempotent two ways
  - `clientRequestToken` dedups Software Development Kit (SDK) retries of the same call
  - `ConflictException` (name exists) falls back to find-by-name + `UpdateGuardrail`

```python
# app/infra/_04safety_01guardrails.py
def create_guardrail(spec: GuardrailSpec, client_token: str | None = None) -> tuple[str, str, str]:
    body = build_guardrail_request(spec)
    body["tags"] = [{"key": k, "value": v} for k, v in spec.tags.items()]
    body["clientRequestToken"] = client_token or str(uuid.uuid4())
    try:
        resp = _control().create_guardrail(**body)
        return resp["guardrailId"], resp["guardrailArn"], resp["version"]
    except ClientError as e:
        if _error_code(e) != "ConflictException":
            raise
    existing = find_guardrail_by_name(spec.name)  # names are unique per account + Region; APIs take ids
    if existing is None:
        raise RuntimeError(f"guardrail {spec.name} reported as existing but not found")
    update_guardrail(existing["id"], spec)  # re-run converges
    return existing["id"], existing["arn"], DRAFT
```

- Catch
  - The SDK path creates its own guardrail (`a-guardrail-sdk`)
    - so it never fights Terraform over `a-guardrail`
  - Terraform owns the real resource; SDK create/update is for tooling and tests

## 3. Content Filters

Six classifier categories: HATE, INSULTS, SEXUAL, VIOLENCE, MISCONDUCT, PROMPT_ATTACK.

### 3.1 Strength vs Confidence

- The classifier assigns each category a confidence
  - NONE, LOW, MEDIUM, HIGH
- **Strength** = the lowest confidence that blocks
  - HIGH strength blocks LOW + MEDIUM + HIGH confidence
    - most blocking, most false positives
  - LOW strength blocks HIGH confidence only
  - NONE = off
- `inputModalities` / `outputModalities` = TEXT, IMAGE
  - image filtering covers the 6 content categories
  - check supported formats

### 3.2 Prompt Attack Filter

- Detects jailbreaks and prompt injection
  - prompt leakage too, on the Standard tier
- `outputStrength` must be `NONE`
  - the API rejects anything else
- Tagging and defense in depth: [04prompt-attacks](guardrails.04prompt-attacks.md)

### 3.3 Code: Content Policy Builder

- Output fields are omitted whenever output strength is NONE
  - this satisfies the PROMPT_ATTACK input-only rule
- Action NONE = detect mode (evaluated, not enforced)

```python
# app/infra/_04safety_01guardrails.py
def content_policy(filters: tuple[ContentFilterSpec, ...], tier: Tier) -> Json:
    out: list[Json] = []
    for f in filters:
        item: Json = {
            "type": f.type,
            "inputStrength": f.input_strength.value,
            "outputStrength": f.output_strength.value,
            "inputAction": f.input_action.value,
            "inputEnabled": f.input_strength != Strength.NONE,
            "inputModalities": list(f.input_modalities),  # TEXT | IMAGE (IMAGE adds image units)
        }
        if f.output_strength != Strength.NONE:  # PROMPT_ATTACK: output strength must stay NONE
            item |= {
                "outputAction": f.output_action.value,
                "outputEnabled": True,
                "outputModalities": list(f.output_modalities),
            }
        out.append(item)
    return {"filtersConfig": out, "tierConfig": {"tierName": tier.value}}
```

```python
# app/domain/_04safety_01guardrails.py  (default_spec excerpt)
content_filters=(
    ContentFilterSpec("HATE", s.HIGH, s.HIGH, input_modalities=("TEXT", "IMAGE")),
    ContentFilterSpec("INSULTS", s.MEDIUM, s.MEDIUM, input_modalities=("TEXT", "IMAGE")),
    ContentFilterSpec("SEXUAL", s.HIGH, s.HIGH, input_modalities=("TEXT", "IMAGE")),
    ContentFilterSpec("VIOLENCE", s.MEDIUM, s.HIGH, input_modalities=("TEXT", "IMAGE")),
    ContentFilterSpec("MISCONDUCT", s.HIGH, s.HIGH, input_modalities=("TEXT", "IMAGE")),
    # Input only: outputStrength must be NONE.
    ContentFilterSpec("PROMPT_ATTACK", s.HIGH, s.NONE, output_action=FilterAction.NONE, output_modalities=()),
),
```

- Catch
  - Higher strength = more recall, more false positives
  - Raise only when eval shows misses; lower when False Positive (FP) rate exceeds target

## 4. Denied Topics

A topic classifier blocks a subject described in natural language.

- Definition = what the topic is, written as a description, not a command
  - "Investment advice is …", not "Don't give …"
- Up to 5 example phrases per topic
- Up to 30 topics per guardrail (check the quota page)
- Topic classifier, not keyword match
  - catches paraphrases
  - also catches near misses (e.g. "what is an index fund?")
- `type` is always `DENY`
- `inputAction` / `outputAction` are API-only
  - Terraform 6.73 cannot set these two

```python
# app/infra/_04safety_01guardrails.py
def topic_policy(topics: tuple[TopicSpec, ...], tier: Tier) -> Json:
    return {
        "topicsConfig": [
            {
                "name": t.name,
                "definition": t.definition,  # describe the topic; do not write "don't ..."
                "examples": list(t.examples),  # up to 5 user phrasings
                "type": "DENY",
                "inputAction": t.input_action.value,
                "outputAction": t.output_action.value,
                "inputEnabled": True,
                "outputEnabled": True,
            }
            for t in topics
        ],
        "tierConfig": {"tierName": tier.value},  # STANDARD: better on typos/obfuscation, more languages
    }
```

```python
# app/domain/_04safety_01guardrails.py  (default_spec excerpt)
TopicSpec(
    "InvestmentAdvice",
    "Personalized recommendations about buying, selling, or allocating stocks, bonds, funds, crypto, "
    "or other financial assets.",
    (
        "Which stocks should I buy this month?",
        "Should I move my 401k into crypto?",
        "Is now a good time to sell my Tesla shares?",
    ),
),
```

- Catch
  - The classifier is semantic ⇒ measure FP on a labeled set
  - Vague definitions over-block adjacent topics

## 5. Word Filters

Exact-match lists for words and phrases the classifiers would not know.

- Exact match after normalization, case-insensitive
  - order of magnitude: up to 10,000 custom words; check the quota page
- Cheap and precise
  - use for brand names, competitor names, internal code names
- Managed list: `PROFANITY` is the only type

```python
# app/infra/_04safety_01guardrails.py
def word_policy(words: tuple[WordSpec, ...], managed_lists: tuple[str, ...]) -> Json:
    return {
        "wordsConfig": [
            {
                "text": w.text,
                "inputAction": w.input_action.value,
                "outputAction": w.output_action.value,
                "inputEnabled": True,
                "outputEnabled": True,
            }
            for w in words
        ],
        "managedWordListsConfig": [{"type": t} for t in managed_lists],  # PROFANITY
    }
```

```python
# app/domain/_04safety_01guardrails.py  (default_spec excerpt)
words=(
    # Internal code name: users may say it, the model must never output it.
    WordSpec("Project Nightingale", input_action=FilterAction.NONE, output_action=FilterAction.BLOCK),
    WordSpec("CompetitorCo"),
),
managed_word_lists=("PROFANITY",),
```

- Catch
  - Exact match misses paraphrases and misspellings
  - Use denied topics for meaning, word filters for literal strings
