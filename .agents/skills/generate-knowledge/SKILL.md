---
name: generate-knowledge
description: Generate rigorous, principal-engineer-reviewable technical knowledge documents from a topic manifest, with mechanism-level explanations, architecture, tradeoffs, failures, production evidence, and distinct L4/L5 interview questions. Use when the user asks to create or refresh system-design knowledge, topic references, technology deep dives, interview review notes, or knowledge files from topics.yaml.
---

# Generate Knowledge

Produce interview-review reference documents for a backend engineer preparing for Amazon SDE II and Google L4 loops. Write Markdown files in this repository.

## Rules file

Always read `.agents/rules.md` first and follow it: bullets-only formatting, hyperlinked index, mechanism-first §4 order per component, comparison tables (§5), doc structure (§6), L4/L5 question format (§7), quality bar (§8), and the topic pair rule (§10: `{topic}.md` + `{topic}1.md` when the user says `in xx/{topic}/ explain {topic}`). Where this skill and `.agents/rules.md` differ, `.agents/rules.md` wins.

## Quality bar

Make every document survive a principal engineer attacking it line by line.

1. Prefer mechanism over label. Explain what creates a property and what it costs.
2. Give every property claim its defeater: state when the property does not hold.
3. Source every precise number with an official document, paper, public postmortem, version, or date. Otherwise label it as an order of magnitude.
4. Cite public production incidents or label them `Canonical failure pattern (not a specific incident)`.
5. Name the tradeoff, identify the deciding variable, and choose a default.
6. Use terms precisely: quorum versus consensus, isolation versus consistency, idempotent versus exactly-once.

## Input

Read a topic manifest at `1sd/topics.yaml` unless the user supplies another path:

```yaml
- id: kafka
  title: Apache Kafka
  sections:
    - "Log & Storage Model"
    - "Producer Path"
    - "Consumer Groups & Rebalancing"
    - "Delivery Semantics"
    - "Replication & ISR"
```

## Output

- Write one file per topic to `1sd/00.base/<id>.md`.
- Overwrite deterministically: the same input produces the same structure.
- Use pure Markdown with language-tagged fenced code blocks.

## Required file structure

For each topic, number sections `1, 2, 3...` and subsections `1.1, 1.2...`. Every subsection must contain all seven parts. If one does not apply, retain its heading and explain why in one line.

```markdown
# <Topic Title>

## 1. <Section Name>

### 1.1 <Subsection Name>

#### Concept
- **What it is** — one precise sentence, then the expansion.
- **What problem it solves** — the concrete pain that existed without it.
- **What it replaced** — the prior art and why it was insufficient.
- **What it works with / ecosystem** — what sits above, below, and beside it; what composes or conflicts.
- **Place in the world** — where it appears in real systems and where it is the wrong answer.

#### Architecture & Core Components
- Give the high-level picture and component inventory.
- Include one ASCII or Mermaid diagram showing data flow and control flow.
- State each component's single responsibility.

#### How Each Component Works
For every component, cover:
- Algorithm or data structure.
- Inputs, outputs, and owned state.
- Lifecycle: start, steady state, shutdown.
- Interaction protocol with adjacent components.

#### Design Decisions, Tradeoffs & Best Practices
- Explain design decisions and rejected alternatives.
- Explain adoption decisions: configuration, topology, sizing, and deciding variable.
- Include `Option | Buys you | Costs you | Choose when`.
- State every best practice as a rule plus the failure it prevents.

#### Failure Modes, Exception Handling & Production Issues
- Include `Failure | Trigger | Blast radius | Detection signal | Mitigation`.
- Explain surfaced versus swallowed errors, retryable versus terminal errors, and poison-pill risk.
- For production issues, provide symptom → root cause → fix → preventive guardrail.

#### Interview Questions
For each question:

**Q:** <question>

**L4 answer** — correct, complete, bounded; demonstrates working knowledge and edges.

**L5 answer** — adds the underlying mechanism, chosen tradeoff, scale break, and context-specific alternative.

Aim for 4–8 questions per subsection.

#### L5-Only Questions
Include depth, scale, ambiguity, and design-ownership questions not appropriate for L4, each with a full L5 answer. Aim for 2–4 per subsection.
```

## Writing rules

- Write tersely and technically. Remove filler and heading restatements.
- Use Java 17 for code unless the topic requires another language.
- Prefer runnable minimal code over pseudocode.
- Prefer a table over three paragraphs.
- Bold a term only on first definition.

## Self-check

Fix every failed check before writing a file:

1. Does every property claim state its defeater?
2. Is every number sourced or explicitly hedged?
3. Is every production issue cited or labeled canonical?
4. Does every best practice name the failure it prevents?
5. Does every L5 answer add a structural signal beyond the L4 answer?
6. Could a principal engineer call any paragraph hand-wavy?
