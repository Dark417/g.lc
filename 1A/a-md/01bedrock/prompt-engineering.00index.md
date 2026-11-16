# prompt-engineering Prompt Engineering And Structured Output

> Shape the input so the model does the task reliably, and make the answer schema-valid JavaScript Object Notation (JSON) code can trust.

## Index

- [1. Source And Scope](#1-source-and-scope)
- [2. One-Minute Version](#2-one-minute-version)
- [3. File Index](#3-file-index)
- [4. Code Map](#4-code-map)
- [5. Gaps](#5-gaps)
- [References](#references)

---

## 1. Source And Scope

This component covers prompt techniques and structured output over Converse.

- Lectures: AIP-C01 #29–#34 (slides p.62–70)
- Scope: Python only
  - No Terraform: uses the [converse](converse.00index.md) Converse permissions on the app role
- Code: Python `app/{config,api,domain,infra}/_01bedrock_05prompt_engineering.py`
- Related
  - [converse](converse.00index.md)
  - [prompt-management](prompt-management.00index.md)
  - [guardrails](../04safety/guardrails.00index.md)
- Numbers: Amazon Bedrock User Guide, Anthropic prompt-engineering docs, read 2026-11
  - Unless marked "order of magnitude"

## 2. One-Minute Version

Prompting is the cheapest lever; structured output makes it machine-usable.

- What
  - **Prompt engineering**: shaping the input so the model does the task reliably
  - **Structured output**: making the answer machine-parseable and schema-valid
- Why
  - Cheapest lever: no training, no infra, minutes to iterate
  - Downstream code needs JSON it can trust, not prose
- How
  - Anatomy: role → task → context → examples → output format
    - Each in its own Extensible Markup Language (XML)-tagged section
  - Few-shot examples teach format and edge cases better than adjectives
  - Structured output, most to least reliable

→ native JSON-schema output (`outputConfig`) or a forced tool with a JSON schema  
→ validate with Pydantic anyway  
→ fallback: JSON in prompt + validate + repair retry

- Catch
  - A prompt is not a security boundary
    - Retrieved text and user input can carry instructions (prompt injection)
    - Defense = fencing + instruction hierarchy + guardrails + least-privilege tools
  - Prompts are model-specific
    - Re-test after every model change
- 🗣 "Show, don't tell: two good examples beat a paragraph of adjectives."
- 🗣 "For JSON, constrain the decoder (schema or tool), then validate anyway."
- 🗣 "Never trust a prompt to protect a tool; trust Identity and Access Management (IAM)."

## 3. File Index

Read top to bottom: shaping the prompt, then the output, then the risks.

- Shaping the prompt
  - [01 Why it matters, anatomy of a prompt](prompt-engineering.01anatomy.md)
  - [02 Zero-, one-, few-shot](prompt-engineering.02few-shot.md)
  - [03 Chain-of-thought](prompt-engineering.03chain-of-thought.md)
  - [04 Templates](prompt-engineering.04templates.md)
  - [05 Temperature and top-p](prompt-engineering.05sampling.md)
- Getting usable output
  - [06 Structured output](prompt-engineering.06structured-output.md)
- Risks
  - [07 Prompt misuse: injection, jailbreak, leakage](prompt-engineering.07prompt-misuse.md)
  - [08 Bias](prompt-engineering.08bias.md)
- Decide and defend
  - [98 Trade-offs: when to use, knobs, comparison, failure modes](prompt-engineering.98tradeoffs.md)
  - [99 Interview questions](prompt-engineering.99interview.md)

## 4. Code Map

All paths are under `app/`; `…` = the same component module, e.g. `infra/_01bedrock_05prompt_engineering.py`.

| Concept file | Python (`app/`) |
|---|---|
| 01 anatomy + tag rendering | `domain/_01bedrock_05prompt_engineering.py` `PromptSections.render` |
| 02 few-shot builders | `domain/…` `build_few_shot_block`, `few_shot_messages` |
| 02 zero- vs few-shot | `infra/…` `PromptingShowcase.classify_zero_shot`, `.classify_few_shot` |
| 03 Chain-of-Thought (CoT) + `<answer>` | `infra/…` `PromptingShowcase.chain_of_thought`, `domain/…` `extract_tag` |
| 04 templates | `domain/…` `render_template` |
| 05 temperature / top-p | `infra/…` `PromptingShowcase.sample_at_temperatures` |

| Concept file | Python (`app/`) |
|---|---|
| 06 forced tool + Pydantic | `infra/…` `PromptingShowcase.extract_with_tool`, `domain/…` `Invoice` |
| 06 native JSON schema | `infra/…` `PromptingShowcase.extract_with_native_schema` |
| 06 JSON + repair loop | `infra/…` `PromptingShowcase.extract_with_repair` |
| 06 prefill | `infra/…` `PromptingShowcase.extract_with_prefill` |
| 06 business validation | `domain/…` `Invoice.check_totals` |

| Concept file | Python (`app/`) |
|---|---|
| 07 fencing | `domain/…` `fence_untrusted`, `infra/…` `PromptingShowcase.answer_from_documents` |
| 07 heuristic detector | `domain/…` `InjectionDetector.scan` |
| Representational State Transfer (REST) Application Programming Interface (API) | `api/_01bedrock_05prompt_engineering.py` `router` (`/prompting`) |

## 5. Gaps

These topics are documented but not coded.

- Dynamic few-shot selection by embedding similarity
  - Needs [embeddings](../02rag/embeddings.00index.md)
- Guardrails `PROMPT_ATTACK` filter → [guardrails](../04safety/guardrails.00index.md) code
- Bias evaluation on sliced datasets → [evaluations](../04safety/evaluations.00index.md)
- Reasoning-model effort settings via `additionalModelRequestFields`

## References

- [aws-samples/prompt-engineering-with-anthropic-claude-v-3](https://github.com/aws-samples/prompt-engineering-with-anthropic-claude-v-3) — interactive prompt-engineering tutorial on Bedrock
- [Amazon Bedrock User Guide: Prompt engineering concepts](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-engineering-guidelines.html)
- [Amazon Bedrock User Guide: Use a tool to complete a model response](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html)
- [Anthropic docs: Prompt engineering overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
- [OWASP Top 10 for LLM Applications: LLM01 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
