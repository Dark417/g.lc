# pii-redaction.05streaming Token-Level Redaction and Streaming

> Span-level masking, and a hold-back window so entities split across stream chunks do not leak (lecture 26).

## Index

- [1. Token-Level Redaction](#1-token-level-redaction)
- [2. Streaming Problem](#2-streaming-problem)
- [3. Hold-Back Window](#3-hold-back-window)
  - [3.1 Code: StreamingRedactor](#31-code-streamingredactor)
- [4. Cost and Bedrock Equivalent](#4-cost-and-bedrock-equivalent)

Back to [00index](pii-redaction.00index.md).

## 1. Token-Level Redaction

Token-level = replace only the sensitive spans, keep the rest of the message usable.

- Versus message-level blocking
  - refuse everything when one entity appears
- Guardrails ANONYMIZE and Comprehend-based masking are both span-level

## 2. Streaming Problem

Per-chunk detection cannot see an entity cut in half.

→ Model output arrives in chunks: `"Call me at 555-"` then `"0142 tomorrow"`.  
→ Detect on each chunk alone.  
⇒ Neither half looks like a phone number.  
⇒ Leak.

## 3. Hold-Back Window

Delay emission by a window so detection always sees whole entities.

→ Append each chunk to a buffer.  
→ When the buffer exceeds 2 × window, run detection on the whole buffer.  
→ Emit only the prefix that ends `window` characters before the end, moved back to a whitespace and never inside an entity.  
→ Keep the tail; at end of stream, detect and flush the rest.

- Window size = longest entity you care about + margin
  - long entities (International Bank Account Number (IBAN), addresses) ⇒ larger window

### 3.1 Code: StreamingRedactor

```python
# app/infra/_04safety_02pii_redaction.py
class StreamingRedactor:
    def __init__(self, policy, vault=None, window=None, detector=None) -> None:
        self._policy = policy
        self._vault = vault
        self._window = window or get_pii_settings().stream_window  # default 64 chars
        self._detect: Detector = detector or (lambda t: detect_pii(t))
        self._buffer = ""
        self.blocked_types: set[str] = set()

    def feed(self, chunk: str) -> str:
        self._buffer += chunk
        if len(self._buffer) < 2 * self._window:
            return ""  # keep buffering
        entities = self._detect(self._buffer)
        cut = len(self._buffer) - self._window
        ws = self._buffer.rfind(" ", 0, cut)
        cut = ws + 1 if ws > 0 else cut  # move back to whitespace
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
```

- Catch
  - The detector is injectable ⇒ tests run without Amazon Web Services (AWS)

## 4. Cost and Bedrock Equivalent

- Latency
  - the user sees text `window` characters late
- Calls
  - one detect per flush
  - order of magnitude: every few hundred characters
  - batch by size, not per token
- Bedrock-native equivalent
  - `streamProcessingMode=sync` with a Guardrails Personally Identifiable Information (PII) filter
  - async mode does not mask
  - see [guardrails.06streaming](guardrails.06streaming.md)
