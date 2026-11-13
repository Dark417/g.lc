"""PII showcase (boto3): Comprehend sync + async PII, vault adapter, streaming redactor, Bedrock calls.

- Order follows docs/04.02.pii-redaction.md.
- client("comprehend"): DetectPiiEntities (offsets + scores), ContainsPiiEntities (labels only),
  StartPiiEntitiesDetectionJob / DescribePiiEntitiesDetectionJob (async S3 batch).
- client("bedrock-runtime"): Converse + ApplyGuardrail for the pipeline, called directly (no import of 04.01).
- No AWS call at import time; throttling is retried by the shared client config.
"""

import hashlib
import hmac
import os
import threading
import time
import uuid
from collections.abc import Callable
from typing import Any

from botocore.exceptions import ClientError

from app.a04_02_pii_redaction.config import get_pii_settings
from app.a04_02_pii_redaction.domain import (
    PiiEntity,
    PseudonymVault,
    RedactionPolicy,
    RedactionResult,
    redact_text,
)
from app.shared import aws
from app.shared.config import get_settings
from app.shared.retry import backoff

Json = dict[str, Any]

# Sync PII APIs cap the text per request (order of magnitude 100 KB UTF-8; check the Comprehend quota page).
# Stay under it with margin and split on whitespace so an entity is rarely cut in two.
MAX_SYNC_BYTES = 90_000
JOB_TERMINAL = {"COMPLETED", "FAILED", "STOPPED"}


def _comprehend() -> Any:
    return aws.client("comprehend")


def _runtime() -> Any:
    return aws.client("bedrock-runtime")


# ================================================================ 1. sync detection


def _chunks(text: str, max_bytes: int = MAX_SYNC_BYTES) -> list[tuple[int, str]]:
    """Split text into (char_offset, chunk) pieces under max_bytes UTF-8, cutting at whitespace when possible."""
    pieces: list[tuple[int, str]] = []
    start = 0
    while start < len(text):
        end = start
        size = 0
        while end < len(text) and size + len(text[end].encode()) <= max_bytes:
            size += len(text[end].encode())
            end += 1
        if end < len(text):
            cut = text.rfind(" ", start, end)
            end = cut + 1 if cut > start else end
        pieces.append((start, text[start:end]))
        start = end
    return pieces


def detect_pii(text: str, language_code: str | None = None) -> list[PiiEntity]:
    """DetectPiiEntities: type + score + character offsets per entity. Long text is chunked and offsets shifted.

    Use when you need WHERE the PII is (to mask / pseudonymize). Catch: an entity sitting on a chunk boundary
    can be missed; billed per 100-char unit with a 3-unit minimum per request.
    """
    lang = language_code or get_pii_settings().language_code
    out: list[PiiEntity] = []
    for offset, chunk in _chunks(text):
        if not chunk.strip():
            continue
        resp = _comprehend().detect_pii_entities(Text=chunk, LanguageCode=lang)
        out.extend(
            PiiEntity(e["Type"], float(e["Score"]), offset + int(e["BeginOffset"]), offset + int(e["EndOffset"]))
            for e in resp.get("Entities", [])
        )
    return out


def contains_pii(text: str, language_code: str | None = None) -> dict[str, float]:
    """ContainsPiiEntities: which types are present (labels + score), no offsets.

    Use as a cheap gate before detect + redact on traffic that is mostly PII-free. Catch: when most messages
    contain PII the gate is a wasted extra call. Only the first chunk is checked here for long text.
    """
    lang = language_code or get_pii_settings().language_code
    chunk = _chunks(text)[0][1] if text else ""
    if not chunk.strip():
        return {}
    resp = _comprehend().contains_pii_entities(Text=chunk, LanguageCode=lang)
    return {lbl["Name"]: float(lbl["Score"]) for lbl in resp.get("Labels", [])}


def redact(
    text: str, policy: RedactionPolicy, vault: PseudonymVault | None = None, precheck: bool = True
) -> RedactionResult:
    """Contains (optional gate) -> detect -> policy apply. Returns redacted text + types/counts to log."""
    if precheck and len(text.encode()) <= MAX_SYNC_BYTES:
        labels = contains_pii(text, None)
        if not any(score >= policy.threshold_for(t) for t, score in labels.items()):
            return RedactionResult(text=text)
    return redact_text(text, detect_pii(text), policy, vault)


# ================================================================ 2. async batch job (S3 -> redacted S3)


def start_redaction_job(
    input_s3_uri: str,
    output_s3_uri: str,
    policy: RedactionPolicy,
    mode: str = "ONLY_REDACTION",
    mask_mode: str = "REPLACE_WITH_PII_ENTITY_TYPE",
    input_format: str = "ONE_DOC_PER_LINE",
    job_name: str | None = None,
    client_token: str | None = None,
) -> str:
    """StartPiiEntitiesDetectionJob for corpora (pre-index scrubbing). Returns the JobId.

    mode ONLY_REDACTION (redacted copies) | ONLY_OFFSETS (entity JSON; apply your own per-type policy).
    mask_mode MASK (mask_char repeated) | REPLACE_WITH_PII_ENTITY_TYPE ([EMAIL]; better for retrieval).
    Catch: ONE mask mode for every type in the job; ClientRequestToken makes a retried start idempotent.
    """
    s = get_pii_settings()
    kwargs: Json = {
        "InputDataConfig": {"S3Uri": input_s3_uri, "InputFormat": input_format},  # ONE_DOC_PER_FILE | ONE_DOC_PER_LINE
        "OutputDataConfig": {"S3Uri": output_s3_uri, "KmsKeyId": s.kms_key_id},
        "Mode": mode,
        "DataAccessRoleArn": s.data_access_role_arn,  # Comprehend assumes it; caller needs iam:PassRole
        "JobName": job_name or f"a-pii-{uuid.uuid4().hex[:8]}",
        "LanguageCode": s.language_code,
        "ClientRequestToken": client_token or str(uuid.uuid4()),
        "Tags": [{"Key": "Component", "Value": "04.02"}],
    }
    if mode == "ONLY_REDACTION":
        kwargs["RedactionConfig"] = {
            "PiiEntityTypes": policy.redacted_types() or ["ALL"],
            "MaskMode": mask_mode,
            "MaskCharacter": policy.mask_char,  # single character; used by MASK only
        }
    resp = _comprehend().start_pii_entities_detection_job(**kwargs)
    return str(resp["JobId"])


def describe_job(job_id: str) -> Json:
    """DescribePiiEntitiesDetectionJob -> status + the job-specific output S3 URI."""
    p = _comprehend().describe_pii_entities_detection_job(JobId=job_id)["PiiEntitiesDetectionJobProperties"]
    return {
        "job_id": p.get("JobId"),
        "status": p.get("JobStatus"),  # SUBMITTED | IN_PROGRESS | COMPLETED | FAILED | STOP_REQUESTED | STOPPED
        "message": p.get("Message", ""),  # failure reason, e.g. AccessDenied on the data-access role
        "mode": p.get("Mode"),
        "output_s3_uri": p.get("OutputDataConfig", {}).get("S3Uri"),
        "redaction": p.get("RedactionConfig"),
    }


def wait_for_job(job_id: str, timeout_s: float = 3600.0) -> Json:
    """Poll with capped exponential backoff + jitter. Jobs take minutes; in prod prefer EventBridge over polling."""
    deadline = time.monotonic() + timeout_s
    attempt = 0
    while True:
        job = describe_job(job_id)
        if job["status"] in JOB_TERMINAL:
            return job
        if time.monotonic() > deadline:
            raise TimeoutError(f"PII job {job_id} still {job['status']} after {timeout_s}s")
        time.sleep(max(5.0, backoff(attempt, base=5.0, cap=60.0)))
        attempt += 1


# ================================================================ 3. reversible pseudonyms (vault adapter)


class InMemoryPseudonymVault:
    """PseudonymVault adapter: deterministic salted-HMAC tokens + an in-memory reverse map.

    token = <<TYPE_hmac_sha256(key, type:value)[:16]>>. The key is the salt: without it, low-entropy values
    (phones, SSNs) cannot be recovered by hashing every candidate. Prod: DynamoDB + KMS, audited detokenize.
    """

    def __init__(self, key: bytes, digest_chars: int = 16) -> None:
        if len(key) < 16:
            raise ValueError("HMAC key must be at least 16 bytes")
        self._key = key
        self._chars = digest_chars
        self._by_token: dict[str, str] = {}
        self._lock = threading.Lock()

    def tokenize(self, entity_type: str, value: str) -> str:
        digest = hmac.new(self._key, f"{entity_type}:{value}".encode(), hashlib.sha256).hexdigest()
        token = f"<<{entity_type}_{digest[: self._chars]}>>"
        with self._lock:
            self._by_token[token] = value
        return token

    def detokenize(self, token: str) -> str | None:
        with self._lock:
            return self._by_token.get(token)


def vault_from_settings() -> InMemoryPseudonymVault:
    key = get_pii_settings().hmac_key.encode() or os.urandom(32)  # random = tokens die with the process
    return InMemoryPseudonymVault(key)


# ================================================================ 4. streaming redactor (token-level, chunked)

Detector = Callable[[str], list[PiiEntity]]


class StreamingRedactor:
    """Redacts a chunked stream without leaking entities split across chunks.

    Holds back `window` chars; when the buffer exceeds 2 x window it detects on the whole buffer and emits the
    prefix that ends before the window, moved back to whitespace and never inside an entity.
    Catch: the user sees text `window` chars late; one detect call per flush.
    """

    def __init__(
        self,
        policy: RedactionPolicy,
        vault: PseudonymVault | None = None,
        window: int | None = None,
        detector: Detector | None = None,
    ) -> None:
        self._policy = policy
        self._vault = vault
        self._window = window or get_pii_settings().stream_window
        self._detect: Detector = detector or (lambda t: detect_pii(t))
        self._buffer = ""
        self.blocked_types: set[str] = set()

    def feed(self, chunk: str) -> str:
        self._buffer += chunk
        if len(self._buffer) < 2 * self._window:
            return ""
        entities = self._detect(self._buffer)
        cut = len(self._buffer) - self._window
        ws = self._buffer.rfind(" ", 0, cut)
        cut = ws + 1 if ws > 0 else cut
        for e in entities:  # never cut inside an entity: move the cut to its start
            if e.begin < cut < e.end:
                cut = e.begin
        if cut <= 0:
            return ""
        head = [e for e in entities if e.end <= cut]
        return self._emit(self._buffer[:cut], head, keep=self._buffer[cut:])

    def flush(self) -> str:
        """End of stream: detect on the tail and emit everything."""
        if not self._buffer:
            return ""
        return self._emit(self._buffer, self._detect(self._buffer), keep="")

    def _emit(self, text: str, entities: list[PiiEntity], keep: str) -> str:
        result = redact_text(text, entities, self._policy, self._vault)
        self._buffer = keep
        if result.blocked:
            # Mid-stream BLOCK: stop emitting the offending part; the caller ends the stream.
            self.blocked_types.update(result.blocked_types)
            return "[REDACTED]"
        return result.text


# ================================================================ 5. Bedrock calls for the pipeline


def converse_text(system: str, user_text: str, model_id: str | None = None) -> str:
    """Plain Converse (no guardrailConfig): the pipeline guards the output separately with ApplyGuardrail."""
    resp = _runtime().converse(
        modelId=model_id or get_pii_settings().model_id or get_settings().fast_model_id,
        system=[{"text": system}],
        messages=[{"role": "user", "content": [{"text": user_text}]}],
        inferenceConfig={"maxTokens": 512, "temperature": 0.2},
    )
    return "".join(c.get("text", "") for c in resp["output"]["message"]["content"])


def guard_output(text: str) -> tuple[bool, str, dict[str, int]]:
    """ApplyGuardrail(source=OUTPUT) as the PII net on the model answer.

    Returns (blocked, text_after_guardrail, pii_type_counts). ANONYMIZE hits come back masked as {EMAIL}.
    """
    s = get_pii_settings()
    try:
        resp = _runtime().apply_guardrail(
            guardrailIdentifier=s.guardrail_id,
            guardrailVersion=s.guardrail_version,
            source="OUTPUT",
            content=[{"text": {"text": text}}],
        )
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") == "ResourceNotFoundException":
            raise RuntimeError("guardrail not found: set A_PII_GUARDRAIL_ID to terraform output guardrail_id") from e
        raise
    counts: dict[str, int] = {}
    blocked = False
    for a in resp.get("assessments", []):
        sens = a.get("sensitiveInformationPolicy", {})
        for hit in sens.get("piiEntities", []) + sens.get("regexes", []):
            key = hit.get("type") or hit.get("name", "REGEX")
            counts[key] = counts.get(key, 0) + 1
            blocked = blocked or hit["action"] == "BLOCKED"
        for f in a.get("contentPolicy", {}).get("filters", []) + a.get("topicPolicy", {}).get("topics", []):
            blocked = blocked or f["action"] == "BLOCKED"
    if resp["action"] == "GUARDRAIL_INTERVENED" and resp.get("outputs"):
        text = "".join(o.get("text", "") for o in resp["outputs"])
    return blocked, text, counts

