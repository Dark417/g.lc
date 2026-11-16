# converse ConverseStream Events

> The same request as Converse, answered as an event stream that can fail halfway.

## Index

- [1. Event Order](#1-event-order)
- [2. Handling The Stream](#2-handling-the-stream)
  - [2.1 Mid-Stream Errors](#21-mid-stream-errors)
  - [2.2 Tool Input Fragments](#22-tool-input-fragments)
  - [2.3 Code](#23-code)
- [3. Why Stream](#3-why-stream)
- [4. Serving It As Server-Sent Events (SSE)](#4-serving-it-as-server-sent-events-sse)
- [5. Limit](#5-limit)

Back to [00index](converse.00index.md).

---

## 1. Event Order

Same request; the response is an event stream over Hypertext Transfer Protocol (HTTP)/2-style chunked frames.

→ `messageStart` (role)  
→ `contentBlockStart` (only for tool use and some block types; carries `toolUseId`, `name`)  
→ `contentBlockDelta` ×N (`text`, or `toolUse.input` as partial JavaScript Object Notation (JSON) string, or `reasoningContent`)  
→ `contentBlockStop` (block index)  
→ `messageStop` (`stopReason`)  
→ `metadata` (`usage`, `metrics.latencyMs`)

- Usage arrives last
  - Handle `messageStop` and `metadata` separately

## 2. Handling The Stream

Two traps: errors after HTTP 200, and tool input that arrives in pieces.

### 2.1 Mid-Stream Errors

- Error events arrive inside the stream
  - `throttlingException`
  - `modelStreamErrorException`
  - `validationException`
  - `internalServerException`
  - `serviceUnavailableException`

⇒ a 200 response can still fail halfway  
⇒ the client must handle mid-stream errors

- botocore raises `EventStreamError` while iterating
  - Treat partial output as failed

### 2.2 Tool Input Fragments

- Tool input arrives as string fragments

→ concatenate per block index  
→ `json.loads` only at `contentBlockStop`

### 2.3 Code

```python
# app/infra/_01bedrock_01converse.py
def converse_stream(self, prompt: str, system: str = "You are a concise assistant.") -> Iterator[StreamEvent]:
    resp = self.runtime.converse_stream(
        modelId=self.settings.text_model(),
        system=[{"text": system}],
        messages=[user_text(prompt)],
        inferenceConfig=self.inference_config(),
    )
    tool_parts: dict[int, dict[str, Any]] = {}  # contentBlockIndex -> {"toolUseId", "name", "input": str}
    for event in resp["stream"]:  # EventStreamError can be raised here, after HTTP 200
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
            yield StreamEvent(kind="metadata", usage=parse_usage(meta.get("usage")),
                              latency_ms=meta.get("metrics", {}).get("latencyMs", 0))
```

```python
# app/domain/_01bedrock_01converse.py
@dataclass(frozen=True)
class StreamEvent:
    """kind: "text" (delta), "tool_use" (complete input at block stop), "stop" (stopReason), "metadata" (usage)."""
    kind: str
    text: str = ""
    tool_use: dict[str, Any] | None = None
    stop_reason: str = ""
    usage: Usage | None = None
    latency_ms: int = 0
```

- Catch: `reasoningContent` deltas are ignored in this code.

## 3. Why Stream

Streaming changes perceived latency, not cost.

- Time to first token drops from "whole answer" to "first chunk"
  - Order of magnitude: sub-second vs seconds
- Total latency and cost are the same
- Stream every user-facing answer

## 4. Serving It As Server-Sent Events (SSE)

- The Representational State Transfer (REST) adapter forwards each normalized event as Server-Sent Events.
- One event per text delta, then stop + usage.

```python
# app/api/_01bedrock_01converse.py
@router.post("/stream")
def stream(body: PromptRequest, showcase: Showcase) -> StreamingResponse:
    def sse() -> Iterator[str]:
        for event in showcase.converse_stream(body.prompt, body.system):
            payload = {k: v for k, v in asdict(event).items() if v not in ("", None, 0)}
            yield f"event: {event.kind}\ndata: {json.dumps(payload)}\n\n"

    return StreamingResponse(sse(), media_type="text/event-stream")
```

## 5. Limit

- Guardrails on streams run in one of two modes
  - Async: sends chunks before the check
  - Sync: buffers
- See [guardrails](../04safety/guardrails.00index.md)
