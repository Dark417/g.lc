"""Domain for customization: training examples, JSONL writer and validator. No boto3 here.

Formats (the base model decides which one; check its customization page):
- prompt_completion: {"prompt": "...", "completion": "..."}                      older text models
- conversation:      {"schemaVersion": "bedrock-conversation-2024", "system": [{"text"}],
                      "messages": [{"role": "user", "content": [{"text"}]}, {"role": "assistant", ...}]}   Nova and newer
"""

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class DatasetFormat(StrEnum):
    CONVERSATION = "conversation"
    PROMPT_COMPLETION = "prompt_completion"


CONVERSATION_SCHEMA = "bedrock-conversation-2024"


@dataclass(frozen=True)
class TrainingExample:
    """One supervised pair: the exact output you want the tuned model to produce for this input."""

    prompt: str
    completion: str
    system: str = ""


@dataclass
class ValidationReport:
    records: int = 0
    errors: list[str] = field(default_factory=list)  # "line N: reason"
    duplicates: int = 0

    @property
    def ok(self) -> bool:
        return not self.errors


def to_jsonl_line(example: TrainingExample, fmt: DatasetFormat) -> str:
    """One example -> one JSON line in the base model's format."""
    if fmt == DatasetFormat.PROMPT_COMPLETION:
        record: dict[str, Any] = {"prompt": example.prompt, "completion": example.completion}
    else:
        record = {
            "schemaVersion": CONVERSATION_SCHEMA,
            "messages": [
                {"role": "user", "content": [{"text": example.prompt}]},
                {"role": "assistant", "content": [{"text": example.completion}]},
            ],
        }
        if example.system:
            record["system"] = [{"text": example.system}]
    return json.dumps(record, ensure_ascii=False)


def write_jsonl(examples: Iterable[TrainingExample], fmt: DatasetFormat) -> bytes:
    """Examples -> UTF-8 JSONL bytes (one object per line, trailing newline)."""
    return ("\n".join(to_jsonl_line(e, fmt) for e in examples) + "\n").encode("utf-8")


def validate_jsonl(data: bytes, fmt: DatasetFormat, max_record_chars: int) -> ValidationReport:
    """Local pre-flight check, so the paid job does not fail an hour in.

    Checks: UTF-8, one JSON object per line, required keys, role order (user -> assistant, ending on assistant),
    non-empty text, size guard, exact duplicates. Catch: model-specific limits (records, tokens) still apply.
    """
    report = ValidationReport()
    seen: set[str] = set()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as e:
        report.errors.append(f"not UTF-8: {e}")
        return report
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        report.records += 1
        if len(line) > max_record_chars:
            report.errors.append(f"line {n}: {len(line)} chars > {max_record_chars}")
        digest = hashlib.sha256(line.encode()).hexdigest()
        if digest in seen:
            report.duplicates += 1
        seen.add(digest)
        try:
            record = json.loads(line)
        except json.JSONDecodeError as e:
            report.errors.append(f"line {n}: invalid JSON ({e.msg})")
            continue
        if not isinstance(record, dict):
            report.errors.append(f"line {n}: not a JSON object")
            continue
        report.errors += [f"line {n}: {msg}" for msg in _check_record(record, fmt)]
    if report.records == 0:
        report.errors.append("empty dataset")
    return report


def _check_record(record: dict[str, Any], fmt: DatasetFormat) -> list[str]:
    if fmt == DatasetFormat.PROMPT_COMPLETION:
        return [f"missing or empty '{k}'" for k in ("prompt", "completion") if not str(record.get(k, "")).strip()]
    problems: list[str] = []
    if record.get("schemaVersion") != CONVERSATION_SCHEMA:
        problems.append(f"schemaVersion must be {CONVERSATION_SCHEMA}")
    messages = record.get("messages")
    if not isinstance(messages, list) or len(messages) < 2:
        return problems + ["messages must hold at least one user + assistant turn"]
    for i, m in enumerate(messages):
        expected = "user" if i % 2 == 0 else "assistant"
        if m.get("role") != expected:
            problems.append(f"message {i} role {m.get('role')!r}, expected {expected!r}")
        texts = [b.get("text", "") for b in m.get("content", []) if isinstance(b, dict)]
        if not any(t.strip() for t in texts):
            problems.append(f"message {i} has no text")
    if messages[-1].get("role") != "assistant":
        problems.append("last message must be the assistant (the target output)")
    return problems
