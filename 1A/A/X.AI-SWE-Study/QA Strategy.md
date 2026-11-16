# QA Strategy

> How a lead or principal quality engineer plans, designs for, runs, and signs off testing, and makes the green, yellow, or red call.

## Index
- [1. Core Idea](#1-core-idea)
- [2. Risk Model](#2-risk-model)
- [3. Design For Testability](#3-design-for-testability)
- [4. Test Layers](#4-test-layers)
- [5. Test Design Techniques](#5-test-design-techniques)
- [6. Running Tests In The Pipeline](#6-running-tests-in-the-pipeline)
- [7. Exit Criteria And The Call](#7-exit-criteria-and-the-call)
- [8. Scenarios](#8-scenarios)
- [9. Testing AI And LLM Systems](#9-testing-ai-and-llm-systems)
- [10. Metrics And Reporting](#10-metrics-and-reporting)
- [11. The Lead's Operating Model](#11-the-leads-operating-model)
- [Where This Fits](#where-this-fits)
- [References](#references)

---

## 1. Core Idea

You cannot test everything, so you test by risk and make the remaining risk visible.

- **Testing fully is impossible.** Input space is effectively infinite.
  - "Full" means: every high risk has a test, and every gap is a known, accepted risk.
- **Quality is built in, not tested in.**
  - Testing measures quality. Design and code create it.
- **The QE's two outputs:**
  1. Evidence: what was tested, how, with what result.
  2. A call: green, yellow, or red, with reasons.
- **Who decides to ship:** the QE recommends. The product or engineering owner accepts the risk.
  - The QE never hides risk to get a green. That is the job's integrity.
- 🗣 "I don't promise zero bugs. I promise that every known risk is tested or consciously accepted."

---

## 2. Risk Model

Test the things that hurt most and fail most often first.

- **Risk = impact × likelihood.**
  - Impact: money, data, safety, legal, users affected.
  - Likelihood: new code, complex logic, many changes, past bugs, weak ownership.
- **Quality attributes to cover** (ISO 25010 style):
  - Functional correctness, performance, reliability, security.
  - Usability and accessibility, compatibility, maintainability, recoverability.

| Risk level | Example | Test depth |
|---|---|---|
| Critical | Payments, auth, data migration, PII | All layers + negative + perf + security + rollback rehearsal |
| High | Core user flows, integrations | Unit + contract + integration + E2E happy and key sad paths |
| Medium | Secondary features | Unit + integration, E2E smoke |
| Low | Cosmetic, internal admin | Unit + exploratory pass |

- Write a **risk register** at design time: risk, impact, likelihood, test that covers it, owner.
- ⚠️ Untested critical risk is the most common hidden red.

---

## 3. Design For Testability

Testable systems are designed that way. Get into the design review, not just the test phase.

- **Seams:** every external dependency behind an interface.
  - Hexagonal style: ports and adapters. Swap a fake adapter in tests.
- **Dependency injection:** pass collaborators in. No hidden `new` of a DB client inside logic.
- **Control nondeterminism:** inject the clock, random seed, and ID generator.
- **Pure core, thin shell:** business logic as pure functions; I/O at the edges.
- **Idempotent operations:** safe to retry, so tests can rerun safely.
- **Contract-first APIs:** OpenAPI or schema first, so consumer and provider test independently.
- **Observability hooks:** structured logs, trace IDs, metrics. Tests and on-call share them.
- **Feature flags:** ship dark, test in prod for a small slice, roll back without deploy.
- **Test data:** builders and factories, not shared mutable fixtures.
- **Environment parity:** containers for real DBs and queues (Testcontainers), not in-memory fakes for critical paths.

```java
// Testable: clock is injected, so tests can fix "now"
class TokenService {
  private final Clock clock;
  TokenService(Clock clock) { this.clock = clock; }
  boolean expired(Instant exp) { return clock.instant().isAfter(exp); }
}
```

- Design review checklist question: "How will we test this, and how will we know it broke in prod?"

---

## 4. Test Layers

Each layer proves something different. Use the cheapest layer that proves it.

| Layer | Proves | Java / Python tools | Speed |
|---|---|---|---|
| Unit | Logic is correct in isolation | JUnit 5, Mockito / pytest | ms |
| Component | One service works with fakes at its edges | Spring Boot test slices / pytest + fakes | seconds |
| Contract | Consumer and provider agree on the API | Pact, schema tests | seconds |
| Integration | Real DB, queue, cache work together | Testcontainers, LocalStack | seconds–minutes |
| End-to-end | Key user journeys work across the system | Playwright, REST Assured | minutes |

- Ratio: many unit, fewer integration, few E2E (the test pyramid).
  - ⚠️ Inverting it gives slow, flaky suites nobody trusts.

| Non-functional | Proves | Tools |
|---|---|---|
| Performance and load | Meets latency and throughput SLOs | Gatling, k6, JMeter |
| Resilience | Survives dependency failures | Chaos tests, fault injection, Toxiproxy |
| Security | No known vulnerabilities, authz holds | SAST, dependency scan, OWASP ZAP |
| Data quality | Pipelines produce correct, complete data | Great Expectations, dbt tests, row counts |
| Migration and rollback | Upgrade and rollback both work | Rehearsal on a prod-like copy |

---

## 5. Test Design Techniques

Good test cases come from techniques, not from guessing.

- **Equivalence partitioning:** one test per class of input that behaves the same.
- **Boundary values:** test at, just below, and just above each limit.
  - Example: limit 100 → test 99, 100, 101, 0, negative.
- **Decision tables:** one row per combination of business rules.
- **State transitions:** every valid and invalid move between states.
  - Example: order created → paid → shipped. Try shipped → paid.
- **Pairwise:** cover every pair of options instead of every combination.
- **Property-based:** state a rule ("decode(encode(x)) == x"), let the tool generate inputs.
  - jqwik for Java, Hypothesis for Python.
- **Negative and abuse cases:** bad input, wrong user, replayed request, huge payload.
- **Exploratory testing:** time-boxed sessions with a charter, e.g. "break checkout with slow network".
- **Mutation testing:** change the code on purpose; good tests should fail.
  - Shows test strength. Line coverage only shows what ran.

---

## 6. Running Tests In The Pipeline

Fast feedback early, deep checks later, real signals in production.

```text
commit -> PR checks -> merge -> staging -> canary -> full prod
          unit,lint    integ    E2E,perf   SLO watch  monitors
```

- Notice: each stage is slower and closer to reality than the one before.

| Stage | Runs | Time budget | Blocks on fail |
|---|---|---|---|
| Pre-merge | Unit, static analysis, contract, security scan | < 10 min | Yes |
| Post-merge | Integration with Testcontainers | < 30 min | Yes |
| Staging | E2E smoke, perf baseline, migration rehearsal | < 1 h | Yes for critical |
| Canary | Real traffic on 1–5%, SLO comparison | 30 min – hours | Auto-rollback |
| Production | Synthetic monitors, alerts, error budgets | Always on | Pages on-call |

- **Flaky test policy:**
  - Quarantine within a day. Fix or delete within a week.
  - A flaky suite trains people to ignore red. That is worse than no test.
- **Test data and environments:** reset per run, no shared state between tests.

---

## 7. Exit Criteria And The Call

Agree on what green means before testing starts, not after.

- **Severity definitions** (agree these with product):
  - **Sev1:** data loss, security hole, critical path down, no workaround.
  - **Sev2:** major feature broken, workaround is hard.
  - **Sev3:** minor feature broken, easy workaround.
  - **Sev4:** cosmetic.

| Call | Meaning | Typical criteria |
|---|---|---|
| Green | Ship | All must-pass tests pass. No open Sev1/Sev2. SLOs met. Every critical risk tested |
| Yellow | Ship with conditions | Known issues have workaround or mitigation. Owner signs off. Fix date set. Often limited rollout |
| Red | Do not ship | Open Sev1. Data, security, or legal risk. Untested critical path. Rollback not proven |

- **Yellow is not a soft green.** It must name:
  1. Each open issue and its user impact.
  2. The mitigation: flag off, limited rollout, monitoring, support script.
  3. The risk owner who accepted it, in writing.
  4. The fix date.
- **Partial calls:** rate each feature or component separately.
  - Ship the green parts. Keep red parts behind a flag that is off.
- **The call can change:** green at staging can turn red in canary. Watch the SLOs.
- 🗣 "Green means tested. Yellow means known and owned. Red means unknown or unacceptable."

---

## 8. Scenarios

Real situations and the call a lead would make.

| Scenario | Call | Why |
|---|---|---|
| All tests pass, p99 latency 10% over SLO | Yellow | Canary with SLO watch, fix date. Red if over by far or on payments |
| Sev2 bug in an internal admin page, workaround exists | Yellow | Low exposure. Document workaround, fix next sprint |
| Irreversible data migration, rollback never rehearsed | Red | One-way door. Rehearse rollback on a prod copy first |
| High-severity CVE in a dependency, code path reachable | Red | Patch or mitigate first. Not reachable: Yellow with ticket |
| 80% of feature tested, untested part behind flag off | Green (partial) | Shipped scope is fully tested. Flag stays off until tested |
| Hotfix for a live incident | Green with conditions | Targeted tests on the fix + regression smoke + canary |

| Scenario | Call | Why |
|---|---|---|
| E2E test fails intermittently | Yellow or Red | Yellow if a test bug is proven. Red if a product race is suspected |
| Third-party sandbox is down, cannot run integration | Yellow | Contract tests pass. Add prod synthetic check after release |
| New feature, no perf test, expected low traffic | Yellow | Accept with monitoring and a rollback flag |
| Accessibility failures on a public form | Yellow or Red | Red if legal exposure applies to your product |
| LLM feature eval score drops 2 points | Depends | Red if outside the confidence interval and below threshold. Else Yellow, rerun |
| Release deadline, testing incomplete on critical path | Red | Offer options: cut scope, flag off, or slip the date |

- The pattern: **reversibility and blast radius** drive the call more than bug count.

---

## 9. Testing AI And LLM Systems

Same principles, but outputs vary and "correct" is fuzzy.

- **What changes:**
  - Nondeterminism: same input, different output. Test distributions, not single runs.
  - No exact assertions: grade outputs with rubrics, schemas, and judges.
  - The model can change under you: a provider update is a release.
- **Layers for AI:**
  - Deterministic parts (parsing, tools, retrieval filters) get normal unit tests.
  - Structured output: validate against schema every time.
  - Golden set evals: versioned cases with expected outcomes.
  - LLM-as-judge: calibrate against human labels before trusting it.
  - Agent trajectory: did it pick the right tools, in a sane order, within budget?
  - Red-teaming: prompt injection, jailbreaks, data leakage through retrieval.
  - Side effects: run tools in a sandbox. Never test writes against prod.
- **The call for AI:**
  - Green: eval scores at or above threshold, inside the confidence interval.
  - Yellow: small regression on a low-risk slice, with online monitoring.
  - Red: safety or leakage failure, or regression on a high-risk slice.
- Depth lives in `AI Engineering Syllabus` §F and `AI Principal Deep Dive` §2.14.

---

## 10. Metrics And Reporting

Measure whether testing catches problems before users do.

| Metric | What it tells you | Watch out |
|---|---|---|
| Escaped defects | Bugs found in prod per release | The truest quality signal |
| Change failure rate | Deploys causing incidents (DORA) | Pairs with deploy frequency |
| Time to restore | How fast you recover (DORA) | Rollback speed matters here |
| Flaky test rate | Suite trustworthiness | Above ~1–2% erodes trust (order of magnitude) |
| Mutation score | Test strength | Expensive; run on critical modules |

- **Code coverage is a signal, not a target.**
  - Low coverage proves gaps. High coverage does not prove quality.
- **The test report (one page):**
  1. The call: green, yellow, or red.
  2. Scope tested and not tested.
  3. Open issues by severity, with owner and date.
  4. Risks accepted, and by whom.
  5. Metrics vs last release.

---

## 11. The Lead's Operating Model

A lead QE builds a system where the team owns quality, not a gate at the end.

- **Shift left:** join design reviews. Write the test strategy with the design doc.
- **Shift right:** canaries, monitors, and error budgets are tests too.
- **Whole-team quality:** developers write unit and integration tests. QE owns strategy, tooling, and hard cases.
- **Test strategy doc per product:** risks, layers, tools, exit criteria, owners.
- **Every incident adds a test:** the postmortem's first action item.
- **Paved road:** shared test frameworks, fixtures, and pipeline templates.
- **Coach, don't police:** teach test design in reviews.
- 🗣 "My success metric is escaped defects going down while release speed goes up."

---

## Where This Fits

- For interviews: testing questions show up in fundamentals and behavioral rounds (the FINRA gap).
- For PAA: pillar 5 (quality and evaluation) is this doc applied to AI systems.
- Time it deserves: one read now. Revisit when you write your first design doc in a new role.
- I should be able to:
  - Explain the risk model and test layers in two minutes.
  - Make a green, yellow, or red call on any section 8 scenario, with reasons.
  - Show one design-for-testability change in my own code.

## References

- [testcontainers-java (GitHub)](https://github.com/testcontainers/testcontainers-java)
- [Pact docs: contract testing](https://docs.pact.io/)
- [Martin Fowler: The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Google SRE Book: Testing for Reliability](https://sre.google/sre-book/testing-reliability/)
- [DORA: software delivery metrics](https://dora.dev/)
