# converse Tool Use Loop

> The model asks for a tool, your code runs it, and you answer with the same `toolUseId`.

## Index

- [1. toolConfig](#1-toolconfig)
  - [1.1 Tool Specs](#11-tool-specs)
  - [1.2 toolChoice](#12-toolchoice)
- [2. The Loop](#2-the-loop)
  - [2.1 Steps](#21-steps)
  - [2.2 Loop Code](#22-loop-code)
  - [2.3 Running One Tool](#23-running-one-tool)
- [3. Who Runs Tools](#3-who-runs-tools)
- [4. Parallel Calls And Round Caps](#4-parallel-calls-and-round-caps)

Back to [00index](converse.00index.md).

---

## 1. toolConfig

Tools are JavaScript Object Notation (JSON)-schema specs plus a choice policy.

### 1.1 Tool Specs

- `toolConfig.tools[].toolSpec`
  - `name`
  - `description`
  - `inputSchema.json` (JSON Schema)
- Short, precise `description`s and tight schemas (`required`, `enum`)

```python
# app/service/_01bedrock_01converse.py
DEMO_TOOLS: list[ToolDefinition] = [
    ToolDefinition(
        name="get_weather",
        description="Current temperature for a city. Use only when the user asks about weather.",
        input_schema={
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name, e.g. Seattle"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},  # enum narrows the model
            },
            "required": ["city"],
        },
        handler=_get_weather,  # local function; validates its own input
    ),
    # add_numbers: "Exact sum of a list of numbers. Use instead of mental arithmetic."
]
```

### 1.2 toolChoice

- **`auto`** (default): model decides
- **`any`**: must call some tool
- **`tool: {name}`**: must call this tool
  - Forced; used for structured output, see [prompt-engineering](prompt-engineering.00index.md)
- Limit: some models support only `auto`
- Limit: some newer Claude models reject forced choice (Anthropic docs 2026-11)

```python
# app/infra/_01bedrock_01converse.py  (start of converse_with_tools)
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
```

## 2. The Loop

Each round either ends the turn or produces tool calls to answer.

### 2.1 Steps

→ call Converse with tools  
→ `stopReason = tool_use` ⇒ the assistant message holds one or more `toolUse` blocks (`toolUseId`, `name`, `input`)  
→ append that assistant message unchanged  
→ run each tool in your code (validate `input` first)  
→ append one `user` message with all `toolResult` blocks (`toolUseId`, `content: [{json}|{text}]`, `status: error` on failure)  
→ call again; stop on `end_turn` or after N rounds

### 2.2 Loop Code

```python
# app/infra/_01bedrock_01converse.py
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
    total = _add_usage(total, result.usage)  # usage summed across rounds
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
```

- Catch: forced choice must be relaxed to `auto` after the first call.
  - Otherwise the model must call the tool forever.

### 2.3 Running One Tool

- Validate `input` before executing.
- Return errors as `toolResult` with `status: error`.
  - The model can then recover or retry once.

```python
# app/infra/_01bedrock_01converse.py
@staticmethod
def _run_tool(by_name: dict[str, ToolDefinition], call: dict[str, Any]) -> dict[str, Any]:
    tool = by_name.get(call["name"])
    if tool is None:
        return {"toolResult": {"toolUseId": call["toolUseId"],
                               "content": [{"text": f"unknown tool {call['name']}"}], "status": "error"}}
    try:
        output = tool.handler(call.get("input", {}))
        return {"toolResult": {"toolUseId": call["toolUseId"], "content": [{"json": output}]}}
    except (ValueError, KeyError, TypeError) as e:  # input validation errors from the handler
        return {"toolResult": {"toolUseId": call["toolUseId"], "content": [{"text": str(e)}], "status": "error"}}
```

```python
# app/service/_01bedrock_01converse.py
def _get_weather(args: dict[str, Any]) -> dict[str, Any]:
    city = str(args["city"]).strip()
    if not city:
        raise ValueError("city must not be empty")  # becomes status=error for the model
    unit = args.get("unit", "celsius")
    if unit not in ("celsius", "fahrenheit"):
        raise ValueError("unit must be celsius or fahrenheit")
    temp_c = 18 + (sum(map(ord, city.lower())) % 10)  # fake, deterministic
    return {"city": city, "temperature": temp_c if unit == "celsius" else round(temp_c * 9 / 5 + 32), "unit": unit}
```

## 3. Who Runs Tools

- Bedrock never runs your tools; your process does

  ⇒ authorization and input validation are yours

- Least privilege
  - See [prompt-engineering](prompt-engineering.00index.md) and [guardrails](../04safety/guardrails.00index.md)

```python
# app/domain/_01bedrock_01converse.py
@dataclass(frozen=True)
class ToolDefinition:
    """A local tool the model may call. Bedrock never runs it; our process does."""
    name: str
    description: str
    input_schema: dict[str, Any]  # JSON Schema
    handler: ToolHandler          # tool input JSON -> tool result JSON
```

## 4. Parallel Calls And Round Caps

- Parallel tool calls: several `toolUse` blocks in one turn

  ⇒ answer all of them in one user message

- Cap the rounds

  ⇒ a confused model can loop forever and burn tokens

```python
# app/config/_01bedrock_01converse.py
max_tool_rounds: int = 5  # hard cap on the tool-use loop
```
