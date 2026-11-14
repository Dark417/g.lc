# 04safety.01guardrails.06streaming Streaming: Sync vs Async

> How `streamProcessingMode` trades time-to-first-token against leaking unchecked text.

## Index

- [1. Sync Mode](#1-sync-mode)
- [2. Async Mode](#2-async-mode)
- [3. Pick](#3-pick)
- [4. Code: Guarded Stream](#4-code-guarded-stream)

Back to [00index](04safety.01guardrails.00index.md).

## 1. Sync Mode

`streamProcessingMode="sync"` is the default.

- Bedrock buffers chunks, runs the output check, then releases them
- Pro
  - nothing unsafe reaches the user
  - Personally Identifiable Information (PII) masking works
- Con
  - time-to-first-token grows by one buffer + one check
  - order of magnitude: hundreds of ms

## 2. Async Mode

`"async"` streams first and checks behind.

- Chunks go to the user immediately
- Checks run in the background
- Hit ⇒ stream stops with `stopReason=guardrail_intervened`
  - earlier chunks are already shown
- Masking (ANONYMIZE) is not applied in async mode
  - a PII chunk can leak (User Guide, "streaming" section)

## 3. Pick

Default to sync; choose async per route.

- Default: sync
- Async only for low-risk content
  - where Time To First Token (TTFT) matters
  - and you can retract text in the User Interface (UI)
- UI must handle a mid-stream stop (retract or replace)
- PII policies force sync mode
- Non-Bedrock streaming needs your own buffering window
  - same trade-off as sync mode
  - see the hold-back window in [04safety.02pii-redaction.05streaming](04safety.02pii-redaction.05streaming.md)

## 4. Code: Guarded Stream

- The user text is wrapped in `guardContent` so only it is evaluated
- Yields text deltas, then one summary event with the stop reason and hits

```python
# app/infra/_04safety_01guardrails.py
def converse_stream_guarded(user_text: str, mode: str | None = None) -> Iterator[Json]:
    cfg = _guardrail_config() | {"streamProcessingMode": mode or get_guardrails_settings().stream_mode}  # sync | async
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
```

- Catch
  - In async mode, text yielded before the stop event is already on screen
  - Stream errors are events in the iterator, not exceptions from `converse_stream`
