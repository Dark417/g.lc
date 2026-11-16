# prompt-engineering Trade-Offs

> When to prompt and when to move on, the knobs that matter, the structured-output options, and how it fails.

## Index

- [1. When To Use / Not](#1-when-to-use--not)
- [2. Knobs And Best Practices](#2-knobs-and-best-practices)
- [3. Comparison](#3-comparison)
- [4. Failure Modes](#4-failure-modes)

Back to [00index](prompt-engineering.00index.md).

---

## 1. When To Use / Not

Prompt first; escalate only for what prompting cannot fix.

- Prompt engineering first when
  - The model can already do the task sometimes
  - Format or consistency is the problem
- Structured output when
  - Code consumes the answer
    - extraction, routing, classification, tool arguments
- Move beyond prompting when
  - Missing knowledge or freshness ⇒ Retrieval-Augmented Generation (RAG) ([02rag](../02rag/embeddings.00index.md))
  - Style or format still fails after good examples, at high volume ⇒ fine-tune ([customization](customization.00index.md))
  - Deterministic rules ⇒ code, not a prompt

## 2. Knobs And Best Practices

Each rule names the failure it prevents where the source does.

- Be specific and positive
  - "answer in 3 bullets" beats "don't be verbose"
- Give the reason behind a rule
  - Models follow rules better when they know why
- Separate sections with Extensible Markup Language (XML) tags
  - Documents first, question last
- Say what to do when unsure ("return null", "say you don't know")
  - Prevents: invented values
- Few-shot: 3–5 varied examples covering edge cases
  - Prevents: format drift and surface copying
- Low temperature for deterministic tasks
- Structured output
  - Native schema or forced tool first
  - Pydantic validation always
  - Cap repair retries at 1–2
  - Log failures for prompt fixes
- Security
  - Fence every untrusted input
  - Keep tools least-privilege
  - Guardrail the user input
- Process
  - Version prompts ([prompt-management](prompt-management.00index.md))
  - Keep a golden test set
  - Re-run it on every prompt or model change ([evaluations](../04safety/evaluations.00index.md))
  - Measure cost: tokens per request from `usage`

## 3. Comparison

Ranked by how much the decoder is constrained.

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| Native JavaScript Object Notation (JSON) schema (`outputConfig`) | Decoder constrained to your JSON Schema | Highest validity; no tool plumbing | Only some models; schema-feature limits | Model supports it; pure extraction |
| Forced tool use (`toolChoice: tool`) | Schema as a tool's input schema | Wide support across Bedrock models; parsed JSON | Forced choice rejected by some newer models; tool loop semantics | Default on Bedrock when native schema is unavailable |
| JSON in prompt + validate + repair | Instructions + Pydantic + retry with the error | Works on any model | Extra calls on failure; still can fail | Model lacks tools/schema; quick prototypes |
| Prefill `{` | Start the assistant turn with JSON | Zero cost, simple | Rejected by newer Claude models; no schema guarantee | Older models only |
| Regex / parser on free text | Parse prose after the fact | No model constraints | Brittle | Legacy outputs; last resort |

- Deciding variable: does the model support constrained decoding (native schema or forced tools)?
- Pick: native JSON schema where supported, else forced tool use, always with Pydantic validation.
  - JSON-in-prompt + repair only as fallback.

## 4. Failure Modes

Split into output failures and security/operations failures.

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Invalid JSON | Free-text prompting, truncation | `json.loads` / Pydantic error; `stopReason = max_tokens` | Native schema or forced tool; raise `maxTokens`; repair retry |
| Schema-valid but wrong | Model guesses missing fields | Business-rule checks fail | Allow `null`; add field descriptions; examples with unknowns |
| Format drift | Zero-shot on varied inputs | Golden-set regression | Few-shot examples; explicit format section |
| Example copying | Few-shot examples too similar | Outputs mirror examples | Vary examples; dynamic selection |
| Chain-of-Thought (CoT) cost blow-up | Step-by-step on every request | Output tokens per request | CoT only where accuracy needs it; reasoning-model effort setting |

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Indirect injection | Instructions in retrieved docs or tool output | Unexpected tool calls; policy violations | Fence content; instruction hierarchy; guardrail; least-privilege tools |
| Prompt leakage | User asks for the system prompt | System text in output | No secrets in prompts; output filter |
| Jailbreak | Role-play / encoding attacks | Guardrail `PROMPT_ATTACK` hits | Guardrails; refuse patterns; monitoring |
| Prompt breaks on model change | Prompt tuned to one model | Eval score drop | Version prompts; re-run evals before switching |
| Rejected parameter | Prefill, forced tool, or temperature on a model that rejects it | `ValidationException` | Per-model config flags; native schema |
