# 2prompt — Prompting And Structured Output

> One good model call: how to write the prompt, and how to get output your code can trust.
> Layer L3 in [1a-bp.md](../1a-bp.md). Context management is in [2context-engineering-handbook.md](2context-engineering-handbook.md).
> Last updated: 2026-11-16.

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Concept](#1-concept)
- [2. Architecture of one call](#2-architecture-of-one-call)
- [3. Key components](#3-key-components)
  - [3.1 Prompt structure](#31-prompt-structure)
  - [3.2 Techniques that still matter](#32-techniques-that-still-matter)
  - [3.3 Structured output: four levels](#33-structured-output-four-levels)
  - [3.4 Constrained decoding](#34-constrained-decoding)
  - [3.5 Prompts as code](#35-prompts-as-code)
- [4. Using it well](#4-using-it-well)
- [5. Comparison](#5-comparison)
- [6. Failure modes](#6-failure-modes)
- [7. Interview questions](#7-interview-questions)
- [8. Deeper](#8-deeper)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** a prompt is the full input to one model call: instructions, examples, data and the output format.
- **Why:** the model is fixed; the prompt and the output contract are the parts you control.
- **How:** clear instructions, a few examples, data marked off from instructions, and a schema for the output.
- **Catch:** free-text output breaks parsers. Use schema-enforced output, and still validate the meaning.
- 🗣 "I treat a prompt like an API: versioned instructions in, a schema-enforced object out, and an eval on every change."

---

## 1. Concept
`AI`

- **Plain idea:** you are writing a precise work order for a very capable new hire who knows nothing about your company.
- **Picture it:** "Summarize this ticket" gives you a paragraph. "Return `{severity, component, summary}` where severity is one of low / med / high" gives you a record you can store.
- **How it works**
  1. You assemble a request: system instructions, examples, tool definitions, the user's input.
  2. The model predicts tokens one by one, conditioned on all of it.
  3. Without constraints, any token can come next, so the output may drift from the format.
  4. With structured output, the provider restricts which tokens are allowed, so the result matches your schema.
  5. Your code validates the object, then acts on it.
- **The catch**
  - Valid JSON is not correct JSON. A schema guarantees shape, not truth.
  - Long prompts cost tokens and latency on every call.
  - A prompt that works on one model may regress on the next version.
- 🗣 "Structured output fixes the shape. Evals and validation check the content."

---

## 2. Architecture of one call
`boundary`

```
  system prompt (role, rules, format)   ─┐
  examples (few-shot)                     ├──> model ──> constrained decoder ──> JSON
  tools + schemas                         │                                       |
  context (retrieved docs, state)         │                           Pydantic validate
  user input (marked as data)           ─┘                                       |
                                                              business checks ──> act / retry / escalate
```

- **System prompt:** stable rules and role. Put it first so it can be cached.
- **Examples:** show the format and edge cases; the model copies patterns.
- **Tools + schemas:** what the model may call, and the argument shapes.
- **Context:** retrieved facts and state for this call (see the context doc).
- **User input:** marked off as data, so it isn't taken as instructions.
- **Constrained decoder:** provider feature that forces output to match the schema.
- **Validator:** your Pydantic model, plus business rules the schema can't express.

---

## 3. Key components

### 3.1 Prompt structure
`AI` ★★★

- **Plain idea:** order and labels matter. Put stable content first and mark every part.
- **The order that works**
  1. Role and goal: who the model is and what "done" means.
  2. Rules: must and must-not, with the reason for each.
  3. Output format: the schema, or a short description of it.
  4. Examples: 2 to 5, covering the edge cases.
  5. Context: documents, state, prior results.
  6. The task input, last.
- **Mark sections**
  - Use XML-style tags or clear headers: `<rules>`, `<document id="3">`, `<user_input>`.
  - Tags let you say "answer only from `<documents>`" and let code find parts later.
- **Say why, not only what**
  - "Never mention prices, because they change daily and we can't guarantee them" generalizes better than "Never mention prices".
- **Stable first, volatile last**
  - Providers cache the longest matching prefix, so the same opening is cheaper on every call.
- 🗣 "Role, rules, format, examples, context, input. Stable parts first, so they cache."

### 3.2 Techniques that still matter
`AI` ★★

- **Few-shot examples** ★★★
  - Best tool for format and tone.
  - Include one hard or negative case, or the model learns only the easy path.
  - Catch: the model copies quirks of the examples, like length or wording.
- **Step-by-step reasoning** ★★
  - Ask the model to think before answering, or turn on the model's built-in reasoning mode.
  - Helps multi-step logic and math; costs tokens and latency.
  - With structured output, put a `reasoning` field before the answer fields, or use the provider's separate reasoning output.
- **Decomposition (prompt chaining)** ★★★
  - Split one big prompt into steps: extract, then classify, then write.
  - Each step is easier to test and can use a smaller model.
- **Grounding instructions** ★★★
  - "Answer only from the documents. If the answer isn't there, say so."
  - Ask for citations by document ID, so code can check them.
- **Role prompting** ★
  - "You are a senior support agent" sets tone. It doesn't add knowledge.
- **Self-check** ★
  - A second call grades or fixes the first output. That is the verifier loop at small scale.

### 3.3 Structured output: four levels
`boundary` ★★★

- **Plain idea:** the stronger the enforcement, the fewer bad outputs reach your code.

| Level | How | Guarantee | Use when |
|---|---|---|---|
| 1. Ask nicely | "Return JSON like this…" in the prompt | none | prototypes only |
| 2. JSON mode | provider flag: output is valid JSON | syntax only, not your fields | old models, loose shapes |
| 3. Schema-enforced | provider gets your JSON Schema; decoding is constrained | matches the schema | default for production |
| 4. Schema + validate + retry | level 3, then Pydantic and business rules; re-ask with the error | shape and rules you can code | anything that acts or writes |

- **Two ways to send a schema**
  - **Response format:** the whole answer is one JSON object.
    - Anthropic: `output_config.format` with `type: "json_schema"`.
    - OpenAI: `json_schema` response format with `strict: true`.
    - Gemini: a response schema with JSON MIME type.
  - **Strict tool use:** the model "calls a tool" whose arguments are your schema.
    - Anthropic and OpenAI both offer `strict: true` on tools.
    - Good when the model must choose between several output shapes.
- **SDK helpers**
  - Pass a Pydantic class; get a parsed object back (e.g. Anthropic `client.messages.parse`).
  - Instructor wraps many providers with the same validate-and-retry loop.
- **ADK**
  - `LlmAgent(output_schema=MyModel)` enforces the shape.
  - `output_key` stores the result in session state for the next agent.
  - Catch: older ADK versions didn't allow tools on an agent with `output_schema`. Check your version, or split into two agents.
- 🗣 "Prompting for JSON is a hope. A schema-enforced response is a contract. Validation checks the business rules the schema can't."

### 3.4 Constrained decoding
`AI` ★★

- **Plain idea:** at each step, the decoder blocks every token that would break the schema.
- **Picture it:** after `{"severity": "`, only tokens that can start `low`, `med` or `high` are allowed.
- **How it works**
  1. The schema is compiled into a grammar (a state machine).
  2. At each step, the grammar gives the set of allowed next tokens.
  3. Disallowed tokens get zero probability; the model picks among the rest.
  4. Output is valid by construction, so no parse retries are needed.
- **The catch**
  - **First-call latency:** compiling the grammar takes time.
    - Anthropic caches compiled grammars for 24 hours from last use (docs, Nov 2026).
  - **Partial JSON Schema support.** Anthropic doesn't support:
    - numeric limits (`minimum`, `maximum`), string length, recursive schemas.
    - Unsupported features return a 400. SDK helpers move those constraints into descriptions and check them after parsing.
  - **Quality can dip** if the schema fights the model, e.g. forcing the answer before any reasoning.
  - **Truncation:** hitting `max_tokens` mid-object still gives broken output. Check the stop reason.
- **Self-hosted:** vLLM supports guided decoding with grammar backends such as XGrammar and Outlines.
- 🗣 "Constrained decoding masks invalid tokens, so the output is valid by construction. It still can't make it true."

### 3.5 Prompts as code
`software` ★★★

- **Plain idea:** a prompt change is a code change. Version it, review it and test it.
- **How**
  1. Keep prompts in files or a registry, not inline strings.
  2. Version each prompt; log the version on every trace.
  3. Run the golden set on every change; block the merge on regression.
  4. Roll out with a flag or canary; keep instant rollback.
- **Catch:** model upgrades are prompt changes too. Re-run evals before switching models.

---

## 4. Using it well
`boundary`

- **Knobs**
  - **Temperature:** 0 to 0.3 for extraction and classification; higher for creative writing.
    - Lower temperature reduces variety, not hallucination.
  - **`max_tokens`:** cap cost; set high enough that objects don't get cut off.
  - **Model size:** small model for extraction, larger for reasoning. Route per step.
- **Tricks**
  - Enums over free strings: `Literal["refund", "replace", "escalate"]` makes routing code trivial.
  - Add an escape value like `"unknown"` or `"needs_human"`, so the model isn't forced to guess.
  - Field descriptions in the schema act as instructions. Write them carefully.
  - Put `reasoning` first and `answer` last, so the model thinks before it commits.
  - Keep schemas flat and small; deep nesting raises error rates.
- **Best practices** (rule, and the failure it prevents)
  - Separate instructions from user data with tags. Prevents prompt injection through input text.
  - Always validate after parsing. Prevents valid-but-wrong values reaching the database.
  - Check the stop reason. Prevents silent truncation.
  - Include a "can't answer" path. Prevents confident made-up answers.
  - Version prompts and schemas together. Prevents a schema change breaking old consumers.
  - Pin model versions in production. Prevents silent behavior change on provider updates.

---

## 5. Comparison
`boundary`

| Option | What it is | Good at | Bad at | Choose when |
|---|---|---|---|---|
| Provider structured output | schema sent to the API; constrained decoding | guaranteed shape, no retries for syntax | partial JSON Schema; first-call compile | default on hosted models |
| Strict tool use | schema as tool arguments | choosing among several shapes; agents | one more layer of indirection | output is an action or a choice |
| Instructor / SDK parse | Pydantic + validate + retry loop | one API over many providers; business rules | retries cost tokens | multi-provider, rich validation |
| Self-hosted guided decoding | vLLM with XGrammar / Outlines | full control, regex and grammars | you run the GPUs | self-hosted models |
| Prompt-only JSON | instructions + parsing | anything, any model | breaks under load | prototypes only |

- Default: provider structured output plus Pydantic validation, unless the output is a choice of action, then strict tool use.

---

## 6. Failure modes
`boundary`

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Invalid JSON | prompt-only format, or truncation | parse errors; stop reason = max tokens | schema-enforced output; raise `max_tokens` |
| Valid but wrong value | schema can't express the rule | business validation fails; eval drop | validate + re-ask with the error; tighter enums |
| Forced guess | no "unknown" option | high confidence on bad inputs | add an escape value and route to a human |
| Prompt injection | user or document text read as instructions | odd tool calls; policy hits | tag data; limit tools; check actions outside the model |
| Silent regression | prompt or model change | golden-set score drops | eval gate in CI; pinned models |
| Cost blowup | long prompts, many retries | tokens per task rising | cache stable prefix; cap retries; smaller model per step |

---

## 7. Interview questions

**Q1. How do you get reliable JSON from an LLM?**
- Intuitive: don't ask for JSON, enforce it.
- L4: use the provider's structured-output mode with a JSON Schema, generated from a Pydantic model. The decoder is constrained, so the output always parses. Then validate with Pydantic before using it.
- L5: also check the stop reason, because truncation still breaks objects. Keep schemas flat, add an escape value, and put reasoning fields first. Schema features the provider doesn't support move into validation after parsing. Track the validation failure rate as a metric.

**Q2. What's the difference between JSON mode and structured outputs?**
- Intuitive: JSON mode promises syntax; structured output promises your shape.
- L4: JSON mode guarantees valid JSON but not your fields. Structured output takes your schema and constrains decoding to match it.
- L5: the mechanism is a grammar compiled from the schema that masks invalid tokens. Costs: compile latency on first use, partial JSON Schema support, and possible quality loss if the schema fights how the model wants to reason.

**Q3. The JSON is valid but the values are wrong. What now?**
- Intuitive: shape is solved; meaning isn't.
- L4: add business validation after parsing, and re-ask with the specific error. Tighten enums and field descriptions.
- L5: first find which fields fail with evals. Then fix by cause: missing context (retrieval), an ambiguous instruction (prompt), or a hard task (split the step or use a bigger model). Retries cost tokens, so cap them and route to a human after the cap.

**Q4. Structured output vs tool calling: when to use which?**
- Intuitive: one is "fill this form", the other is "pick an action and fill its form".
- L4: use response format when the answer is always one shape. Use tools when the model chooses between actions or shapes.
- L5: inside an agent loop, everything is a tool call, including a final `submit_answer` tool with the result schema. That gives one parsing path and a clear stop signal.

**Q5. How do you defend a prompt against injection?**
- Intuitive: treat all input as data, never as orders.
- L4: put user and document text inside tags, and tell the model it is data. Limit the tools the model can use.
- L5: prompts alone can't stop injection. The real controls sit outside the model: tool permissions follow the user, writes need approval, and outputs are checked before acting. Test with an injection set in the evals.

**Q6. How do you manage prompts in production?**
- Intuitive: like code.
- L4: version prompts in the repo, review changes, and run the golden set in CI.
- L5: log the prompt and model version on every trace, so a regression maps to a change. Roll out with flags or canaries. Treat a model upgrade as a prompt change and re-run the evals.

**Q7. Few-shot or fine-tuning for a strict format?**
- Intuitive: try the cheap thing first.
- L4: start with structured output and a few examples. That usually fixes format with no training.
- L5: fine-tune when the prompt gets too long to pay for on every call, or when style must be very consistent at high volume. Even then, keep schema enforcement and validation.

**Q8. Does temperature 0 stop hallucination?**
- Intuitive: no; it makes the same answer more likely, not a true one.
- L4: low temperature reduces variety. It doesn't add knowledge.
- L5: hallucination falls with grounding (retrieval plus "answer only from sources"), citations you can check, and an "I don't know" path. Even at temperature 0, outputs aren't fully deterministic on many providers.

---

## 8. Deeper
- **Why reasoning-first ordering helps:** the model generates left to right. If the answer field comes first, it commits before "thinking".
- **Grammar compilation cost:** large enums and deep nesting make bigger state machines. Keep schemas small on hot paths.
- **Provider differences:** each supports a different subset of JSON Schema. Generate schemas from Pydantic and test them against each provider you use.
- **L5 adds:** a validation-failure metric per field, a retry budget per task, and schema versioning tied to consumers.

---

## Where this fits
- **Place:** L3 of [1a-bp.md](../1a-bp.md). Every agent step is one of these calls.
- **Time it deserves:** 45 minutes before tomorrow; §0, §3.3 and Q1 to Q5.
- **I should be able to…**
  - Explain constrained decoding in two sentences.
  - Say why valid JSON can still be wrong, and how to catch it.
  - Show the Pydantic → schema → parse → validate path from memory.

## References
1. [Anthropic structured outputs docs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) — JSON outputs, strict tool use, schema limits, grammar caching.
2. [Anthropic prompt engineering overview](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview) — clarity, examples, XML tags.
3. [OpenAI structured outputs guide](https://platform.openai.com/docs/guides/structured-outputs) — strict JSON Schema.
4. [567-labs/instructor](https://github.com/567-labs/instructor) — Pydantic validate-and-retry loop; read `retry.py`.
5. [Google ADK LLM agents](https://google.github.io/adk-docs/agents/llm-agents/) — `output_schema`, `output_key`.
