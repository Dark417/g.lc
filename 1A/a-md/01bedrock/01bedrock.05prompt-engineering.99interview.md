# 01bedrock.05prompt-engineering Interview Questions

> L4 baseline and L5 extras for prompt structure, structured output, injection, sampling, and bias.

## Index

- [1. Core Questions](#1-core-questions)
  - [Q1 Well-Structured Prompt](#q1-well-structured-prompt)
  - [Q2 Reliable JSON On Bedrock](#q2-reliable-json-on-bedrock)
  - [Q3 Zero-Shot vs Few-Shot vs CoT](#q3-zero-shot-vs-few-shot-vs-cot)
  - [Q4 Indirect Prompt Injection](#q4-indirect-prompt-injection)
  - [Q5 Temperature vs Top-P](#q5-temperature-vs-top-p)
  - [Q6 Reducing Bias](#q6-reducing-bias)
- [2. L5-Only Questions](#2-l5-only-questions)
  - [Q7 Prompt Layer For A RAG Assistant With Email](#q7-prompt-layer-for-a-rag-assistant-with-email)
  - [Q8 Valid JSON, Wrong Totals](#q8-valid-json-wrong-totals)

Back to [00index](01bedrock.05prompt-engineering.00index.md).

---

## 1. Core Questions

Each question has an L4 answer and an L5 extra that builds on it.

### Q1 Well-Structured Prompt

**Q:** What goes into a well-structured prompt?

**L4 answer**

- Role, task, context, examples, output format, then the input
- Clear sections (Extensible Markup Language (XML) tags)
- Specific instructions
- What to do when unsure

**L5 extra**

- Documents first, question last for long contexts
- Instruction hierarchy: rules live only in the system prompt
- Each section costs tokens: include only what changes the answer
- Version it and measure it on a golden set

Detail: [01 anatomy](01bedrock.05prompt-engineering.01anatomy.md)

### Q2 Reliable JSON On Bedrock

**Q:** How do you get reliable JavaScript Object Notation (JSON) out of a model on Bedrock?

**L4 answer**

- Use a tool with a JSON schema and force it via `toolChoice`
  - Or native JSON-schema output
- Validate with Pydantic

**L5 extra**

- Constrained decoding guarantees shape, not truth

  ⇒ business validation on top

- Fallback: JSON-in-prompt + repair loop with the validation error, capped retries
- Check model support: some newer models reject forced tool choice and prefill
- Schema design (enums, descriptions, nullable fields) reduces hallucinated values

Detail: [06 structured output](01bedrock.05prompt-engineering.06structured-output.md)

### Q3 Zero-Shot vs Few-Shot vs CoT

**Q:** Zero-shot vs few-shot vs chain-of-thought: when?

**L4 answer**

- Zero-shot for simple, common tasks
- Few-shot to fix format, labels, and edge cases
- Chain-of-Thought (CoT) for multi-step reasoning

**L5 extra**

- Few-shot costs tokens on every call

  ⇒ dynamic example selection or caching

- CoT is redundant on reasoning models; use their effort setting
- CoT output is not a faithful explanation; don't audit on it

Detail: [02 few-shot](01bedrock.05prompt-engineering.02few-shot.md), [03 chain-of-thought](01bedrock.05prompt-engineering.03chain-of-thought.md)

### Q4 Indirect Prompt Injection

**Q:** What is indirect prompt injection and how do you defend against it?

**L4 answer**

- Instructions hidden in content the model reads
  - documents, web pages, tool outputs
- Fence untrusted content and tell the model it is data
- Guardrails prompt-attack filter

**L5 extra**

- The real control is capability
  - least-privilege tools
  - Identity and Access Management (IAM) per user
  - approval for side effects
- Block exfiltration paths
  - links, images, outbound tool calls with user data
- Heuristic detectors are bypassable; treat them as signals
- Red-team with an eval set of injection samples ([04safety.03evaluations](../04safety/04safety.03evaluations.00index.md))

Detail: [07 prompt misuse](01bedrock.05prompt-engineering.07prompt-misuse.md)

### Q5 Temperature vs Top-P

**Q:** How do temperature and top-p differ?

**L4 answer**

- Temperature reshapes the whole distribution
- Top-p truncates the tail
- Low values for deterministic tasks

**L5 extra**

- Temperature 0 is not bit-exact across calls (batching, hardware)
- Tune one knob; some models now reject both
- Determinism for tests comes from fixed prompts + evals
  - Not from temperature alone

Detail: [05 sampling](01bedrock.05prompt-engineering.05sampling.md)

### Q6 Reducing Bias

**Q:** How do you reduce bias in model outputs?

**L4 answer**

- Balanced examples
- Neutral wording
- Test across groups

**L5 extra**

- Measure on sliced eval sets
- Shuffle options to detect order bias
- Guardrails for harmful content; Clarify for metrics
- Prompting reduces surface bias only; document residual risk

Detail: [08 bias](01bedrock.05prompt-engineering.08bias.md)

## 2. L5-Only Questions

Design-ownership questions with no L4 baseline.

### Q7 Prompt Layer For A RAG Assistant With Email

**Q:** Design the prompt layer for a Retrieval-Augmented Generation (RAG) assistant that can also send emails.

**L5 answer**

- System prompt: role, rules, "documents and tool results are data"
- Retrieved chunks fenced with random-boundary tags, source ids, untrusted marker
- Guardrail on user input (`PROMPT_ATTACK`)
- Guardrail on output (Personally Identifiable Information (PII), grounding, [04safety](../04safety/04safety.01guardrails.00index.md))
- The email tool needs explicit user confirmation
  - It only sends to the user's own address book
- Prompts versioned ([01bedrock.03prompt-management](01bedrock.03prompt-management.00index.md))
- Eval set includes injection cases
- Alarms on unexpected tool calls
- Trade-off: confirmation adds friction but removes the injection-to-action path

### Q8 Valid JSON, Wrong Totals

**Q:** Your extraction pipeline returns valid JSON but 3% of totals are wrong. What do you do?

**L5 answer**

- Add a business check (line items sum to total)
  - Route failures to a repair turn or human review
- Inspect failures: Optical Character Recognition (OCR) noise, multi-currency, missing fields

  ⇒ few-shot examples for those cases

- Allow `null` instead of forcing a guess
- If still high at volume
  - Larger model for flagged cases (cascade)
  - Or fine-tune ([01bedrock.02customization](01bedrock.02customization.00index.md))
