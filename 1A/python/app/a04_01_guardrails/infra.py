"""Bedrock Guardrails showcase (boto3), in the order of docs/04.01.guardrails.md.

- Two clients:
  - client("bedrock"): control plane = create/update/version/get/list guardrails (configuration as code)
  - client("bedrock-runtime"): data plane = apply_guardrail, converse(+stream) with guardrailConfig,
    invoke_guardrail_checks
- Field names follow the botocore 1.44 service model; every knob carries its allowed values in a comment.
- No AWS call at import time: clients are created on first use via app.shared.aws.
- Throttling is retried by the shared client config (adaptive mode); business outcomes
  (GUARDRAIL_INTERVENED) are results, not errors.
"""

import time
import uuid
from collections.abc import Iterator
from typing import Any

from botocore.exceptions import ClientError

from app.a04_01_guardrails.config import get_guardrails_settings
from app.a04_01_guardrails.domain import (
    ContentFilterSpec,
    GroundingScore,
    GuardedReply,
    GuardrailSpec,
    GuardrailVerdict,
    PiiSpec,
    PolicyHit,
    Qualifier,
    RegexSpec,
    Source,
    Strength,
    TextBlock,
    Tier,
    TopicSpec,
    WordSpec,
)
from app.shared import aws
from app.shared.config import get_settings
from app.shared.retry import backoff

Json = dict[str, Any]

INTERVENED = "GUARDRAIL_INTERVENED"
STOP_INTERVENED = "guardrail_intervened"
DRAFT = "DRAFT"
READY_STATES = {"READY"}
FAILED_STATES = {"FAILED"}


def _control() -> Any:
    return aws.client("bedrock")


def _runtime() -> Any:
    return aws.client("bedrock-runtime")


def _model_id() -> str:
    return get_guardrails_settings().model_id or get_settings().text_model_id


def _error_code(e: ClientError) -> str:
    return str(e.response.get("Error", {}).get("Code", ""))


# ================================================================ 1. policy builders (one per policy type)
# Each returns exactly the dict CreateGuardrail / UpdateGuardrail expects for that policy.


def content_policy(filters: tuple[ContentFilterSpec, ...], tier: Tier) -> Json:
    """contentPolicyConfig: HATE, INSULTS, SEXUAL, VIOLENCE, MISCONDUCT, PROMPT_ATTACK.

    Strength NONE|LOW|MEDIUM|HIGH; action BLOCK|NONE (NONE = detect mode). Catch: PROMPT_ATTACK is input-only,
    its outputStrength must be NONE, so output fields are omitted whenever output strength is NONE.
    """
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
        if f.output_strength != Strength.NONE:
            item |= {
                "outputAction": f.output_action.value,
                "outputEnabled": True,
                "outputModalities": list(f.output_modalities),
            }
        out.append(item)
    return {"filtersConfig": out, "tierConfig": {"tierName": tier.value}}


def topic_policy(topics: tuple[TopicSpec, ...], tier: Tier) -> Json:
    """topicPolicyConfig: denied topics. type is always DENY.

    Definition describes the topic; examples are user phrasings (up to 5). The classifier is semantic, so it
    also blocks paraphrases and near misses: measure FP on a labeled set. inputAction/outputAction are API-only.
    """
    return {
        "topicsConfig": [
            {
                "name": t.name,
                "definition": t.definition,
                "examples": list(t.examples),
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


def word_policy(words: tuple[WordSpec, ...], managed_lists: tuple[str, ...]) -> Json:
    """wordPolicyConfig: exact custom words/phrases + AWS-managed lists (PROFANITY is the only type)."""
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
        "managedWordListsConfig": [{"type": t} for t in managed_lists],
    }


def _pii_item(p: PiiSpec) -> Json:
    return {
        "type": p.type,
        "action": p.action.value,  # BLOCK | ANONYMIZE | NONE
        "inputAction": (p.input_action or p.action).value,
        "outputAction": (p.output_action or p.action).value,
        "inputEnabled": True,
        "outputEnabled": True,
    }


def _regex_item(r: RegexSpec) -> Json:
    item: Json = {"name": r.name, "pattern": r.pattern, "action": r.action.value}
    if r.description:
        item["description"] = r.description
    return item


def sensitive_information_policy(pii: tuple[PiiSpec, ...], regexes: tuple[RegexSpec, ...]) -> Json:
    """sensitiveInformationPolicyConfig: built-in PII entities + custom regexes.

    BLOCK = refuse the call; ANONYMIZE = replace with {TYPE} / {regex name} and continue; NONE = detect only.
    Catch: ANONYMIZE is not applied in async streaming mode; regex units are reported as free units.
    """
    return {
        "piiEntitiesConfig": [_pii_item(p) for p in pii],
        "regexesConfig": [_regex_item(r) for r in regexes],
    }


def contextual_grounding_policy(grounding_threshold: float, relevance_threshold: float, tier: Tier) -> Json:
    """contextualGroundingPolicyConfig: GROUNDING (answer supported by source) + RELEVANCE (answer fits query).

    threshold 0..0.99, block when score < threshold. Only runs when the call carries grounding_source + query
    qualifiers; otherwise it is silently skipped.
    """
    return {
        "filtersConfig": [
            {"type": "GROUNDING", "threshold": grounding_threshold, "action": "BLOCK", "enabled": True},
            {"type": "RELEVANCE", "threshold": relevance_threshold, "action": "BLOCK", "enabled": True},
        ],
        "tierConfig": {"tierName": tier.value},  # API only; Terraform 6.73 has no tier for grounding
    }


def automated_reasoning_policy(policy_arns: tuple[str, ...], confidence_threshold: float) -> Json | None:
    """automatedReasoningPolicyConfig: attach Automated Reasoning policy VERSION ARNs (SDK only, not in Terraform).

    Findings only (valid / invalid / satisfiable / impossible / translationAmbiguous / tooComplex /
    noTranslations); the guardrail does not block on them, your code decides.
    """
    if not policy_arns:
        return None
    return {"policies": list(policy_arns), "confidenceThreshold": confidence_threshold}


def cross_region_config(tier: Tier, guardrail_profile_id: str) -> Json | None:
    """crossRegionConfig: required for the STANDARD tier; the check may run in another Region of the geography."""
    if tier != Tier.STANDARD:
        return None
    if not guardrail_profile_id:
        raise ValueError("STANDARD tier needs a guardrail profile id, e.g. us.guardrail.v1:0")
    return {"guardrailProfileIdentifier": guardrail_profile_id}


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


# ================================================================ 2. control plane: create / update / version / read


def create_guardrail(spec: GuardrailSpec, client_token: str | None = None) -> tuple[str, str, str]:
    """CreateGuardrail with every policy. Returns (guardrail_id, arn, "DRAFT").

    Idempotent two ways: clientRequestToken dedups SDK retries of the same call; a ConflictException
    (name already exists) falls back to find-by-name + UpdateGuardrail so a re-run converges.
    """
    body = build_guardrail_request(spec)
    body["tags"] = [{"key": k, "value": v} for k, v in spec.tags.items()]
    body["clientRequestToken"] = client_token or str(uuid.uuid4())
    try:
        resp = _control().create_guardrail(**body)
        return resp["guardrailId"], resp["guardrailArn"], resp["version"]
    except ClientError as e:
        if _error_code(e) != "ConflictException":
            raise
    existing = find_guardrail_by_name(spec.name)
    if existing is None:
        raise RuntimeError(f"guardrail {spec.name} reported as existing but not found")
    update_guardrail(existing["id"], spec)
    return existing["id"], existing["arn"], DRAFT


def update_guardrail(guardrail_id: str, spec: GuardrailSpec) -> str:
    """UpdateGuardrail edits the DRAFT only. Full replace: omitted policies are REMOVED, not kept.

    Catch: numbered versions are untouched, so apps pinned to "1" see nothing until you create a version.
    """
    body = build_guardrail_request(spec)
    resp = _control().update_guardrail(guardrailIdentifier=guardrail_id, **body)
    return str(resp["version"])  # always "DRAFT"


def wait_until_ready(guardrail_id: str, version: str = DRAFT, timeout_s: float = 120.0) -> str:
    """Poll GetGuardrail until status READY (CREATING / UPDATING / VERSIONING are transient).

    FAILED carries statusReasons + failureRecommendations (e.g. an invalid regex): surface them.
    """
    deadline = time.monotonic() + timeout_s
    attempt = 0
    while True:
        g = _control().get_guardrail(guardrailIdentifier=guardrail_id, guardrailVersion=version)
        status = g["status"]
        if status in READY_STATES:
            return status
        if status in FAILED_STATES:
            reasons = g.get("statusReasons", []) + g.get("failureRecommendations", [])
            raise RuntimeError(f"guardrail {guardrail_id} {version} FAILED: {reasons}")
        if time.monotonic() > deadline:
            raise TimeoutError(f"guardrail {guardrail_id} still {status} after {timeout_s}s")
        time.sleep(max(0.5, backoff(attempt, base=0.5, cap=5.0)))
        attempt += 1


def create_guardrail_version(guardrail_id: str, description: str, client_token: str | None = None) -> str:
    """CreateGuardrailVersion snapshots the current DRAFT into an immutable "1", "2", ...

    Pass a stable clientRequestToken (e.g. a hash of the release id) so a retried release does not mint two
    versions. Catch: there is a per-guardrail version quota; old versions must be deleted eventually.
    """
    resp = _control().create_guardrail_version(
        guardrailIdentifier=guardrail_id,
        description=description,
        clientRequestToken=client_token or str(uuid.uuid4()),
    )
    return str(resp["version"])


def get_guardrail(guardrail_id: str, version: str | None = None) -> Json:
    """GetGuardrail returns the effective config of DRAFT (version omitted) or a numbered version.

    Response uses read names (contentPolicy.filters, sensitiveInformationPolicy.piiEntities, ...) that differ
    from the create names (contentPolicyConfig.filtersConfig, ...): do not round-trip blindly.
    """
    kwargs: Json = {"guardrailIdentifier": guardrail_id}
    if version:
        kwargs["guardrailVersion"] = version
    g = _control().get_guardrail(**kwargs)
    return {
        "id": g["guardrailId"],
        "arn": g["guardrailArn"],
        "name": g["name"],
        "version": g["version"],
        "status": g["status"],
        "content_filters": [
            {"type": f["type"], "in": f["inputStrength"], "out": f["outputStrength"]}
            for f in g.get("contentPolicy", {}).get("filters", [])
        ],
        "content_tier": g.get("contentPolicy", {}).get("tier", {}).get("tierName"),
        "topics": [t["name"] for t in g.get("topicPolicy", {}).get("topics", [])],
        "words": [w["text"] for w in g.get("wordPolicy", {}).get("words", [])],
        "pii": {p["type"]: p["action"] for p in g.get("sensitiveInformationPolicy", {}).get("piiEntities", [])},
        "regexes": [r["name"] for r in g.get("sensitiveInformationPolicy", {}).get("regexes", [])],
        "grounding": {
            f["type"]: f["threshold"] for f in g.get("contextualGroundingPolicy", {}).get("filters", [])
        },
        "automated_reasoning": g.get("automatedReasoningPolicy", {}).get("policies", []),
        "cross_region_profile": g.get("crossRegionDetails", {}).get("guardrailProfileId"),
        "kms_key_arn": g.get("kmsKeyArn"),
    }


def list_guardrails(guardrail_id: str | None = None) -> list[Json]:
    """ListGuardrails with manual nextToken pagination.

    Without guardrail_id: the DRAFT of every guardrail. With it: every version of that one guardrail.
    """
    out: list[Json] = []
    kwargs: Json = {"maxResults": 100}  # 1..1000
    if guardrail_id:
        kwargs["guardrailIdentifier"] = guardrail_id
    while True:
        resp = _control().list_guardrails(**kwargs)
        out.extend(
            {"id": g["id"], "name": g["name"], "version": g["version"], "status": g["status"]}
            for g in resp["guardrails"]
        )
        token = resp.get("nextToken")
        if not token:
            return out
        kwargs["nextToken"] = token


def list_versions(guardrail_id: str) -> list[str]:
    """Numbered versions of one guardrail (DRAFT excluded), oldest first."""
    versions = [g["version"] for g in list_guardrails(guardrail_id) if g["version"] != DRAFT]
    return sorted(versions, key=int)


def find_guardrail_by_name(name: str) -> Json | None:
    """Names are unique per account + Region, but APIs take ids: resolve name -> id by listing."""
    resp_items = list_guardrails()
    for g in resp_items:
        if g["name"] == name:
            arn = _control().get_guardrail(guardrailIdentifier=g["id"])["guardrailArn"]
            return {"id": g["id"], "arn": arn}
    return None


# ================================================================ 3. ApplyGuardrail: standalone, any model


def _block_json(b: TextBlock) -> Json:
    text: Json = {"text": b.text}
    if b.qualifiers:
        text["qualifiers"] = [q.value for q in b.qualifiers]
    return {"text": text}


def apply_guardrail(
    blocks: list[TextBlock],
    source: Source,
    version: str | None = None,
    output_scope: str = "INTERVENTIONS",
    image_png: bytes | None = None,
) -> GuardrailVerdict:
    """ApplyGuardrail: check text without calling a model; works for Bedrock, SageMaker, or any provider.

    source INPUT = user side, OUTPUT = model side (adds grounding / AR). output_scope INTERVENTIONS (only hits)
    or FULL (every assessment incl. non-hits: use for eval and threshold tuning). Catch: one extra round trip
    per check; version is required here (DRAFT or a number).
    """
    s = get_guardrails_settings()
    content = [_block_json(b) for b in blocks]
    if image_png is not None:
        # Image block: content filters with IMAGE modality; png | jpeg; raw bytes (boto3 base64-encodes).
        content.append({"image": {"format": "png", "source": {"bytes": image_png}}})
    resp = _runtime().apply_guardrail(
        guardrailIdentifier=s.guardrail_id,
        guardrailVersion=version or s.guardrail_version,
        source=source.value,
        content=content,
        outputScope=output_scope,
    )
    original = "\n".join(b.text for b in blocks if Qualifier.GROUNDING_SOURCE not in b.qualifiers)
    return parse_apply_response(resp, original)


def _assessment_hits(a: Json) -> tuple[list[PolicyHit], list[GroundingScore]]:
    """One GuardrailAssessment -> flat hits. Same shape in ApplyGuardrail and in the Converse trace."""
    hits: list[PolicyHit] = []
    for t in a.get("topicPolicy", {}).get("topics", []):
        hits.append(PolicyHit("topic", t["name"], t["action"], t.get("detected", t["action"] != "NONE")))
    for f in a.get("contentPolicy", {}).get("filters", []):
        hits.append(
            PolicyHit(
                "content", f["type"], f["action"], f.get("detected", f["action"] != "NONE"), f.get("confidence", "")
            )
        )
    word = a.get("wordPolicy", {})
    for w in word.get("customWords", []):
        hits.append(PolicyHit("word", "CUSTOM", w["action"], w.get("detected", True), match=w["match"]))
    for w in word.get("managedWordLists", []):
        hits.append(PolicyHit("managed_word", w["type"], w["action"], w.get("detected", True), match=w["match"]))
    sens = a.get("sensitiveInformationPolicy", {})
    for p in sens.get("piiEntities", []):
        hits.append(PolicyHit("pii", p["type"], p["action"], p.get("detected", True), match=p["match"]))
    for r in sens.get("regexes", []):
        hits.append(PolicyHit("regex", r.get("name", ""), r["action"], r.get("detected", True), match=r.get("match", "")))
    for finding in a.get("automatedReasoningPolicy", {}).get("findings", []):
        kind = next(iter(finding), "unknown")  # valid | invalid | satisfiable | impossible | translationAmbiguous ...
        hits.append(PolicyHit("automated_reasoning", kind, "NONE", True))
    grounding = [
        GroundingScore(f["type"], float(f["score"]), float(f["threshold"]), f["action"])
        for f in a.get("contextualGroundingPolicy", {}).get("filters", [])
    ]
    return hits, grounding


def parse_apply_response(resp: Json, original_text: str = "") -> GuardrailVerdict:
    """ApplyGuardrail response -> GuardrailVerdict.

    outputs[] is present only when the guardrail intervened: masked text (ANONYMIZE) or the blocked message.
    """
    hits: list[PolicyHit] = []
    grounding: list[GroundingScore] = []
    latency = 0
    for a in resp.get("assessments", []):
        h, g = _assessment_hits(a)
        hits += h
        grounding += g
        latency += int(a.get("invocationMetrics", {}).get("guardrailProcessingLatency", 0))
    intervened = resp.get("action") == INTERVENED
    outputs = [o.get("text", "") for o in resp.get("outputs", [])]
    coverage = resp.get("guardrailCoverage", {}).get("textCharacters", {})
    return GuardrailVerdict(
        intervened=intervened,
        blocked=any(h.action == "BLOCKED" for h in hits) or any(g.action == "BLOCKED" for g in grounding),
        output_text="\n".join(outputs) if intervened and outputs else original_text,
        action_reason=resp.get("actionReason", ""),
        hits=tuple(hits),
        grounding=tuple(grounding),
        usage={k: int(v) for k, v in resp.get("usage", {}).items()},
        guarded_chars=int(coverage.get("guarded", 0)),
        total_chars=int(coverage.get("total", 0)),
        latency_ms=latency,
    )


def check_grounding(passages: list[str], query: str, answer: str, version: str | None = None) -> GuardrailVerdict:
    """Contextual grounding of a RAG answer: OUTPUT source + the three qualifiers.

    Catch: the guarantee is relative to the passages you pass; wrong retrieval + faithful answer still passes.
    """
    blocks = [TextBlock(p, (Qualifier.GROUNDING_SOURCE,)) for p in passages]
    blocks += [TextBlock(query, (Qualifier.QUERY,)), TextBlock(answer, (Qualifier.GUARD_CONTENT,))]
    return apply_guardrail(blocks, Source.OUTPUT, version=version)


class BedrockGuardrail:
    """GuardrailPort adapter over ApplyGuardrail."""

    def __init__(self, version: str | None = None) -> None:
        self._version = version

    def apply(self, blocks: list[TextBlock], source: Source) -> GuardrailVerdict:
        return apply_guardrail(blocks, source, version=self._version)


class BedrockChatModel:
    """ChatModelPort adapter: plain Converse WITHOUT guardrailConfig (the service guards around it).

    Swap for any provider: the guard calls do not care which model produced the text.
    """

    def generate(self, system: str, user_text: str, context: list[str]) -> str:
        prompt = user_text if not context else "Context:\n" + "\n---\n".join(context) + "\n\nQuestion: " + user_text
        resp = _runtime().converse(
            modelId=_model_id(),
            system=[{"text": system}],
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 512, "temperature": 0.2},
        )
        return "".join(c.get("text", "") for c in resp["output"]["message"]["content"])


# ================================================================ 4. Converse with guardrailConfig


def _guardrail_config(trace: str | None = None) -> Json:
    s = get_guardrails_settings()
    return {
        "guardrailIdentifier": s.guardrail_id,
        "guardrailVersion": s.guardrail_version,  # pin a number in prod; DRAFT changes under you
        "trace": trace or s.trace,  # disabled | enabled | enabled_full (adds raw modelOutput: don't log it)
    }


def _trace_verdicts(trace: Json) -> tuple[GuardrailVerdict | None, GuardrailVerdict | None]:
    """trace.guardrail: inputAssessment = {guardrailId: assessment}, outputAssessments = {guardrailId: [..]}."""
    g = trace.get("guardrail", {})

    def verdict(assessments: list[Json]) -> GuardrailVerdict | None:
        if not assessments:
            return None
        hits: list[PolicyHit] = []
        grounding: list[GroundingScore] = []
        for a in assessments:
            h, gr = _assessment_hits(a)
            hits += h
            grounding += gr
        blocked = any(h.action == "BLOCKED" for h in hits) or any(x.action == "BLOCKED" for x in grounding)
        return GuardrailVerdict(
            intervened=bool(hits or blocked),
            blocked=blocked,
            output_text="",
            action_reason=g.get("actionReason", ""),
            hits=tuple(hits),
            grounding=tuple(grounding),
        )

    inputs = list(g.get("inputAssessment", {}).values())
    outputs = [a for lst in g.get("outputAssessments", {}).values() for a in lst]
    return verdict(inputs), verdict(outputs)


def _reply_from_converse(resp: Json) -> GuardedReply:
    text = "".join(c.get("text", "") for c in resp["output"]["message"]["content"])
    vin, vout = _trace_verdicts(resp.get("trace", {}))
    return GuardedReply(text=text, stop_reason=resp["stopReason"], input_verdict=vin, output_verdict=vout)


def converse_guarded(user_text: str, system: str = "You are a helpful banking assistant.") -> GuardedReply:
    """Converse + guardrailConfig: Bedrock runs input check -> model -> output check in one call.

    stopReason "guardrail_intervened" => output.message is the blocked message. Catch: with no guardContent
    blocks every message (history included) is evaluated, so templated instructions inside user turns can
    trip PROMPT_ATTACK; tag the untrusted part (next function) to make the scope explicit.
    """
    resp = _runtime().converse(
        modelId=_model_id(),
        system=[{"text": system}],
        messages=[{"role": "user", "content": [{"text": user_text}]}],
        inferenceConfig={"maxTokens": 512, "temperature": 0.2},
        guardrailConfig=_guardrail_config(),
    )
    return _reply_from_converse(resp)


def converse_guard_user_text_only(
    user_text: str,
    passages: list[str] | None = None,
    system: str = "Answer only from the context. If the context does not contain the answer, say so.",
) -> GuardedReply:
    """guardContent blocks: only tagged text is evaluated (fixes prompt-attack FPs on instructions/context).

    With passages, tags them grounding_source and the question query, so contextual grounding scores the
    model answer. The model still sees all blocks; guardContent only changes what the guardrail evaluates.
    """
    content: list[Json] = [{"text": "Use the context below to answer the question."}]  # not evaluated
    for p in passages or []:
        content.append({"guardContent": {"text": {"text": p, "qualifiers": [Qualifier.GROUNDING_SOURCE.value]}}})
    content.append({"guardContent": {"text": {"text": user_text, "qualifiers": [Qualifier.QUERY.value]}}})
    resp = _runtime().converse(
        modelId=_model_id(),
        system=[{"text": system}],
        messages=[{"role": "user", "content": content}],
        inferenceConfig={"maxTokens": 512, "temperature": 0.0},
        guardrailConfig=_guardrail_config(),
    )
    return _reply_from_converse(resp)


# ================================================================ 5. ConverseStream: sync vs async


def converse_stream_guarded(user_text: str, mode: str | None = None) -> Iterator[Json]:
    """ConverseStream + guardrailConfig.streamProcessingMode.

    sync (default): chunks are buffered and checked before release -> safe, masking works, slower first token.
    async: chunks flow at once, checks run behind -> fast, but text can show before a block and ANONYMIZE is
    not applied. Yields {"text": ...} deltas, then {"stop_reason": ..., "intervened": bool, "trace": ...}.
    """
    cfg = _guardrail_config() | {"streamProcessingMode": mode or get_guardrails_settings().stream_mode}
    resp = _runtime().converse_stream(
        modelId=_model_id(),
        messages=[{"role": "user", "content": [{"guardContent": {"text": {"text": user_text}}}]}],
        inferenceConfig={"maxTokens": 512},
        guardrailConfig=cfg,
    )
    stop_reason = ""
    for event in resp["stream"]:
        if "contentBlockDelta" in event:
            text = event["contentBlockDelta"]["delta"].get("text")
            if text:
                yield {"text": text}
        elif "messageStop" in event:
            stop_reason = event["messageStop"]["stopReason"]
        elif "metadata" in event:
            vin, vout = _trace_verdicts(event["metadata"].get("trace", {}))
            yield {
                "stop_reason": stop_reason,
                "intervened": stop_reason == STOP_INTERVENED,
                "input_hits": [h.name for h in vin.hits] if vin else [],
                "output_hits": [h.name for h in vout.hits] if vout else [],
                "usage": event["metadata"].get("usage", {}),
            }
        else:
            # Stream errors arrive as events, not exceptions at call time.
            for err in ("internalServerException", "modelStreamErrorException", "throttlingException",
                        "validationException", "serviceUnavailableException"):
                if err in event:
                    raise RuntimeError(f"{err}: {event[err].get('message', '')}")


# ================================================================ 6. inline checks (no guardrail resource)


def invoke_guardrail_checks(text: str, role: str = "user") -> Json:
    """InvokeGuardrailChecks (new in botocore 1.44): ad-hoc checks configured in the request, raw scores back.

    Returns severity / confidence scores instead of a block decision: useful for threshold tuning and eval.
    Catch: newer API, verify Region availability and the IAM action name; no topics/words/grounding here.
    """
    resp = _runtime().invoke_guardrail_checks(
        messages=[{"role": role, "content": [{"text": text}]}],  # role: user | assistant | system
        checks={
            "contentFilter": {
                "categories": [{"category": c} for c in ("VIOLENCE", "HATE", "SEXUAL", "MISCONDUCT", "INSULTS")]
            },
            "promptAttack": {
                "categories": [{"category": c} for c in ("JAILBREAK", "PROMPT_INJECTION", "PROMPT_LEAKAGE")]
            },
            "sensitiveInformation": {"entities": [{"type": t} for t in ("EMAIL", "PHONE", "US_SOCIAL_SECURITY_NUMBER")]},
        },
    )
    r = resp["results"]
    return {
        "content": {x["category"]: x["severityScore"] for x in r.get("contentFilter", {}).get("results", [])},
        "prompt_attack": {x["category"]: x["severityScore"] for x in r.get("promptAttack", {}).get("results", [])},
        "pii": [
            {"type": x["type"], "score": x["confidenceScore"], "begin": x["beginOffset"], "end": x["endOffset"]}
            for x in r.get("sensitiveInformation", {}).get("results", [])
        ],
        "usage": resp.get("usage", {}),
    }
