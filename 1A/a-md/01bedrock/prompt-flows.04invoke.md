# prompt-flows Invoking A Flow

> `InvokeFlow` on an alias returns an event stream of outputs, completion, traces, and errors.

## Index

- [1. The Call](#1-the-call)
- [2. Response Events](#2-response-events)
- [3. Parsing The Stream](#3-parsing-the-stream)
- [4. Multi-Turn](#4-multi-turn)
- [5. Limit](#5-limit)

Back to [00index](prompt-flows.00index.md).

---

## 1. The Call

- `bedrock-agent-runtime.invoke_flow(...)`
  - `flowIdentifier`
  - `flowAliasIdentifier`
  - `inputs`
  - `enableTrace`
  - `executionId`
- The input `content` must match the Input node's declared type.

## 2. Response Events

The response is an event stream.

- **`flowOutputEvent`**: `nodeName`, `nodeType`, `content.document` (the result)
  - One per Output node
- **`flowCompletionEvent`**: `completionReason = SUCCESS` or `INPUT_REQUIRED`
- **`flowMultiTurnInputRequestEvent`**: an Agent node asks the caller for more input
- **`flowTraceEvent`** (with `enableTrace`)
  - node inputs/outputs
  - condition results
  - timings
- Errors inside the stream
  - `throttlingException`, `validationException`
  - `dependencyFailedException`, `badGatewayException`, ...

⇒ errors arrive after Hypertext Transfer Protocol (HTTP) 200  
⇒ outputs seen before an error are partial

## 3. Parsing The Stream

```python
# app/infra/_01bedrock_04prompt_flows.py
STREAM_ERRORS = (
    "throttlingException", "validationException", "accessDeniedException",
    "resourceNotFoundException", "serviceQuotaExceededException", "conflictException",
    "dependencyFailedException",  # a node's dependency (model, Lambda, KB) failed
    "badGatewayException", "internalServerException",
)

def invoke_flow(self, document: str, alias_id: str | None = None, flow_id: str | None = None) -> FlowRun:
    try:
        resp = self.agent_runtime.invoke_flow(
            flowIdentifier=flow_id or self.settings.flow_id,
            flowAliasIdentifier=alias_id or self.settings.flow_alias_id,  # an alias, never the DRAFT
            inputs=[{
                "nodeName": INPUT_NODE,
                "nodeOutputName": INPUT_OUTPUT_NAME,  # the Input node's output
                "content": {"document": document},    # must match the Input node's declared type
            }],
            enableTrace=self.settings.enable_trace,
            # executionId="...",  # continue a multi-turn execution after INPUT_REQUIRED
        )
    except ClientError as e:
        raise FlowError(f"{e.response['Error']['Code']}: {e.response['Error'].get('Message', '')}") from e

    run = FlowRun(execution_id=resp.get("executionId", ""))
    for event in resp["responseStream"]:
        if "flowOutputEvent" in event:
            out = event["flowOutputEvent"]
            run.outputs[out["nodeName"]] = out["content"]["document"]
        elif "flowCompletionEvent" in event:
            run.completion_reason = event["flowCompletionEvent"]["completionReason"]
        elif "flowMultiTurnInputRequestEvent" in event:
            req = event["flowMultiTurnInputRequestEvent"]
            run.input_request = {"node": req["nodeName"], "content": req["content"].get("document")}
        elif "flowTraceEvent" in event:
            run.traces.append(event["flowTraceEvent"]["trace"])
        else:
            for err in STREAM_ERRORS:  # error event after HTTP 200
                if err in event:
                    raise FlowError(f"{err}: {event[err].get('message', '')} (partial outputs: {list(run.outputs)})")
    return run
```

```python
# app/domain/_01bedrock_04prompt_flows.py
@dataclass
class FlowRun:
    execution_id: str = ""
    outputs: dict[str, Any] = field(default_factory=dict)  # Output node name -> content.document
    completion_reason: str = ""                            # SUCCESS | INPUT_REQUIRED
    input_request: dict[str, Any] | None = None            # multi-turn: an Agent node asks for more input
    traces: list[dict[str, Any]] = field(default_factory=list)
```

```python
# app/config/_01bedrock_04prompt_flows.py
enable_trace: bool = False  # traces show node inputs/outputs: great for debugging, may contain PII
```

- Catch: traces may contain Personally Identifiable Information (PII).
  - Enable in test, sample in production.

## 4. Multi-Turn

- `executionId` continues a multi-turn execution
- Trigger: `completionReason = INPUT_REQUIRED` from an Agent node

## 5. Limit

- Synchronous call with a timeout
  - Order of magnitude: minutes
- Long jobs need async patterns elsewhere
  - e.g. Step Functions ([98 trade-offs](prompt-flows.98tradeoffs.md))
