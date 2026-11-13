"""Bedrock Converse showcase (boto3): one method per scenario, in the order of docs/01.01.bedrock-converse.md.

- Two clients: "bedrock" (control plane: list models/profiles) and "bedrock-runtime" (data plane: inference).
- boto3 takes raw bytes for image/document blocks (it base64-encodes on the wire); never pre-encode.
- IAM: Converse = bedrock:InvokeModel, ConverseStream = bedrock:InvokeModelWithResponseStream
  (terraform/01.01.bedrock-converse.tf).
- No AWS call at import time: clients are created on first use via app.shared.aws.
"""

import json
from collections.abc import Iterator
from typing import Any

from botocore.exceptions import ClientError, EventStreamError, ReadTimeoutError

from app.a01_01_converse.config import ConverseSettings, get_converse_settings
from app.a01_01_converse.domain import (
    ConversationStore,
    ConverseError,
    ConverseResult,
    Message,
    ModelInfo,
    StopReason,
    StreamEvent,
    ToolDefinition,
    Usage,
    safe_document_name,
)
from app.shared import aws
from app.shared.retry import call_with_retry

# Retryable error codes. ModelTimeoutException is retryable only if the cause is transient;
# a prompt that always needs > timeout must shrink (maxTokens) or stream instead.
RETRYABLE_CODES = {
    "ThrottlingException",  # 429: RPM/TPM quota for this model in this Region
    "ServiceUnavailableException",  # 503: capacity
    "InternalServerException",  # 500
    "ModelNotReadyException",  # 429: model (often custom/imported) still loading
    "ModelTimeoutException",  # 408: generation too slow
}
NON_RETRYABLE_CODES = {"ValidationException", "AccessDeniedException", "ResourceNotFoundException"}

ANTHROPIC_BEDROCK_VERSION = "bedrock-2023-05-31"  # required "anthropic_version" in native Claude bodies


# ================================================================ parsing helpers


def parse_usage(raw: dict[str, Any] | None) -> Usage:
    raw = raw or {}
    return Usage(
        input_tokens=raw.get("inputTokens", 0),
        output_tokens=raw.get("outputTokens", 0),
        total_tokens=raw.get("totalTokens", 0),
        cache_read_input_tokens=raw.get("cacheReadInputTokens", 0),
        cache_write_input_tokens=raw.get("cacheWriteInputTokens", 0),
    )


def parse_converse_response(resp: dict[str, Any], rounds: int = 1) -> ConverseResult:
    """Converse response -> ConverseResult: text, stopReason, usage, latency, toolUse blocks."""
    message: Message = resp["output"]["message"]
    blocks = message.get("content", [])
    return ConverseResult(
        text="".join(b["text"] for b in blocks if "text" in b),
        stop_reason=resp["stopReason"],
        usage=parse_usage(resp.get("usage")),
        latency_ms=resp.get("metrics", {}).get("latencyMs", 0),
        message=message,
        tool_calls=[b["toolUse"] for b in blocks if "toolUse" in b],
        rounds=rounds,
    )


def error_code(e: Exception) -> str:
    # EventStreamError (mid-stream error event) subclasses ClientError, so both land here.
    if isinstance(e, (ClientError, EventStreamError)):
        return e.response.get("Error", {}).get("Code", "")
    return ""


def is_retryable(e: Exception) -> bool:
    """Predicate for app.shared.retry: retry capacity/transient errors, never request errors."""
    if isinstance(e, ReadTimeoutError):
        return True
    return error_code(e) in RETRYABLE_CODES


def user_text(text: str) -> Message:
    return {"role": "user", "content": [{"text": text}]}


class ConverseShowcase:
    def __init__(self, settings: ConverseSettings | None = None) -> None:
        self.settings = settings or get_converse_settings()

    # ---------------------------------------------------------------- clients (lazy)

    @property
    def runtime(self) -> Any:
        """Data plane: Converse, ConverseStream, InvokeModel. Shared client = shared adaptive rate limiter."""
        return aws.client("bedrock-runtime")

    @property
    def control(self) -> Any:
        """Control plane: models, inference profiles, customization, provisioned throughput."""
        return aws.client("bedrock")

    def inference_config(self, max_tokens: int | None = None, stop: list[str] | None = None) -> dict[str, Any]:
        """inferenceConfig: maxTokens (output cap), temperature (0..1), topP (0..1), stopSequences (max 4 on many models).

        Catch: some newer models reject temperature/topP ⇒ send_sampling=False drops them.
        """
        cfg: dict[str, Any] = {"maxTokens": max_tokens or self.settings.max_tokens}
        if self.settings.send_sampling:
            cfg["temperature"] = self.settings.temperature
            cfg["topP"] = self.settings.top_p
        if stop:
            cfg["stopSequences"] = stop
        return cfg

    # ================================================================ 1.4 model access and model IDs

    def list_foundation_models(
        self,
        provider: str | None = None,
        output_modality: str | None = None,
        inference_type: str | None = None,
        customization: str | None = None,
    ) -> list[ModelInfo]:
        """Shows: ListFoundationModels filters + lifecycle. Use to validate config at startup or alarm on LEGACY.

        Filters (all optional): byProvider ("Anthropic", "Amazon", "Meta", ...), byOutputModality (TEXT | IMAGE |
        EMBEDDING), byInferenceType (ON_DEMAND | PROVISIONED), byCustomizationType (FINE_TUNING |
        CONTINUED_PRE_TRAINING | DISTILLATION). Catch: not paginated, and lists models in this Region only;
        a model offered only via an inference profile shows inferenceTypesSupported=["INFERENCE_PROFILE"].
        """
        kwargs: dict[str, str] = {}
        if provider:
            kwargs["byProvider"] = provider
        if output_modality:
            kwargs["byOutputModality"] = output_modality
        if inference_type:
            kwargs["byInferenceType"] = inference_type
        if customization:
            kwargs["byCustomizationType"] = customization
        resp = self.control.list_foundation_models(**kwargs)
        return [
            ModelInfo(
                model_id=m["modelId"],
                provider=m.get("providerName", ""),
                input_modalities=m.get("inputModalities", []),
                output_modalities=m.get("outputModalities", []),
                streaming=m.get("responseStreamingSupported", False),
                inference_types=m.get("inferenceTypesSupported", []),
                lifecycle=m.get("modelLifecycle", {}).get("status", ""),
            )
            for m in resp["modelSummaries"]
        ]

    def list_inference_profiles(self, type_equals: str = "SYSTEM_DEFINED") -> list[dict[str, str]]:
        """Shows: inference profiles, paginated by nextToken. SYSTEM_DEFINED = us./eu./apac./global. cross-Region;
        APPLICATION = your tagged copies (a-app-profile). Catch: the profile's model list shows which Regions
        it can route to ⇒ IAM must allow the foundation model in each of them.
        """
        profiles: list[dict[str, str]] = []
        token: str | None = None
        while True:
            kwargs: dict[str, Any] = {"typeEquals": type_equals, "maxResults": 100}
            if token:
                kwargs["nextToken"] = token
            resp = self.control.list_inference_profiles(**kwargs)
            for p in resp.get("inferenceProfileSummaries", []):
                profiles.append(
                    {
                        "id": p["inferenceProfileId"],
                        "arn": p["inferenceProfileArn"],
                        "regions": ",".join(m["modelArn"].split(":")[3] for m in p.get("models", [])),
                    }
                )
            token = resp.get("nextToken")
            if not token:  # only a missing nextToken means the last page
                return profiles

    # ================================================================ 1.6 basic Converse

    def converse_basic(
        self,
        prompt: str,
        system: str = "You are a concise assistant for backend engineers.",
        model_id: str | None = None,
        max_tokens: int | None = None,
        stop_sequences: list[str] | None = None,
    ) -> ConverseResult:
        """Shows: one Converse call with system prompt + inferenceConfig, and the parsed usage/latency/stopReason.
        Use for any single-shot task. Catch: check stop_reason == max_tokens before trusting the text.
        """
        resp = self.runtime.converse(
            modelId=model_id or self.settings.text_model(),  # model ID, profile ID, or profile/provisioned ARN
            system=[{"text": system}],  # list of blocks; some models don't support system prompts
            messages=[user_text(prompt)],
            inferenceConfig=self.inference_config(max_tokens, stop_sequences),
            # Provider-specific keys Converse does not model (Anthropic example): top_k sampling cutoff.
            # additionalModelRequestFields={"top_k": 250},
            # JSON pointers into the native response, returned in additionalModelResponseFields:
            # additionalModelResponseFieldPaths=["/stop_sequence"],
            requestMetadata={"feature": "converse-basic"},  # lands in invocation logs (05.01) for filtering
        )
        return parse_converse_response(resp)

    def converse_messages(self, messages: list[Message], system: str, model_id: str | None = None) -> ConverseResult:
        """Shows: Converse over a full history (multi-turn). Used by service.ChatService with the store port.
        Catch: the API is stateless ⇒ input tokens grow every turn; trim or summarize.
        """
        resp = self.runtime.converse(
            modelId=model_id or self.settings.text_model(),
            system=[{"text": system}],
            messages=messages,
            inferenceConfig=self.inference_config(),
        )
        return parse_converse_response(resp)

    def converse_cached_system(self, long_system: str, prompt: str) -> ConverseResult:
        """Shows: prompt caching with a cachePoint block after a long, stable system prompt.
        Use when many calls share a big prefix (policy text, a document). Catch: below the model's minimum
        prefix length nothing is cached; verify usage.cache_read_input_tokens > 0 on the second call.
        """
        resp = self.runtime.converse(
            modelId=self.settings.text_model(),
            system=[{"text": long_system}, {"cachePoint": {"type": "default"}}],  # everything above is cacheable
            messages=[user_text(prompt)],
            inferenceConfig=self.inference_config(),
        )
        return parse_converse_response(resp)

    def converse_via_app_profile(self, prompt: str) -> ConverseResult:
        """Shows: calling through the application inference profile (a-app-profile) for cost allocation tags.
        Catch: modelId is the profile ARN; IAM must allow that ARN (01.01 .tf does).
        """
        arn = self.settings.app_profile_arn
        if not arn:
            raise ConverseError("A_CONVERSE_APP_PROFILE_ARN is not set (terraform output converse_app_profile_arn)")
        return self.converse_basic(prompt, model_id=arn)

    # ================================================================ 1.7 ConverseStream

    def converse_stream(self, prompt: str, system: str = "You are a concise assistant.") -> Iterator[StreamEvent]:
        """Shows: ConverseStream event handling: text deltas, tool input assembly, messageStop, metadata.
        Use for every user-facing answer (time to first token). Catch: errors can arrive mid-stream after
        HTTP 200 (botocore raises EventStreamError while iterating) ⇒ treat partial output as failed.
        """
        resp = self.runtime.converse_stream(
            modelId=self.settings.text_model(),
            system=[{"text": system}],
            messages=[user_text(prompt)],
            inferenceConfig=self.inference_config(),
        )
        tool_parts: dict[int, dict[str, Any]] = {}  # contentBlockIndex -> {"toolUseId", "name", "input": str}
        for event in resp["stream"]:
            if "messageStart" in event:
                continue  # {"role": "assistant"}
            if "contentBlockStart" in event:
                start = event["contentBlockStart"]
                if "toolUse" in start.get("start", {}):
                    tu = start["start"]["toolUse"]
                    tool_parts[start["contentBlockIndex"]] = {"toolUseId": tu["toolUseId"], "name": tu["name"], "input": ""}
            elif "contentBlockDelta" in event:
                d = event["contentBlockDelta"]
                delta = d["delta"]
                if "text" in delta:
                    yield StreamEvent(kind="text", text=delta["text"])
                elif "toolUse" in delta:  # partial JSON string: concatenate, parse at block stop
                    tool_parts[d["contentBlockIndex"]]["input"] += delta["toolUse"].get("input", "")
                # "reasoningContent" deltas (reasoning models) are ignored here
            elif "contentBlockStop" in event:
                idx = event["contentBlockStop"]["contentBlockIndex"]
                if idx in tool_parts:
                    part = tool_parts.pop(idx)
                    part["input"] = json.loads(part["input"] or "{}")
                    yield StreamEvent(kind="tool_use", tool_use=part)
            elif "messageStop" in event:
                yield StreamEvent(kind="stop", stop_reason=event["messageStop"]["stopReason"])
            elif "metadata" in event:  # always last: usage + latency
                meta = event["metadata"]
                yield StreamEvent(
                    kind="metadata",
                    usage=parse_usage(meta.get("usage")),
                    latency_ms=meta.get("metrics", {}).get("latencyMs", 0),
                )

    # ================================================================ 1.8 tool use loop

    def converse_with_tools(
        self,
        prompt: str,
        tools: list[ToolDefinition],
        tool_choice: str = "auto",
        forced_tool: str | None = None,
    ) -> ConverseResult:
        """Shows: the full toolUse -> toolResult loop with toolConfig and toolChoice, capped at max_tool_rounds.
        toolChoice: "auto" (model decides, default) | "any" (must call some tool) | {"tool": {"name"}} (forced).
        Catch: Bedrock never runs tools; validate inputs here. Some models support only "auto".
        """
        by_name = {t.name: t for t in tools}
        choice: dict[str, Any]
        if forced_tool:
            choice = {"tool": {"name": forced_tool}}
        elif tool_choice == "any":
            choice = {"any": {}}
        else:
            choice = {"auto": {}}
        tool_config = {
            "tools": [
                {"toolSpec": {"name": t.name, "description": t.description, "inputSchema": {"json": t.input_schema}}}
                for t in tools
            ],
            "toolChoice": choice,
        }
        messages: list[Message] = [user_text(prompt)]
        total = Usage()
        for round_no in range(1, self.settings.max_tool_rounds + 1):
            resp = self.runtime.converse(
                modelId=self.settings.text_model(),
                system=[{"text": "Use the tools when they help. Answer briefly."}],
                messages=messages,
                inferenceConfig=self.inference_config(),
                toolConfig=tool_config,  # must be sent on EVERY call that has toolUse/toolResult in history
            )
            result = parse_converse_response(resp, rounds=round_no)
            total = _add_usage(total, result.usage)
            messages.append(result.message)  # assistant message unchanged (text + toolUse blocks)
            if result.stop_reason != StopReason.TOOL_USE:
                return _with_usage(result, total)
            # Answer EVERY toolUse of this turn in ONE user message (parallel tool calls).
            results = [self._run_tool(by_name, call) for call in result.tool_calls]
            messages.append({"role": "user", "content": results})
            if forced_tool:
                # After a forced call the next request must allow a normal answer, or it loops forever.
                tool_config = {**tool_config, "toolChoice": {"auto": {}}}
        raise ConverseError(f"tool loop exceeded {self.settings.max_tool_rounds} rounds")

    @staticmethod
    def _run_tool(by_name: dict[str, ToolDefinition], call: dict[str, Any]) -> dict[str, Any]:
        """Executes one toolUse block; failures go back as status=error so the model can recover."""
        tool = by_name.get(call["name"])
        if tool is None:
            return {"toolResult": {"toolUseId": call["toolUseId"], "content": [{"text": f"unknown tool {call['name']}"}], "status": "error"}}
        try:
            output = tool.handler(call.get("input", {}))
            return {"toolResult": {"toolUseId": call["toolUseId"], "content": [{"json": output}]}}
        except (ValueError, KeyError, TypeError) as e:  # input validation errors from the handler
            return {"toolResult": {"toolUseId": call["toolUseId"], "content": [{"text": str(e)}], "status": "error"}}

    # ================================================================ 1.9 multimodal blocks

    def converse_image(self, image: bytes, image_format: str, question: str) -> ConverseResult:
        """Shows: an image content block (format png | jpeg | gif | webp, raw bytes). Image first, question after.
        Catch: images cost input tokens by pixel count; resize first. Size/count limits are per model.
        """
        if image_format not in {"png", "jpeg", "gif", "webp"}:
            raise ConverseError(f"unsupported image format {image_format}")
        resp = self.runtime.converse(
            modelId=self.settings.text_model(),
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"image": {"format": image_format, "source": {"bytes": image}}},
                        # {"image": {"format": ..., "source": {"s3Location": {"uri": "s3://..."}}}}  # some models only (Nova)
                        {"text": question},
                    ],
                }
            ],
            inferenceConfig=self.inference_config(),
        )
        return parse_converse_response(resp)

    def converse_document(self, document: bytes, doc_format: str, filename: str, question: str) -> ConverseResult:
        """Shows: a document block (pdf | csv | doc | docx | xls | xlsx | html | txt | md) with a sanitized name.
        Use for one-off document Q&A; use RAG (02.x) for corpora. Catch: name chars are restricted and the name
        reaches the model; limits on count/size are per model (order of magnitude: a few docs of a few MB).
        """
        resp = self.runtime.converse(
            modelId=self.settings.text_model(),
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "document": {
                                "format": doc_format,
                                "name": safe_document_name(filename),
                                "source": {"bytes": document},
                                # "citations": {"enabled": True},  # models that support citation blocks
                            }
                        },
                        {"text": question},  # a text block is required alongside a document
                    ],
                }
            ],
            inferenceConfig=self.inference_config(),
        )
        return parse_converse_response(resp)

    # ================================================================ 1.5 InvokeModel for contrast

    def invoke_model_anthropic(self, prompt: str, system: str = "You are concise.") -> dict[str, Any]:
        """Shows: InvokeModel with Anthropic's native Messages body; the response is native JSON too.
        Use only for native-only features; swapping to Nova means rewriting this method. Catch: field names
        differ from Converse (max_tokens vs maxTokens, stop_reason vs stopReason).
        """
        body = {
            "anthropic_version": ANTHROPIC_BEDROCK_VERSION,
            "max_tokens": self.settings.max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        }
        resp = self.runtime.invoke_model(
            modelId=self.settings.text_model(),
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
        native = json.loads(resp["body"].read())  # StreamingBody: read once
        return {
            "text": "".join(c.get("text", "") for c in native.get("content", [])),
            "stop_reason": native.get("stop_reason"),  # end_turn | max_tokens | stop_sequence | tool_use
            "usage": native.get("usage", {}),  # {"input_tokens", "output_tokens", ...}
            # Token counts are also returned as HTTP headers on InvokeModel:
            "header_input_tokens": resp["ResponseMetadata"]["HTTPHeaders"].get("x-amzn-bedrock-input-token-count"),
        }

    # ================================================================ 1.10 errors and retries

    def converse_with_retry(self, prompt: str) -> ConverseResult:
        """Shows: error classification + app-level retry with full jitter on top of the SDK's adaptive retries.
        Retry: Throttling, ServiceUnavailable, InternalServer, ModelNotReady, ModelTimeout. Never: Validation,
        AccessDenied. Catch: retries multiply under load (SDK 5 x app 3) ⇒ keep the product small.
        """
        try:
            return call_with_retry(
                lambda: self.converse_basic(prompt),
                retryable=is_retryable,
                max_attempts=self.settings.app_retry_attempts,
                base=0.5,
                cap=8.0,
            )
        except ClientError as e:
            code = error_code(e)
            if code in NON_RETRYABLE_CODES:
                # e.g. roles not alternating, unsupported field for this model, bare ID of a profile-only model
                raise ConverseError(f"{code}: {e.response['Error'].get('Message', '')}") from e
            raise  # retryable but exhausted: let the caller shed load / fall back to the fast model


def _add_usage(a: Usage, b: Usage) -> Usage:
    return Usage(
        a.input_tokens + b.input_tokens,
        a.output_tokens + b.output_tokens,
        a.total_tokens + b.total_tokens,
        a.cache_read_input_tokens + b.cache_read_input_tokens,
        a.cache_write_input_tokens + b.cache_write_input_tokens,
    )


def _with_usage(result: ConverseResult, usage: Usage) -> ConverseResult:
    return ConverseResult(
        text=result.text,
        stop_reason=result.stop_reason,
        usage=usage,
        latency_ms=result.latency_ms,
        message=result.message,
        tool_calls=result.tool_calls,
        rounds=result.rounds,
    )


# ================================================================ conversation store adapter


class InMemoryConversationStore(ConversationStore):
    """Adapter for the ConversationStore port: dict in process memory (dev/tests only).

    Production: DynamoDB adapter (PK=CONV#<id>, SK=MSG#<seq>, TTL) so any instance can serve the next turn.
    Catch: lost on restart and not shared across replicas.
    """

    def __init__(self) -> None:
        self._data: dict[str, list[Message]] = {}

    def load(self, conversation_id: str) -> list[Message]:
        return list(self._data.get(conversation_id, []))

    def append(self, conversation_id: str, messages: list[Message]) -> None:
        self._data.setdefault(conversation_id, []).extend(messages)

    def clear(self, conversation_id: str) -> None:
        self._data.pop(conversation_id, None)
