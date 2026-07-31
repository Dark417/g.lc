# Round Mechanics — the 45-Minute Clock

## Why the budget is tight

A 45-minute round often leaves roughly 38 minutes of design after introductions and candidate questions. The common failure is reaching the deep dive too late to discuss failures. Time discipline is itself a scored behavior.

## Phase budgets

| Phase | Clock | Hard stop | Done means |
|---|---|---|---|
| Requirements & scope | 0:00–0:05 | 0:07 | 3–5 functional bullets, numbered non-functionals, explicit non-goals |
| Estimation & API | 0:05–0:10 | 0:12 | QPS/storage tied to decisions; 3–6 endpoints |
| High-level design | 0:10–0:22 | 0:25 | Diagram, one end-to-end request, data model with keys |
| Deep dive | 0:22–0:37 | 0:39 | One component at mechanism depth with a concrete walkthrough |
| Failure & wrap | 0:37–0:45 | — | Failure table, first 10× bottleneck, four-sentence recap |

If a phase overruns, cut scope out loud rather than silently rushing.

## Signal by phase

### Requirements

Bound the problem, turn adjectives into numbers, and name non-goals. Ask two or three questions, then propose assumptions and confirm them.

### Estimation

Round aggressively and state the consequence: “400 write QPS means a single primary is fine; no sharding in v1.”

### High-level design

Trace one request through the system and name partition keys plus the cheap and expensive access patterns. A narrated noun list is not a design.

### Deep dive

Choose the component where the hard problem lives. Cover the algorithm/data structure, concurrency, consistency, and exact failure.

### Failure and wrap

Volunteer blast radius, degraded mode, weakest assumption, and first bottleneck at 10×.

## Recovery moves

| Situation | Move |
|---|---|
| Behind at 0:25 | Announce a cut and move directly to the deep dive |
| Interviewer interrupts | Follow the probe; it is now the round |
| Mechanism is unfamiliar | Say so, reason from first principles, and state what to verify |
| Core choice is rejected | Ask which constraint changed and re-derive |
| Silence follows | Volunteer the weakest assumption |

## Panel and remote variations

- With two interviewers, expect one to drive and one to attack.
- In a shared document, use a pre-planned ASCII layout because typing is slower than drawing.
- Amazon rounds may splice behavioral ownership probes into the design discussion.
