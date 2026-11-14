# 01bedrock.05prompt-engineering Structured Output

> Four ways to get JavaScript Object Notation (JSON), most to least reliable, and why you validate even when the decoder is constrained.

## Index

- [1. Options Ranked](#1-options-ranked)
- [2. Native JSON Schema](#2-native-json-schema)
- [3. Forced Tool Use](#3-forced-tool-use)
- [4. JSON In Prompt + Validate + Repair](#4-json-in-prompt--validate--repair)
- [5. Prefill](#5-prefill)
- [6. Always Validate](#6-always-validate)
- [7. Design The Schema For The Model](#7-design-the-schema-for-the-model)

Back to [00index](01bedrock.05prompt-engineering.00index.md).

---

## 1. Options Ranked

Most to least reliable:

→ native JSON-schema output (`outputConfig`)  
→ forced tool use with your schema  
→ JSON in the prompt + validate + repair  
→ prefill `{`

- Every path still validates with Pydantic, then with business rules
- Per-model capability flags pick the path

```python
# app/config/_01bedrock_05prompt_engineering.py
supports_forced_tool: bool = True     # False for models that only accept toolChoice=auto
supports_native_schema: bool = False  # True where Converse outputConfig json_schema is supported
max_repairs: int = 2                  # validate-and-repair retries (each = one more model call)
```

## 2. Native JSON Schema

The decoder is constrained to the schema.

- Converse `outputConfig.textFormat = {type: json_schema, structure.jsonSchema}`
- The answer arrives as JSON text in a text block

```python
# app/infra/_01bedrock_05prompt_engineering.py
def extract_with_native_schema(self, document_text: str) -> Invoice:
    if not self.settings.supports_native_schema:
        raise StructuredOutputError("native JSON-schema output disabled for this model")
    resp = self._converse(
        [{"role": "user", "content": [{"text": f"<document>\n{document_text}\n</document>\n\nExtract the invoice."}]}],
        "You extract invoice data. Use null for fields that are not present.",
        outputConfig={
            "textFormat": {
                "type": "json_schema",  # only allowed value today
                "structure": {
                    "jsonSchema": {
                        "name": "invoice",
                        "description": "Fields of one invoice",
                        "schema": json.dumps(tool_schema(Invoice)),  # a JSON *string*, not a dict
                    }
                },
            }
        },
    )
    return self._validated(Invoice, json.loads(self._text(resp)))
```

- Limit: only some models.
- Limit: schema features (recursion, some keywords) may be unsupported.
  - Unsupported keywords ⇒ `ValidationException`.

## 3. Forced Tool Use

A tool whose input schema is your schema, forced with `toolChoice`.

- `inputSchema` = your schema
- `toolChoice = {tool: {name}}`
- `toolUse.input` arrives as parsed JSON
- `strict: true` on the tool spec adds schema enforcement where supported
- Default path on Bedrock when native schema is unavailable

```python
# app/infra/_01bedrock_05prompt_engineering.py
EXTRACT_TOOL = "record_invoice"

def extract_with_tool(self, document_text: str) -> Invoice:
    # fall back to auto + instruction where forced toolChoice is rejected
    tool_choice = {"tool": {"name": EXTRACT_TOOL}} if self.settings.supports_forced_tool else {"auto": {}}
    resp = self._converse(
        [{"role": "user", "content": [{"text": f"<document>\n{document_text}\n</document>\n\nCall {EXTRACT_TOOL} with the invoice fields."}]}],
        "You extract invoice data. Use null for fields that are not present. Never guess.",
        toolConfig={
            "tools": [{"toolSpec": {
                "name": EXTRACT_TOOL,
                "description": "Record the fields of one invoice.",
                "inputSchema": {"json": tool_schema(Invoice)},
                # "strict": True,  # schema-enforced tool input where the model supports it
            }}],
            "toolChoice": tool_choice,
        },
    )
    uses = [b["toolUse"] for b in resp["output"]["message"]["content"] if "toolUse" in b]
    if not uses:
        raise StructuredOutputError(f"model answered without calling the tool (stopReason={resp['stopReason']})")
    return self._validated(Invoice, uses[0]["input"])
```

- Limit: some newer Claude models reject forced `toolChoice`

  ⇒ use `auto` + instruction, or native schema

- Catch: `toolUse.input` is schema-shaped, not guaranteed valid.
  - Pydantic + business checks still run.

## 4. JSON In Prompt + Validate + Repair

Works on any model, at the price of extra calls on failure.

→ ask for JSON only  
→ parse  
→ validate with Pydantic  
→ on failure: send the validation error back, ask for a corrected object (1–2 retries)

```python
# app/infra/_01bedrock_05prompt_engineering.py
def extract_with_repair(self, document_text: str) -> Invoice:
    schema = json.dumps(tool_schema(Invoice))
    messages = [{"role": "user", "content": [{"text":
        f"<document>\n{document_text}\n</document>\n\n"
        f"Return only a JSON object matching this JSON Schema, no prose, no code fences:\n<schema>{schema}</schema>"}]}]
    last_error = ""
    for _ in range(self.settings.max_repairs + 1):
        resp = self._converse(messages, "You output strict JSON only.")
        raw = self._text(resp).strip().removeprefix("```json").removesuffix("```").strip()
        try:
            return self._validated(Invoice, json.loads(raw))
        except (json.JSONDecodeError, StructuredOutputError) as e:
            last_error = str(e)[:1000]
            messages.append(resp["output"]["message"])  # keep the bad answer so the model sees what it wrote
            messages.append({"role": "user", "content": [{"text": f"That was invalid: {last_error}\nReturn the corrected JSON object only."}]})
    raise StructuredOutputError(f"no valid JSON after {self.settings.max_repairs} repairs: {last_error}")
```

- Catch: each repair is a full extra call (latency + cost).
- Catch: log failures to fix the prompt; don't loop forever.

## 5. Prefill

Start the assistant turn with `{` so the model continues JSON.

- Cheap on older models
- Rejected by newer Claude models (Anthropic docs 2026-11)
  - A final assistant turn ⇒ `ValidationException`

```python
# app/infra/_01bedrock_05prompt_engineering.py
def extract_with_prefill(self, document_text: str) -> Invoice:
    resp = self._converse(
        [
            {"role": "user", "content": [{"text": f"<document>\n{document_text}\n</document>\n\nExtract the invoice as JSON with keys vendor, invoice_number, invoice_date, currency, total, line_items."}]},
            {"role": "assistant", "content": [{"text": "{"}]},  # prefill
        ],
        "You output strict JSON only.",
    )
    return self._validated(Invoice, json.loads("{" + self._text(resp)))  # re-add the prefilled brace
```

- Catch: no schema guarantee; stop at the closing brace yourself.

## 6. Always Validate

Validate even with constrained decoding.

- Schema-valid ≠ correct
  - Totals can be wrong
  - Dates invented
- Add business checks (line items sum to total)

```python
# app/infra/_01bedrock_05prompt_engineering.py
@staticmethod
def _validated(model: type[Invoice], data: Any) -> Invoice:
    try:
        obj = model.model_validate(data)  # 1. schema / types
    except ValidationError as e:
        raise StructuredOutputError(e.json(include_url=False)) from e
    problems = obj.check_totals()         # 2. business rules
    if problems:
        raise StructuredOutputError("; ".join(problems))
    return obj
```

```python
# app/domain/_01bedrock_05prompt_engineering.py
def check_totals(self, tolerance: Decimal = Decimal("0.01")) -> list[str]:
    if not self.line_items:
        return []
    items = sum((li.quantity * li.unit_price for li in self.line_items), Decimal(0))
    return [] if abs(items - self.total) <= tolerance else [f"line items sum to {items}, total is {self.total}"]
```

- Catch: tax/discount lines make `sum(items) != total` legitimately.
  - Tune per document type.

## 7. Design The Schema For The Model

- Descriptions on fields
- Enums for closed sets
- `null` allowed for unknowns

⇒ fewer invented values

```python
# app/domain/_01bedrock_05prompt_engineering.py
# Decimal in code (exact money math), plain "number" in the schema the model sees
# (Pydantic's default Decimal schema is number-or-string, which invites quoted numbers).
NonNegative = Annotated[Decimal, Field(ge=0), WithJsonSchema({"type": "number", "minimum": 0})]

class Invoice(BaseModel):
    """Nullable fields let the model say "unknown" instead of inventing a value."""
    vendor: str = Field(description="Seller name as printed on the invoice")
    invoice_number: str | None = Field(default=None, description="Invoice id; null if absent")
    invoice_date: date | None = Field(default=None, description="ISO date YYYY-MM-DD; null if absent")
    currency: Currency = Field(description="ISO 4217 code")  # StrEnum: USD, EUR, GBP, JPY
    total: NonNegative = Field(description="Grand total including tax")
    line_items: list[LineItem] = Field(default_factory=list)

def tool_schema(model: type[BaseModel]) -> dict[str, Any]:
    """Pydantic JSON Schema for toolSpec.inputSchema.json / outputConfig."""
    return model.model_json_schema()
```

- Catch: `$defs` refs are valid JSON Schema.
  - Some providers handle inlined schemas better (check per model).
- The Representational State Transfer (REST) adapter exposes `/schema` to inspect what the model must fill.
