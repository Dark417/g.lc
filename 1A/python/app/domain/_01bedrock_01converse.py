"""Domain for the Converse slice: result models, stream events, the conversation-store port.

- No boto3 here. Bedrock messages are plain dicts in the Converse wire shape:
  {"role": "user" | "assistant", "content": [{"text": ...} | {"toolUse": ...} | {"toolResult": ...} | ...]}
- The store is a port (Protocol): the in-memory adapter lives in infra.py; DynamoDB is the production adapter.
"""

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol

Message = dict[str, Any]  # one Converse message (role + content blocks)
ToolHandler = Callable[[dict[str, Any]], dict[str, Any]]  # tool input JSON -> tool result JSON


class StopReason(StrEnum):
    """Every stopReason Converse can return (botocore bedrock-runtime model, 2026-11)."""

    END_TURN = "end_turn"  # model finished
    TOOL_USE = "tool_use"  # model wants tool results before it continues
    MAX_TOKENS = "max_tokens"  # truncated by inferenceConfig.maxTokens
    STOP_SEQUENCE = "stop_sequence"  # hit one of inferenceConfig.stopSequences
    GUARDRAIL_INTERVENED = "guardrail_intervened"  # guardrail blocked/masked (04.01)
    CONTENT_FILTERED = "content_filtered"  # provider-side filter
    MALFORMED_MODEL_OUTPUT = "malformed_model_output"
    MALFORMED_TOOL_USE = "malformed_tool_use"
    MODEL_CONTEXT_WINDOW_EXCEEDED = "model_context_window_exceeded"


@dataclass(frozen=True)
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cache_read_input_tokens: int = 0  # > 0 proves a cachePoint prefix was reused
    cache_write_input_tokens: int = 0


@dataclass(frozen=True)
class ConverseResult:
    text: str
    stop_reason: str
    usage: Usage
    latency_ms: int  # metrics.latencyMs = server-side time for the whole call
    message: Message  # the assistant message, to append unchanged to history
    tool_calls: list[dict[str, Any]] = field(default_factory=list)  # toolUse blocks, if any
    rounds: int = 1  # model calls made (tool loop)


@dataclass(frozen=True)
class StreamEvent:
    """One normalized ConverseStream event.

    kind: "text" (delta), "tool_use" (complete tool input at block stop), "stop" (stopReason), "metadata" (usage).
    """

    kind: str
    text: str = ""
    tool_use: dict[str, Any] | None = None
    stop_reason: str = ""
    usage: Usage | None = None
    latency_ms: int = 0


@dataclass(frozen=True)
class ModelInfo:
    model_id: str
    provider: str
    input_modalities: list[str]
    output_modalities: list[str]
    streaming: bool
    inference_types: list[str]  # ON_DEMAND, PROVISIONED (INFERENCE_PROFILE-only models show neither)
    lifecycle: str  # ACTIVE | LEGACY


@dataclass(frozen=True)
class ToolDefinition:
    """A local tool the model may call. Bedrock never runs it; our process does."""

    name: str
    description: str
    input_schema: dict[str, Any]  # JSON Schema
    handler: ToolHandler


class ConverseError(Exception):
    """Non-retryable request problem (ValidationException, AccessDenied): fix the request, don't retry."""


# ---------------------------------------------------------------- conversation store port


class ConversationStore(Protocol):
    """History per conversation. Converse is stateless: the caller resends history every turn.

    Production adapter: DynamoDB, PK=CONV#<id>, SK=MSG#<zero-padded seq>, TTL on expiresAt,
    one item per message (400 KB item cap ⇒ large documents go to S3, store a pointer).
    """

    def load(self, conversation_id: str) -> list[Message]: ...

    def append(self, conversation_id: str, messages: list[Message]) -> None: ...

    def clear(self, conversation_id: str) -> None: ...


def trim_history(messages: list[Message], max_messages: int) -> list[Message]:
    """Sliding window that keeps Converse's role rules valid.

    - Converse requires the first message to be "user" and roles to alternate.
    - A toolResult user message must follow its toolUse assistant message, so never start on one.
    Catch: a window by count ignores tokens; a token budget (CountTokens) is the precise version.
    """
    if len(messages) <= max_messages:
        return messages
    window = messages[-max_messages:]
    while window and (window[0]["role"] != "user" or _has_tool_result(window[0])):
        window = window[1:]
    return window


def _has_tool_result(message: Message) -> bool:
    return any("toolResult" in block for block in message.get("content", []))


_DOC_NAME_BAD = re.compile(r"[^A-Za-z0-9\s\-\(\)\[\]]")
_SPACES = re.compile(r"\s+")


def safe_document_name(filename: str) -> str:
    """DocumentBlock.name allows letters, digits, single whitespace, hyphens, parentheses, square brackets.

    The name is also shown to the model ⇒ treat it as untrusted text (prompt-injection surface).
    """
    stem = filename.rsplit(".", 1)[0]
    cleaned = _SPACES.sub(" ", _DOC_NAME_BAD.sub("-", stem)).strip()
    return (cleaned or "document")[:200]
