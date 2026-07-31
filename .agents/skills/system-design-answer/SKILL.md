---
name: system-design-answer
description: Generate complete, defensible system design interview answers structured as a real 45-minute round, with distinct L4 target-hire and L5 senior-stretch answers plus interviewer pushback. Use when the user asks for a system design answer, “design X” interview walkthrough, SD preparation, level comparison, or review/grading of their own system design draft.
---

# System Design Answer

Produce a timed round transcript, not a polished architecture document. Show what to say, in what order, under 45 minutes of pressure.

## Workflow

1. Identify the exact interviewer prompt. If ambiguous, state one reasonable framing and proceed without blocking.
2. Read the repository's `1sd/build.md`; it is the mandatory generation contract. Respect its cold-attempt gate and default to a skeleton when a full artifact is not authorized.
3. Read `1sd/0flow.md` for the current phase order, communication moves, and answer-defense guidance.
4. Read [round-mechanics.md](references/round-mechanics.md) for compact phase budgets and recovery moves.
5. Read [level-calibration.md](references/level-calibration.md) every time. L5 must differ structurally, not merely in length.
6. Read [building-blocks.md](references/building-blocks.md) when capacity, storage, or component tradeoffs matter.
7. Locate the canonical packet through `1sd/1index.md`; do not create a duplicate in another domain.
8. Write one Markdown file named `<question-slug>-45min.md` only after a cold attempt. Otherwise create or improve the canonical one-page skeleton.
9. Run the self-check before delivery.

## Required output structure

```markdown
# <Question as the interviewer would ask it>

**Framing assumed:** <scope decision and reason>
**Round shape:** 45 min · <interviewer/panel> · <whiteboard/shared doc>

| Phase | Clock | Goal | Fail mode if overrun |
|---|---|---|---|
| Requirements & scope | 0:00–0:05 | ... | ... |
| Estimation & API | 0:05–0:10 | ... | ... |
| High-level design | 0:10–0:22 | ... | ... |
| Deep dive | 0:22–0:37 | ... | ... |
| Failure, bottlenecks, wrap | 0:37–0:45 | ... | ... |

# PART A — L4 Answer

## 0:00–0:05 · Requirements & Scope
**Say this:** <verbatim script>
**Land on:** functional requirements, numbered non-functionals, explicit non-goals.

## 0:05–0:10 · Estimation & API
Show arithmetic and state the decision each estimate forces.
Give 3–6 exact endpoints with idempotency and pagination.

## 0:10–0:22 · High-Level Design
Draw before prose. Trace one request end-to-end.
Include components, chosen mechanism, rejected alternative, and keyed data model.

## 0:22–0:37 · Deep Dive
Name why this component is the hard part.
Cover algorithm/data structure, concurrency, consistency, concrete values, and exact failure.

## 0:37–0:45 · Failure, Bottlenecks, Wrap
Include `Failure | Blast radius | Detection | Degraded behavior | Mitigation`.
Name the first 10× bottleneck and give a four-sentence recap.

## L4 signal check
## Pushbacks this answer invites

# PART B — L5 Answer

Rewrite all five phases. Do not copy and pad Part A.

The L5 answer must:
- negotiate scope and name what a cut buys;
- rank non-functional priorities and design to that order;
- let a number force a choice;
- name a rejected alternative and flip condition;
- volunteer degradation, rollout, migration, cost, and blast radius;
- identify its weakest assumption before the interviewer does.

## Delta table — what actually changed
| Phase | L4 did | L5 did | Separating signal |
|---|---|---|---|

## Pushback ladder
↳ P1 mechanism → response
↳ P2 scale/failure → response
↳ P3 premise reversal → what bends and what is replaced

## Over-reach warnings
Name the exact sentence likely to over-engineer the problem.

# Shared Reference

Include numbers with arithmetic/source, precise vocabulary, Amazon-vs-Google emphasis, and 2–5 primary references.
```

## Defensibility rules

- Write verbatim scripts for requirements and wrap.
- Attach a number to every non-functional requirement.
- Make every estimate change a decision or remove it.
- Pair every named service with the mechanism bought and cost paid.
- State every property’s defeater.
- Cite public incidents or label a canonical pattern; never invent a war story.
- Mark uncertainty with `> ⚠️ Low confidence:`.
- Draw the high-level diagram before explanatory prose.
- Use Java 17 only when code clarifies what prose cannot.

## Self-check

Fix every “no” before delivery:

1. Do phase budgets total 45 minutes?
2. Does every non-functional requirement have a number?
3. Does every estimate force a decision?
4. Is L5 structurally different from L4?
5. Does the delta table avoid “more detail” as the signal?
6. Does P3 reverse a premise?
7. Does each technology include its mechanism and cost?
8. Is every number sourced or derived?
9. Is there a specific over-reach warning?
10. Could a principal engineer call any paragraph hand-wavy?
